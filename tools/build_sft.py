"""build_sft.py — Day 4: SFT 数据构建（chat 模板 + assistant-only mask + 预训练混入）

输入：data/raw/minimind_dataset/sft_t2t_mini.jsonl（905,718 条 conversations，jsonl）
模板：`<|im_start|>{role}\n{content}<|im_end|>\n`（minimind 原格式；本仓 tokenizer specials = 1/2）
输出：`data/sft-mix/{train,val}.bin`（uint16 输入 id）+ `{train,val}.labels.bin`（int16，-100 = 不算 loss）
      + `meta.json` + `SHA256SUMS`

关键设计：
  1) **会话不跨块**：平均 268 token/会话，按 1024 定长块打包；装不下就补 EOS(0) 收块再起新块
     （块内填充约 13%，但每条对话的模板/边界完整；比"一会话一样本 + padding"仍省 ~60% 算力）。
  2) **assistant-only mask**：每轮 assistant 只训"正文 + 结尾 im_end"——mask 覆盖
     [header 末 token, 正文末 token]（label 右移后恰好训练 content[0]…im_end）；
     user/system 段与跨会话边界全部 -100。
  3) **预训练混入**：按块固定节奏（ratio=0.25 → 每 4 块 1 块）从 data/shards 抽随机窗口，
     mask 全 1（正常 LM 目标）——PLAN 风险表要求混 20~30% 防 SFT 后幻觉加重。

用法（仓库根目录；CPU only，可与主训练并行）：
  .venv-pre/bin/python -I tools/build_sft.py --max-tokens 250e6 --pretrain-ratio 0.25 2>&1 | tee logs/day4-sft-build.log
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np
from tokenizers import Tokenizer

IM_START, IM_END, EOS = 1, 2, 0


def fmt_ratio(s: str) -> float:
    return float(s[:-1]) / 100 if s.endswith("%") else float(s)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class PretrainSource:
    """从 data/shards 抽随机窗口（预训练混入用）。"""

    def __init__(self, data_dir: Path, block_size: int, seed: int):
        meta = json.loads((data_dir / "meta.json").read_text(encoding="utf-8"))
        names = [s["name"] for s in meta["shards"]] if "shards" in meta else ["train.bin"]
        self.arrays = [np.memmap(data_dir / n, dtype=np.uint16, mode="r") for n in names]
        self.lens = np.asarray([len(a) for a in self.arrays], dtype=np.float64)
        self.probs = self.lens / self.lens.sum()
        self.block = block_size
        self.rng = np.random.default_rng(seed)

    def next_block(self) -> list[int]:
        si = int(self.rng.choice(len(self.arrays), p=self.probs))
        a = self.arrays[si]
        off = int(self.rng.integers(0, len(a) - self.block - 2))
        return a[off:off + self.block].tolist()


class BlockWriter:
    """定长块写入器：token(uint16) + label(int16) 双文件；块尾 label=-100（跨块不预测）。"""

    def __init__(self, tok_path: Path, lbl_path: Path, block_size: int,
                 pretrain: PretrainSource | None = None, every: int = 0):
        self.block = block_size
        self.tok_f = tok_path.open("wb")
        self.lbl_f = lbl_path.open("wb")
        self.pre = pretrain
        self.every = every
        self.cur_t: list[int] = []
        self.cur_m: list[int] = []
        self.blocks = 0
        self.tokens = 0
        self.supervised = 0

    # ---- 内部 ----
    def _flush(self) -> None:
        assert len(self.cur_t) == self.block
        t = np.asarray(self.cur_t, dtype=np.uint16)
        m = np.asarray(self.cur_m, dtype=np.int16)
        lab = np.full(self.block, -100, dtype=np.int16)
        nxt = m[:-1] == 1
        lab[:-1][nxt] = t[1:][nxt]
        self.tok_f.write(t.tobytes())
        self.lbl_f.write(lab.tobytes())
        self.blocks += 1
        self.tokens += self.block
        self.supervised += int((m == 1).sum())
        self.cur_t, self.cur_m = [], []

    def _pad_flush(self) -> None:
        pad = self.block - len(self.cur_t)
        if pad:
            self.cur_t += [EOS] * pad
            self.cur_m += [0] * pad
        self._flush()

    def _maybe_pretrain(self) -> None:
        """当前块序号命中预训练节奏时，直接写一个完整预训练块。"""
        if self.every and self.pre is not None and self.blocks % self.every == 0:
            self.cur_t = self.pre.next_block()
            self.cur_m = [1] * self.block
            self._flush()

    # ---- 外部 ----
    def add_conversation(self, ids: list[int], mask: list[int]) -> None:
        assert len(ids) == len(mask) and len(ids) <= self.block
        if not self.cur_t:
            self._maybe_pretrain()
        if len(self.cur_t) + len(ids) > self.block:
            self._pad_flush()
            self._maybe_pretrain()
        self.cur_t.extend(ids)
        self.cur_m.extend(mask)

    def close(self) -> None:
        if self.cur_t:
            self._pad_flush()
        self.tok_f.close()
        self.lbl_f.close()


def conversation_segments(tok: Tokenizer, convs: list[dict], roles_head: dict, end_ids: list[int]):
    """返回 (ids, mask, n_assistant)：assistant 段头末 token + 正文参与训练。"""
    ids: list[int] = []
    mask: list[int] = []
    n_assistant = 0
    for m in convs:
        role = m.get("role", "user")
        content = (m.get("content") or "").strip()
        if role not in roles_head:  # 未知角色（如 tool）按需补表
            roles_head[role] = tok.encode(f"<|im_start|>{role}\n", add_special_tokens=False).ids
        head = roles_head[role]
        body = tok.encode(content, add_special_tokens=False).ids if content else []
        ids.extend(head)
        mask.extend([0] * len(head))
        if role == "assistant" and body:
            mask[-1] = 1                     # header 末 token（"\n"）预测首个正文 token
            ids.extend(body)
            mask.extend([1] * len(body))
        else:
            ids.extend(body)
            mask.extend([0] * len(body))
        ids.extend(end_ids)
        mask.extend([0] * len(end_ids))
        if role == "assistant" and body:
            n_assistant += 1
    return ids, mask, n_assistant


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sft-jsonl", default="data/raw/minimind_dataset/sft_t2t_mini.jsonl")
    ap.add_argument("--shards-dir", default="data/shards")
    ap.add_argument("--out-dir", default="data/sft-mix")
    ap.add_argument("--tokenizer", default="data/tokenizer-32k/tokenizer.json")
    ap.add_argument("--block-size", type=int, default=1024)
    ap.add_argument("--max-tokens", type=float, default=250e6, help="训练集总 token（含预训练混入）")
    ap.add_argument("--val-tokens", type=float, default=2e6)
    ap.add_argument("--pretrain-ratio", type=fmt_ratio, default=0.25)
    ap.add_argument("--val-mod", type=int, default=100, help="blake2b64(line) %% val-mod == 0 → val")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    tok = Tokenizer.from_file(args.tokenizer)
    roles_head = {r: tok.encode(f"<|im_start|>{r}\n", add_special_tokens=False).ids
                  for r in ("user", "assistant", "system")}
    end_ids = tok.encode("<|im_end|>\n", add_special_tokens=False).ids
    assert roles_head["assistant"][0] == IM_START and end_ids[0] == IM_END, "special 编码异常"

    pre = PretrainSource(Path(args.shards_dir), args.block_size, args.seed)
    every = max(1, round(1 / args.pretrain_ratio)) if args.pretrain_ratio > 0 else 0
    train = BlockWriter(out / "train.bin", out / "train.labels.bin", args.block_size, pre, every)
    val = BlockWriter(out / "val.bin", out / "val.labels.bin", args.block_size)

    t0 = time.time()
    n_read, n_train_conv, n_val_conv, skipped_long, sample_checks = 0, 0, 0, 0, 0
    with open(args.sft_jsonl, encoding="utf-8") as f:
        for line in f:
            if train.tokens >= args.max_tokens and val.tokens >= args.val_tokens:
                break
            n_read += 1
            h = int.from_bytes(hashlib.blake2b(line.encode(), digest_size=8).digest(), "little")
            is_val = (h % args.val_mod == 0)
            rec = json.loads(line)
            ids, mask, n_asst = conversation_segments(tok, rec.get("conversations") or [],
                                                      roles_head, end_ids)
            if n_asst == 0 or not ids:
                continue
            if len(ids) > args.block_size:      # 本数据集 max 742，实际不触发
                skipped_long += 1
                ids, mask = ids[:args.block_size], mask[:args.block_size]
            # 抽样自检：分段编码 vs 整段编码（确认 ByteLevel 边界无合并差异）
            if sample_checks < 30 and n_read % 7919 == 0:
                text = "".join(f"<|im_start|>{m.get('role', 'user')}\n{(m.get('content') or '').strip()}"
                               f"<|im_end|>\n" for m in (rec.get("conversations") or []))
                assert tok.decode(ids, skip_special_tokens=False) == text, "分段编码与整段不一致"
                sample_checks += 1
            if is_val:
                if val.tokens < args.val_tokens:
                    val.add_conversation(ids, mask)
                    n_val_conv += 1
            elif train.tokens < args.max_tokens:
                train.add_conversation(ids, mask)
                n_train_conv += 1
            if n_read % 100000 == 0:
                print(f"[{n_read:>7,}] train={train.tokens/1e6:.1f}M val={val.tokens/1e6:.2f}M "
                      f"({(time.time()-t0)/60:.1f} min)", flush=True)

    train.close()
    val.close()

    meta = {
        "source": args.sft_jsonl,
        "template": "<|im_start|>{role}\\n{content}<|im_end|>\\n",
        "specials": {"endoftext": 0, "im_start": 1, "im_end": 2},
        "block_size": args.block_size,
        "train": {"tokens": train.tokens, "blocks": train.blocks,
                  "supervised_tokens": train.supervised,
                  "supervised_ratio": round(train.supervised / max(train.tokens, 1), 4),
                  "conversations": n_train_conv},
        "val": {"tokens": val.tokens, "blocks": val.blocks, "conversations": n_val_conv,
                "supervised_ratio": round(val.supervised / max(val.tokens, 1), 4)},
        "pretrain_mix": {"ratio_blocks": args.pretrain_ratio, "every_n_blocks": every,
                         "source": args.shards_dir},
        "val_split": f"blake2b64(line) % {args.val_mod} == 0（文档级）",
        "skipped_long": skipped_long,
        "sample_checks": sample_checks,
        "elapsed_s": round(time.time() - t0, 1),
        "created": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [f"{sha256_file(out / name)}  {name}"
             for name in ("train.bin", "train.labels.bin", "val.bin", "val.labels.bin")]
    (out / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("[done] " + json.dumps({"train": meta["train"], "val_tokens": meta["val"]["tokens"]},
                                 ensure_ascii=False), flush=True)
    print(f"[done] 落位 {out}/（SHA256SUMS 4 条）· {(time.time()-t0)/60:.1f} min", flush=True)


if __name__ == "__main__":
    main()