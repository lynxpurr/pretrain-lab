"""eval_lang.py — 分语言 val：SFT val 按中/英分块算 PPL 分项（spec 2026-11-21 T5）

目的：收口"英文正例上采样（v2c~v2e）是否稀释中文"的疑问（Day 8 qa-day-8 题 3）。
方法：data/sft-mix/val.bin（各 SFT 版共用的同一 val，2M token ≈1,955 块）按块解码，
CJK/拉丁字母占比分类 zh/en；每块算两个 CE：
  - all = 全 token CE（语言建模口径，y = 右移一位）
  - sup = assistant 监督 CE（labels + ignore_index=-100，指令拟合口径）
同语言块按 8 块一批前向（batch 内 CE 为 token 加权平均，×n 还原累加即精确聚合），
按语言分列 PPL = exp(mean CE)；zh 相对 v1（无英文上采样基线）的退化幅度按 spec §5
判读：≤1% 无稀释证据 / 1~3% 弱信号 / >3% 有稀释信号。

用法（仓库根目录，GPU 空闲时跑）：
  .venv-pre/bin/python -I tools/eval_lang.py \
      --ckpt base=out/main140m/last.pt --ckpt v1=out/sft-v1/last.pt \
      --ckpt v2=out/sft-v2/last.pt --ckpt v2e=out/sft-v2e/last.pt \
      --out reports/2026-11-21-langval.md
"""
from __future__ import annotations

import argparse
import csv
import math
import re
import sys
from pathlib import Path

import numpy as np
import torch

from tokenizers import Tokenizer

sys.path.insert(0, str(Path(__file__).resolve().parent))

from model import GPT, GPTConfig  # noqa: E402

_CJK = re.compile(r"[\u4e00-\u9fff]")
_LATIN = re.compile(r"[A-Za-z]")


def load_model(ckpt_path: Path, device: str):
    ck = torch.load(ckpt_path, map_location=device, weights_only=False)
    saved = ck["config"]
    cfg = GPTConfig(**{k: saved[k] for k in
                       ("vocab_size", "n_embd", "n_layer", "n_head", "block_size",
                        "rope_base", "multiple_of") if k in saved})
    model = GPT(cfg).to(device)
    model.load_state_dict(ck["model"])
    model.eval()
    return model, ck.get("step")


