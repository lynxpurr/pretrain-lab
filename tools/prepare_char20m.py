"""prepare_char20m.py — Day 1 字符级最小闭环的数据准备（D-06 语料的切片复用）

从 minimind pretrain_t2t.jsonl（中文主力语料，Day 0 已预下载、指纹在 data/raw/SHA256SUMS）流式切片：
  1. 抽取 "text" 字段，文档级切分：头部若干行作 val（不与 train 共享文档，避免泄漏）
  2. 统计字符频率 → 字符词表（specials：<unk>=0 <bos>=1 <eos>=2 <pad>=3，其后按频次排）
  3. 编码为 uint16 原始文件 train.bin / val.bin（memmap 友好，nanoGPT 式）+ meta.json
Day 1 有意保持"简陋"：不做去重/清洗/混配比——那是 Day 2 BPE + memmap 流水线的正戏。
用法：仓库根目录运行 `.venv-pre/bin/python -I tools/prepare_char20m.py`（-I 隔离模式，纯 stdlib+numpy）。
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="data/raw/minimind_dataset/pretrain_t2t.jsonl")
    ap.add_argument("--out", default="data/day1-char20m")
    ap.add_argument("--train-chars", type=int, default=300_000_000, help="训练文本字符预算")
    ap.add_argument("--val-chars", type=int, default=3_000_000, help="验证文本字符预算")
    ap.add_argument("--vocab-cap", type=int, default=16000, help="词表上限（含 4 个 specials）")
    ap.add_argument("--min-freq", type=int, default=5, help="字符入表最低频次")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    # ---- 1. 流式抽取（8.28GB 文件不整载内存，够预算即停） ----
    val_parts: list[str] = []
    train_parts: list[str] = []
    got_val = got_train = 0
    n_lines = 0
    with open(args.src, encoding="utf-8") as f:
        for line in f:
            n_lines += 1
            try:
                text = json.loads(line).get("text", "")
            except json.JSONDecodeError:
                continue
            if not text:
                continue
            if got_val < args.val_chars:  # 文档级切分：边界文档只进 val，不跨集合
                take = min(args.val_chars - got_val, len(text))
                val_parts.append(text[:take])
                got_val += take
            elif got_train < args.train_chars:
                take = min(args.train_chars - got_train, len(text))
                train_parts.append(text[:take])
                got_train += take
            else:
                break
    train_text = "\n".join(train_parts)
    val_text = "\n".join(val_parts)

    # ---- 2. 字符词表 ----
    counter = Counter(train_text)
    itos = ["<unk>", "<bos>", "<eos>", "<pad>"]
    for ch, cnt in counter.most_common():
        if len(itos) >= args.vocab_cap or cnt < args.min_freq:
            break
        itos.append(ch)
    stoi = {s: i for i, s in enumerate(itos)}
    unk = stoi["<unk>"]
    total_freq = sum(counter.values())
    covered = sum(cnt for ch, cnt in counter.items() if ch in stoi)
    coverage = covered / total_freq

    # ---- 3. 编码（translate 一次成表：C 速度完成 300M 字符的查表，快于逐字符 Python 循环） ----
    # 坑（2026-11-18 实证）：translate 对"不在表内的字符"原样放行——val 取自语料头部，
    # 含 train 未出现的字符，穿透后码点 >65535 被 uint16 截断成垃圾 id。故表须覆盖
    # set(train)|set(val)，并在 encode 内断言 id 上限作防线。
    table = str.maketrans(
        {ord(c): chr(stoi.get(c, unk)) for c in set(train_text) | set(val_text)}
    )

    def encode(s: str) -> np.ndarray:
        ids = np.frombuffer(
            s.translate(table).encode("utf-32-le"), dtype=np.dtype("<u4")
        ).astype(np.uint16)
        assert ids.max() < len(itos), f"编码越界 id {int(ids.max())} ≥ vocab {len(itos)}"
        return ids

    train_ids = encode(train_text)
    val_ids = encode(val_text)
    (out / "train.bin").write_bytes(train_ids.tobytes())
    (out / "val.bin").write_bytes(val_ids.tobytes())

    meta = {
        "src": args.src,
        "src_sha256_prefix": "31efc9a6fa743076",  # data/raw/SHA256SUMS 中的指纹前缀
        "vocab_size": len(itos),
        "itos": itos,
        "stoi": stoi,
        "stats": {
            "n_lines_read": n_lines,
            "train_chars": len(train_text),
            "val_chars": len(val_text),
            "unique_chars": len(counter),
            "coverage_of_train": round(coverage, 6),
            "train_bin_mb": round((out / "train.bin").stat().st_size / 2**20, 1),
            "val_bin_mb": round((out / "val.bin").stat().st_size / 2**20, 1),
        },
    }
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")

    # ---- 证据输出 ----
    top20 = "".join(ch for ch, _ in counter.most_common(20)).replace("\n", "\\n")
    print(f"[prepare] 读入 {n_lines} 行 → train {len(train_text):,} chars / val {len(val_text):,} chars")
    print(f"[prepare] 唯一字符 {len(counter):,} → 词表 {len(itos)}（覆盖率 {coverage:.4%}）")
    print(f"[prepare] 高频前 20：{top20}")
    print(f"[prepare] 落位 {out}/train.bin {meta['stats']['train_bin_mb']}MB · "
          f"val.bin {meta['stats']['val_bin_mb']}MB · meta.json")


if __name__ == "__main__":
    main()
