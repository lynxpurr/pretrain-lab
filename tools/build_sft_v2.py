"""build_sft_v2.py — Day 7: SFT 数据 v2（数据侧修正版）

相对 v1（tools/build_sft.py）只改**样本采样**，不改 tokenizer / 模板 / 预训练混入 / block / val 切分：
  1) **校准/拒答**：v1 数据里真正的"承认不知道/纠正错误前提"样本极少（assistant 侧直接承认仅 3,786 条，
     且多为长推理里的"无法确定"）→ 注入 tools/gen_sft_v2_extra.py 生成的 calibration 样本
     （未来事件 / 错误前提 / 实时信息 / 隐私 / 不可验证 / 已知事实对比），并重复 --calib-repeat 次。
  2) **格式硬约束**：v1 的"只回答"样本仅 46 条 → 注入 format 样本（只回答数字算术 / 一句话 /
     不超过 N 字 / 列出 3 条），重复 --format-repeat 次；同时把主数据里命中的格式约束样本上采样 2×。
  3) **压罗列癖**：assistant 任一段含 ≥5 个编号/项目行 → 按 blake2b64(line)%3==0 保留（≈1/3），
     使列表类会话占比降到 ≤15%（v1 实测 34.2%）。
  4) **正例对冲**：注入 helpful 样本（中英良性问答），对冲 v1 的拒答模板泄漏（en-fluency 失败）。
  5) 其余不变：25% 预训练块（按块节奏）/ assistant-only mask / block 1024 / val 2M 文档级留出。
     **val 直接复用 v1 的 `data/sft-mix/{val.bin,val.labels.bin}`**——v2 因降采样会读得更远，
     若重建 val 会得到不同留出集、破坏 v1/v2 可比性；所有 hash 留出记录在 v2 训练流中一律跳过。

输出：`data/sft-mix-v2/{train,val}.bin` + `{train,val}.labels.bin` + `meta.json` + `SHA256SUMS`
      （新目录，**不动 v1 的 data/sft-mix/**）

用法（仓库根目录，CPU only，可与 GPU 任务并行）：
  .venv-pre/bin/python -I tools/build_sft_v2.py \
      --max-tokens 250e6 --pretrain-ratio 0.25 --calib-repeat 3 --format-repeat 2 2>&1 | tee logs/day7-sft-v2-build.log
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import sys
import time
from pathlib import Path

import numpy as np
from tokenizers import Tokenizer

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_sft import (  # noqa: E402
    EOS, IM_START, BlockWriter, PretrainSource, conversation_segments, fmt_ratio, sha256_file,
)

# ---------------------------------------------------------------- classifiers

# assistant 侧"承认不知道/纠正前提"（取答案前 120 字或短答案，避免把长推理里的"无法确定"全算进来）
CALIB_RE = re.compile(
    r"我不知道|我不确定|我无法确定|我无法回答|我无法提供|我无法获取|我无法预测|我无法知道|"
    r"无法确定|不能确定|尚未公布|尚未发布|尚未确定|尚未发生|尚未举行|尚未产生|尚未揭晓|"
    r"没有官方(?:记录|消息|信息|数据)|没有公开(?:的)?(?:信息|记录|数据)|没有相关(?:信息|记录|资料)|"
    r"缺乏相关(?:信息|资料)|无法得知|无从得知|没有足够(?:的)?(?:信息|资料|数据)|"
    r"这里的前提不对|前提不对|并不举办|没有这项|不存在.*(?:冠军|结果)|"
    r"\b(?:I don't know|I do not know|I'm not sure|I am not sure|cannot determine|can't determine|"
    r"can't provide|cannot provide|not publicly available|no official)\b",
    re.I,
)

# user 侧格式硬约束（长假设句排除：v1 数据里"如果每天只用一句话描述生活"不是格式约束）
FMT_RE = re.compile(
    r"只回答|只需回答|仅回答|只需要回答|"
    r"用一句话(?:解释|概括|总结|说明|回答|描述|介绍)|一句话(?:概括|总结|回答|说明)|"
    r"不超过\s*\d+\s*(?:个)?(?:字|词|条|个)|"
    r"列出\s*(?:三|3|两|2|四|4|五|5)\s*(?:条|个)|"
    r"不要解释|不用解释|无需解释|直接给出(?:答案|结果)|直接回答|"
    r"\b(?:only answer|answer only|in one sentence|one sentence|at most|no more than|"
    r"list (?:three|3|two|2)|briefly|without explanation|just (?:give|answer|list))\b",
    re.I,
)
FMT_HYPOTHETICAL_RE = re.compile(r"如果|假如|你是否想过|有没有想过|会怎样|会如何|是不是可以")

LIST_LINE_RE = re.compile(
    r"^\s*(?:\d{1,2}[.、)）]|[（(]\d{1,2}[)）]|[一二三四五六七八九十]+[、.]|[-*•])\s*\S"
)

# 数学/推理样本：v2 把长数学推理当"列表类"一起砍掉，导致 math-add/math-mul 算术回归；
# v2b 对命中样本**豁免列表降采样**（保留 1×），其余规则不变。
MATH_KW_RE = re.compile(
    r"等于|计算|求值|解方程|方程|面积|周长|速度|路程|距离|概率|乘以|除以|加上|减去|"
    r"加|减|乘|除|数学|几何|代数|函数|证明|推理|逻辑|规律|数列|排列|组合|"
    r"百分|比例|平均|折扣|利润|利率|总价|单价|多少|几[个只条块元人天年月日]"
)
MATH_DIGIT_RE = re.compile(r"\d")
MATH_ASST_RE = re.compile(r"\\times|\\frac|\$\$|=\s*\d")


def texts(rec: dict) -> tuple[str, str]:
    convs = rec.get("conversations") or []
    users, assts = [], []
    for m in convs:
        c = (m.get("content") or "")
        if m.get("role") == "assistant":
            assts.append(c)
        elif m.get("role") == "user":
            users.append(c)
    return "\n".join(users), "\n".join(assts)


def is_calib(rec: dict) -> bool:
    _, a = texts(rec)
    if not a:
        return False
    m = CALIB_RE.search(a)
    if not m:
        return False
    # 只认"答案开头附近"或短答案：长推理中间冒出"无法确定"不算校准样本
    return m.start() <= 120 or len(a) <= 400


def is_fmt(rec: dict) -> bool:
    u, _ = texts(rec)
    if not u or len(u) > 200 or FMT_HYPOTHETICAL_RE.search(u):
        return False
    return bool(FMT_RE.search(u))


def list_items(text: str) -> int:
    return sum(1 for ln in text.splitlines() if LIST_LINE_RE.match(ln))


def is_listy(rec: dict) -> bool:
    convs = rec.get("conversations") or []
    return any(m.get("role") == "assistant" and list_items(m.get("content") or "") >= 5
               for m in convs)


def is_math(rec: dict) -> bool:
    """数学/推理样本（文本启发式）：用户句含数学关键词+数字，或答案含公式/等式。"""
    u, a = texts(rec)
    return bool((MATH_KW_RE.search(u) and MATH_DIGIT_RE.search(u)) or MATH_ASST_RE.search(a))


def keep_for_listy(line: str, keep_den: int = 3) -> bool:
    h = int.from_bytes(hashlib.blake2b(line.encode(), digest_size=8).digest(), "little")
    return h % keep_den == 0


# ---------------------------------------------------------------- mask verifier

def verify_masks(out_dir: Path, block_size: int, roles_head: dict[str, list[int]],
                 n_sample: int = 300, seed: int = 7) -> dict:
    """段级断言：枚举块内每个 im_start…im_end 段，验证 assistant-only mask 恒等式。

    断言（与 Day 4 的验证脚本同款）：
      - user/system 段：段内 label 全 -100；
      - assistant 段：header 末 token 的 label == 首个正文 token（label 右移）；
        正文每个位置 label[i] == token[i+1]；正文末 token 的 label == im_end；
      - 块尾 label == -100；token id < 32000。
    返回统计；任何违规则抛 AssertionError（数据不能进训练）。
    """
    x = np.memmap(out_dir / "train.bin", dtype=np.uint16, mode="r")
    y = np.memmap(out_dir / "train.labels.bin", dtype=np.int16, mode="r")
    assert len(x) == len(y), "tokens/labels 长度不一致"
    n_blocks = len(x) // block_size
    rng = np.random.default_rng(seed)
    offsets = rng.permutation(n_blocks) * block_size
    checked_blocks = checked_segments = 0
    violations: list[str] = []
    for off in offsets:
        if checked_blocks >= n_sample:
            break
        t = x[off:off + block_size].astype(np.int64)
        lab = y[off:off + block_size].astype(np.int64)
        if not (t == IM_START).any():
            # 预训练块：应只有块尾一个 -100（mask 全 1 的包装）
            if int((lab == -100).sum()) != 1 or lab[-1] != -100:
                violations.append(f"pretrain block @{off}: -100 count={int((lab == -100).sum())}")
            continue
        checked_blocks += 1
        # 枚举 im_start 段
        pos = 0
        while True:
            starts = np.flatnonzero(t[pos:] == IM_START)
            if len(starts) == 0:
                break
            s = pos + int(starts[0])
            # 匹配角色 header
            role = None
            for r, h in roles_head.items():
                if s + len(h) <= block_size and t[s:s + len(h)].tolist() == h:
                    role = r
                    break
            ends = np.flatnonzero(t[s + 1:] == 2)  # IM_END
            if len(ends) == 0:
                break
            e = s + 1 + int(ends[0])
            if role is None:
                pos = s + 1
                continue
            checked_segments += 1
            hlen = len(roles_head[role])
            body_start = s + hlen
            if role == "assistant" and body_start < e:
                # header 末 token（"\n"）预测首个正文 token
                if not (s + hlen - 1 < block_size and lab[s + hlen - 1] == t[body_start]):
                    violations.append(f"block@{off} asst header label mismatch at {s}")
                # 正文逐位右移
                body = t[body_start:e]
                nxt = t[body_start + 1:e + 1]
                lab_body = lab[body_start:e]
                if not np.array_equal(lab_body, nxt):
                    bad = np.flatnonzero(lab_body != nxt)[:3]
                    violations.append(f"block@{off} asst body label mismatch at +{bad.tolist()}")
                # 正文末预测 im_end
                if e < block_size and lab[e - 1] != 2:
                    violations.append(f"block@{off} asst tail label != im_end at {e-1}")
            elif role != "assistant":
                if not (lab[s:e + 1] == -100).all():
                    violations.append(f"block@{off} {role} segment has supervised labels at {s}")
            pos = e + 1
        if int(t.max()) >= 32000:
            violations.append(f"block@{off} max_id={int(t.max())}")
        if lab[-1] != -100:
            violations.append(f"block@{off} block tail label != -100")
    if violations:
        raise AssertionError("mask 自检失败：\n" + "\n".join(violations[:20]))
    return {"checked_blocks": checked_blocks, "checked_segments": checked_segments,
            "violations": 0}


# ---------------------------------------------------------------- main

def load_extras(path: Path, repeat: int) -> list[dict]:
    if repeat <= 0 or not path.exists():
        return []
    recs = [json.loads(line) for line in path.open(encoding="utf-8")]
    return recs * repeat


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sft-jsonl", default="data/raw/minimind_dataset/sft_t2t_mini.jsonl")
    ap.add_argument("--extra-dir", default="data/sft-extra-v2")
    ap.add_argument("--shards-dir", default="data/shards")
    ap.add_argument("--out-dir", default="data/sft-mix-v2")
    ap.add_argument("--tokenizer", default="data/tokenizer-32k/tokenizer.json")
    ap.add_argument("--block-size", type=int, default=1024)
    ap.add_argument("--max-tokens", type=float, default=250e6)
    ap.add_argument("--val-from", default="data/sft-mix", help="复用该目录的 val.bin/val.labels.bin")
    ap.add_argument("--pretrain-ratio", type=fmt_ratio, default=0.25)
    ap.add_argument("--val-mod", type=int, default=100)
    ap.add_argument("--calib-repeat", type=int, default=3, help="calibration 补充样本重复次数")
    ap.add_argument("--format-repeat", type=int, default=2, help="format 补充样本重复次数")
    ap.add_argument("--helpful-repeat", type=int, default=3, help="helpful 正例重复次数")
    ap.add_argument("--fmt-upsample", type=int, default=2, help="主数据格式样本上采样倍数")
    ap.add_argument("--listy-keep-den", type=int, default=3, help="列表类保留 1/den")
    ap.add_argument("--protect-math", action="store_true",
                    help="数学/推理样本豁免列表降采样（v2b；修复 math-add/math-mul 回归）")
    ap.add_argument("--mask-sample", type=int, default=300)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    tok = Tokenizer.from_file(args.tokenizer)
    roles_head = {r: tok.encode(f"<|im_start|>{r}\n", add_special_tokens=False).ids
                  for r in ("user", "assistant", "system")}
    end_ids = tok.encode("<|im_end|>\n", add_special_tokens=False).ids
    assert roles_head["assistant"][0] == IM_START and end_ids[0] == 2, "special 编码异常"

    pre = PretrainSource(Path(args.shards_dir), args.block_size, args.seed)
    every = max(1, round(1 / args.pretrain_ratio)) if args.pretrain_ratio > 0 else 0
    train = BlockWriter(out / "train.bin", out / "train.labels.bin", args.block_size, pre, every)

    t0 = time.time()
    stats = {
        "extras": {}, "mined": {"calib_kept": 0, "fmt_kept": 0, "listy_seen": 0,
                                 "listy_kept": 0, "math_listy_kept": 0,
                                 "listy_dropped": 0, "plain_kept": 0},
        "train_conv_by_cat": {}, "val_skipped": 0, "n_read": 0,
        "skipped_long": 0, "sample_checks": 0,
    }

    # ---- 1) 补充样本（先写，计入 250M 预算；只进 train） ----
    extra_specs = [
        ("calibration", args.calib_repeat),
        ("format", args.format_repeat),
        ("helpful", args.helpful_repeat),
    ]
    extra_items: list[tuple[str, dict]] = []
    for name, rep in extra_specs:
        p = Path(args.extra_dir) / f"{name}.jsonl"
        recs = load_extras(p, rep)
        stats["extras"][name] = {"file": str(p), "repeat": rep, "unique": len(recs) // max(rep, 1),
                                 "written": 0, "tokens": 0}
        extra_items.extend((name, r) for r in recs)
    random.Random(args.seed).shuffle(extra_items)
    for name, rec in extra_items:
        ids, mask, n_asst = conversation_segments(tok, rec.get("conversations") or [],
                                                  roles_head, end_ids)
        if n_asst == 0 or not ids:
            continue
        if len(ids) > args.block_size:
            ids, mask = ids[:args.block_size], mask[:args.block_size]
        before = train.tokens
        train.add_conversation(ids, mask)
        stats["extras"][name]["written"] += 1
        stats["extras"][name]["tokens"] += train.tokens - before
        stats["train_conv_by_cat"][name] = stats["train_conv_by_cat"].get(name, 0) + 1
    extras_tokens = train.tokens
    print(f"[extras] {json.dumps({k: {'written': v['written'], 'tokens': v['tokens']} for k, v in stats['extras'].items()}, ensure_ascii=False)} "
          f"→ train={extras_tokens/1e6:.2f}M token", flush=True)

    # ---- 2) 主数据流（分类采样；hash 留出记录一律跳过，val 复用 v1） ----
    with open(args.sft_jsonl, encoding="utf-8") as f:
        for line in f:
            if train.tokens >= args.max_tokens:
                break
            stats["n_read"] += 1
            h = int.from_bytes(hashlib.blake2b(line.encode(), digest_size=8).digest(), "little")
            if h % args.val_mod == 0:   # v1 的 val 留出集（val 文件直接复用，不再重建）
                stats["val_skipped"] += 1
                continue

            rec = json.loads(line)
            # 先分类（不 tokenize），降采样掉的不再付 tokenize 成本
            fmt = is_fmt(rec)
            calib = is_calib(rec)
            listy = is_listy(rec)
            math = is_math(rec) if args.protect_math else False
            if fmt:
                reps = args.fmt_upsample
                cat = "mined_fmt"
                stats["mined"]["fmt_kept"] += 1
            elif calib:
                reps = 1
                cat = "mined_calib"
                stats["mined"]["calib_kept"] += 1
            elif listy:
                stats["mined"]["listy_seen"] += 1
                if math:   # v2b：数学/推理样本豁免降采样
                    reps = 1
                    cat = "mined_math_listy"
                    stats["mined"]["math_listy_kept"] += 1
                elif not keep_for_listy(line, args.listy_keep_den):
                    stats["mined"]["listy_dropped"] += 1
                    continue
                else:
                    reps = 1
                    cat = "mined_listy_kept"
                    stats["mined"]["listy_kept"] += 1
            else:
                reps = 1
                cat = "mined_plain"
                stats["mined"]["plain_kept"] += 1

            ids, mask, n_asst = conversation_segments(tok, rec.get("conversations") or [],
                                                      roles_head, end_ids)
            if n_asst == 0 or not ids:
                continue
            if len(ids) > args.block_size:
                stats["skipped_long"] += 1
                ids, mask = ids[:args.block_size], mask[:args.block_size]
            if stats["sample_checks"] < 30 and stats["n_read"] % 7919 == 0:
                text = "".join(f"<|im_start|>{m.get('role', 'user')}\n{(m.get('content') or '').strip()}"
                               f"<|im_end|>\n" for m in (rec.get("conversations") or []))
                assert tok.decode(ids, skip_special_tokens=False) == text, "分段编码与整段不一致"
                stats["sample_checks"] += 1

            for _ in range(reps):
                if train.tokens >= args.max_tokens:
                    break
                train.add_conversation(ids, mask)
                stats["train_conv_by_cat"][cat] = stats["train_conv_by_cat"].get(cat, 0) + 1

            if stats["n_read"] % 100000 == 0:
                print(f"[{stats['n_read']:>7,}] train={train.tokens/1e6:.1f}M "
                      f"({(time.time()-t0)/60:.1f} min)", flush=True)

    train.close()

    # ---- 2b) val 复用 v1（同一 hash 留出规则 + 同一 2M token，保证 v1/v2 可比） ----
    val_src = Path(args.val_from)
    val_meta = json.loads((val_src / "meta.json").read_text(encoding="utf-8"))["val"]
    for name in ("val.bin", "val.labels.bin"):
        (out / name).write_bytes((val_src / name).read_bytes())
    val_stat = {"tokens": len(np.memmap(out / "val.bin", dtype=np.uint16, mode="r")),
                "blocks": len(np.memmap(out / "val.bin", dtype=np.uint16, mode="r")) // args.block_size,
                "conversations": val_meta.get("conversations"),
                "supervised_ratio": val_meta.get("supervised_ratio"),
                "source": str(val_src)}
    assert val_stat["tokens"] == val_meta["tokens"], "复用 val 的 token 数不一致"

    # ---- 3) 段级 mask 自检（不过不进训练） ----
    print("[verify] 段级 mask 自检 ...", flush=True)
    v = verify_masks(out, args.block_size, roles_head, n_sample=args.mask_sample)
    print(f"[verify] {v}", flush=True)

    # ---- 4) meta + 指纹 ----
    chat_total = sum(stats["train_conv_by_cat"].values())
    listy_kept = (stats["train_conv_by_cat"].get("mined_listy_kept", 0)
                  + stats["train_conv_by_cat"].get("mined_math_listy", 0))
    meta = {
        "source": args.sft_jsonl,
        "extra_dir": args.extra_dir,
        "template": "<|im_start|>{role}\\n{content}<|im_end|>\\n",
        "specials": {"endoftext": 0, "im_start": 1, "im_end": 2},
        "block_size": args.block_size,
        "train": {"tokens": train.tokens, "blocks": train.blocks,
                  "supervised_tokens": train.supervised,
                  "supervised_ratio": round(train.supervised / max(train.tokens, 1), 4),
                  "conversations": chat_total},
        "val": val_stat,
        "pretrain_mix": {"ratio_blocks": args.pretrain_ratio, "every_n_blocks": every,
                         "source": args.shards_dir},
        "v2_changes": {
            "calibration_extras": stats["extras"]["calibration"],
            "format_extras": stats["extras"]["format"],
            "helpful_extras": stats["extras"]["helpful"],
            "mined": stats["mined"],
            "train_conv_by_cat": stats["train_conv_by_cat"],
            "listy_ratio_after": round(listy_kept / max(chat_total, 1), 4),
            "listy_rule": (f"assistant 任一段 ≥5 个编号/项目行 → blake2b64(line)%{args.listy_keep_den}==0 保留"
                           + ("；数学/推理样本豁免（v2b）" if args.protect_math else "")),
            "protect_math": args.protect_math,
            "fmt_upsample": args.fmt_upsample,
        },
        "val_split": f"blake2b64(line) % {args.val_mod} == 0（文档级）；v2 直接复用 v1 val 文件，训练流跳过全部留出记录（跳过 {stats['val_skipped']:,} 条）",
        "skipped_long": stats["skipped_long"],
        "sample_checks": stats["sample_checks"],
        "mask_verify": v,
        "elapsed_s": round(time.time() - t0, 1),
        "created": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [f"{sha256_file(out / name)}  {name}"
             for name in ("train.bin", "train.labels.bin", "val.bin", "val.labels.bin")]
    (out / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("[done] " + json.dumps({"train": meta["train"], "val": meta["val"],
                                  "v2_changes": meta["v2_changes"]}, ensure_ascii=False), flush=True)
    print(f"[done] 落位 {out}/（SHA256SUMS 4 条）· {(time.time()-t0)/60:.1f} min", flush=True)


if __name__ == "__main__":
    main()