def classify_blocks(tok: Tokenizer, arr: np.ndarray, block: int,
                    threshold: float, min_chars: int):
    """按块解码并分类 zh/en；字母信息量不足（纯数字/符号/填充）的块跳过。"""
    labels = []
    for i in range(len(arr) // block):
        text = tok.decode(arr[i * block:(i + 1) * block].tolist(), skip_special_tokens=True)
        cjk = len(_CJK.findall(text))
        latin = len(_LATIN.findall(text))
        if cjk + latin < min_chars:
            labels.append(None)
        else:
            labels.append("zh" if cjk / (cjk + latin) >= threshold else "en")
    return labels


@torch.no_grad()
def lang_ce(model, arr, labels_arr, offs, device: str, sup: bool, block: int, bs: int = 8):
    """一组同语言块的 token 加权 mean CE（sup=True 用 labels/-100，否则全 token）。"""
    total, count = 0.0, 0
    for i in range(0, len(offs), bs):
        chunk = offs[i:i + bs]
        x = torch.from_numpy(np.stack([arr[o:o + block].astype(np.int64) for o in chunk])).to(device)
        if sup:
            y = torch.from_numpy(np.stack([labels_arr[o:o + block].astype(np.int64) for o in chunk])).to(device)
            n = int((y != -100).sum())
        else:
            y = torch.from_numpy(np.stack([arr[o + 1:o + 1 + block].astype(np.int64) for o in chunk])).to(device)
            n = y.numel()
        if n == 0:
            continue
        with torch.autocast("cuda", dtype=torch.bfloat16):
            _, loss = model(x, y, ignore_index=-100)
        total += float(loss) * n
        count += n
    return (total / count if count else None), count


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", action="append", required=True, help="name=path（可重复）")
    ap.add_argument("--val-dir", default="data/sft-mix")
    ap.add_argument("--tokenizer", default="data/tokenizer-32k/tokenizer.json")
    ap.add_argument("--block", type=int, default=1024)
    ap.add_argument("--threshold", type=float, default=0.3, help="CJK 占比 ≥threshold 判 zh")
    ap.add_argument("--min-chars", type=int, default=20)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--out", default="reports/2026-11-21-langval.md")
    args = ap.parse_args()

    device = args.device
    val_dir = Path(args.val_dir)
    tok = Tokenizer.from_file(args.tokenizer)

    x = np.memmap(val_dir / "val.bin", dtype=np.uint16, mode="r")
    y = np.memmap(val_dir / "val.labels.bin", dtype=np.int16, mode="r")
    n_blocks = len(x) // args.block
    print(f"[data] val {len(x):,} tok · {n_blocks} 块 · block={args.block}")

    lang_of = classify_blocks(tok, x, args.block, args.threshold, args.min_chars)
    n_zh = sum(1 for t in lang_of if t == "zh")
    n_en = sum(1 for t in lang_of if t == "en")
    n_skip = sum(1 for t in lang_of if t is None)
    print(f"[lang] zh={n_zh} en={n_en} skip={n_skip}（threshold={args.threshold}）")

    groups = {"zh": [], "en": []}
    for i, t in enumerate(lang_of):
        # 全 token CE 需要 y = arr[o+1:o+1+block]，故末块按 eval.py 同款 (len-1)//block 规避越界
        if t is not None and (i + 1) * args.block < len(x):
            groups[t].append(i * args.block)

    results = {}  # name -> {lang: ((ce_all, n_all), (ce_sup, n_sup))}
    for pair in args.ckpt:
        name, path = pair.split("=", 1)
        model, step = load_model(Path(path), device)
        print(f"[ckpt] {name} = {path}（step={step}）")
        res = {}
        for lang in ("zh", "en"):
            ce_all, n_all = lang_ce(model, x, y, groups[lang], device, sup=False, block=args.block)
            ce_sup, n_sup = lang_ce(model, x, y, groups[lang], device, sup=True, block=args.block)
            res[lang] = ((ce_all, n_all), (ce_sup, n_sup))
            print(f"  [{lang}] all PPL {math.exp(ce_all):.4f} (n={n_all:,}) · "
                  f"sup PPL {math.exp(ce_sup):.4f} (n={n_sup:,})")
        results[name] = res
        del model
        torch.cuda.empty_cache()

    v1 = results.get("v1")

    def rel(name, lang, which):
        """zh PPL 相对 v1 的退化百分比（v1 自身与未提供 v1 时为 —）。"""
        if v1 is None or name == "v1":
            return None
        cur = results[name][lang][which][0]
        base = v1[lang][which][0]
        if cur is None or base is None:
            return None
        return (math.exp(cur) / math.exp(base) - 1) * 100.0

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    csv_path = out.with_suffix(".csv")
    with csv_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["model", "lang", "ppl_all", "ppl_sup", "n_tok_all", "n_tok_sup",
                    "rel_vs_v1_all_pct", "rel_vs_v1_sup_pct"])
        for name, res in results.items():
            for lang in ("zh", "en"):
                (a, na), (s, ns) = res[lang]
                r0, r1 = rel(name, lang, 0), rel(name, lang, 1)
                w.writerow([name, lang, f"{math.exp(a):.4f}", f"{math.exp(s):.4f}",
                            na, ns,
                            f"{r0:.2f}" if r0 is not None else "",
                            f"{r1:.2f}" if r1 is not None else ""])

    lines = [
        "# 分语言 val（中/英 PPL 分项）",
        "",
        f"> val = `{val_dir}/val.bin`（各 SFT 版共用，{n_blocks} 块：zh {n_zh} / en {n_en} / skip {n_skip}，"
        f"CJK 占比 ≥{args.threshold} 判 zh）· CE 口径：**all** = 全 token（语言建模），**sup** = assistant 监督 token（指令拟合）。",
        "",
        "| 模型 | zh PPL (all) | en PPL (all) | zh PPL (sup) | en PPL (sup) | zh/all vs v1 | zh/sup vs v1 |",
        "|---|---|---|---|---|---|---|",
    ]
    for name, res in results.items():
        (a_zh, _), (s_zh, _) = res["zh"]
        (a_en, _), (s_en, _) = res["en"]
        r0, r1 = rel(name, "zh", 0), rel(name, "zh", 1)
        lines.append(
            f"| {name} | {math.exp(a_zh):.4f} | {math.exp(a_en):.4f} | "
            f"{math.exp(s_zh):.4f} | {math.exp(s_en):.4f} | "
            f"{'—' if r0 is None else f'{r0:+.2f}%'} | {'—' if r1 is None else f'{r1:+.2f}%'} |")
    lines += [
        "",
        "判读（spec §5 预注册）：zh 相对 v1 退化 ≤1% = 无稀释证据；1~3% = 弱信号；>3% = 有稀释信号。",
        "",
        f"CSV: `{csv_path.name}`",
    ]
    out.write_text("\n".join(lines) + "\n")
    print(f"[done] {out} · {csv_path}")


if __name__ == "__main__":
    main()
