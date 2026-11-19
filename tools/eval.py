"""eval.py — Day 5: 评测框架（held-out 困惑度 + 自设计测试集）

两个维度，对应 G5：
  1) **held-out PPL**
     - 预训练 val（data/shards/val.bin，4M token）→ 底座语言建模能力
     - SFT val（data/sft-mix/val.bin + labels，只算 assistant token）→ 指令跟随拟合度
  2) **自设计测试集**（data/eval/tests.json，18 题，7 个 tag：事实/数学/身份/解释/翻译/总结/格式/代码/推理/校准）
     - 固定 chat 模板 + **greedy 解码**（可复现），在 `<|im_end|>` 处截断
     - 规则判分：`expect_any` 任一子串命中即 pass（大小写不敏感）；同时落原文供人工复核

用法（仓库根目录，GPU 空闲时跑）：
  .venv-pre/bin/python -I tools/eval.py \
      --ckpt base=out/main140m/last.pt --ckpt sft=out/sft-v1/last.pt \
      --out reports/2026-11-19-day5-eval.md
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch

from tokenizers import Tokenizer

sys.path.insert(0, str(Path(__file__).resolve().parent))

from model import GPT, GPTConfig  # noqa: E402




def load_model(ckpt_path: Path, device: str):
    ck = torch.load(ckpt_path, map_location=device, weights_only=False)
    saved = ck["config"]
    cfg = GPTConfig(**{k: saved[k] for k in
                       ("vocab_size", "n_embd", "n_layer", "n_head", "block_size",
                        "rope_base", "multiple_of") if k in saved})
    model = GPT(cfg).to(device)
    model.load_state_dict(ck["model"])
    model.eval()
    return model, cfg, ck.get("step")


@torch.no_grad()
def ppl_on_windows(model, arr, block: int, n_iter: int, bs: int, device: str, labels=None):
    """按窗口算 CE（用模型自带 loss：预训练 y = 右移一位；SFT y = labels + ignore_index）。"""
    n_blocks = (len(arr) - 1) // block
    rng = np.random.default_rng(1234)
    need = n_iter * bs
    offs = rng.permutation(n_blocks)[:need] * block
    total, count = 0.0, 0
    for i in range(n_iter):
        idx = offs[i * bs:(i + 1) * bs]
        x = np.stack([arr[o:o + block].astype(np.int64) for o in idx])
        x = torch.from_numpy(x).to(device)
        if labels is None:
            y = np.stack([arr[o + 1:o + 1 + block].astype(np.int64) for o in idx])
        else:
            y = np.stack([labels[o:o + block].astype(np.int64) for o in idx])
        y = torch.from_numpy(y).to(device)
        with torch.autocast("cuda", dtype=torch.bfloat16):
            _, loss = model(x, y, ignore_index=-100)
        n = y.numel() if labels is None else int((y != -100).sum())
        total += float(loss) * n
        count += n
    return total / max(count, 1)


def repetition_metrics(text: str):
    """字符级退化指标：distinct-2（去重二元组占比）与 rep-4（重复四元组占比）。"""
    s = "".join(text.split())
    if len(s) < 5:
        return 1.0, 0.0
    bigrams = [s[i:i + 2] for i in range(len(s) - 1)]
    quads = [s[i:i + 4] for i in range(len(s) - 3)]
    d2 = len(set(bigrams)) / max(len(bigrams), 1)
    rep4 = 1.0 - len(set(quads)) / max(len(quads), 1)
    return d2, rep4


@torch.no_grad()
def chat(model, tok: Tokenizer, prompt: str, device: str, max_new: int = 100,
         temperature: float = 0.0, top_k: int = 0, top_p: float = 1.0,
         rep_penalty: float = 1.0) -> str:
    text = f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
    ids = tok.encode(text, add_special_tokens=False).ids
    idx = torch.tensor([ids], dtype=torch.long, device=device)
    out = model.generate(idx, max_new, temperature=temperature if temperature > 0 else 1.0,
                         top_k=(top_k or None), top_p=top_p, repetition_penalty=rep_penalty,
                         greedy=(temperature <= 0))
    full = tok.decode(out[0].tolist(), skip_special_tokens=False)
    return full[len(text):].split("<|im_end|>")[0].strip()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", action="append", required=True, help="name=path（可重复）")
    ap.add_argument("--tests", default="data/eval/tests.json")
    ap.add_argument("--tokenizer", default="data/tokenizer-32k/tokenizer.json")
    ap.add_argument("--pretrain-val", default="data/shards/val.bin")
    ap.add_argument("--sft-val", default="data/sft-mix/val.bin")
    ap.add_argument("--sft-labels", default="data/sft-mix/val.labels.bin")
    ap.add_argument("--block", type=int, default=1024)
    ap.add_argument("--ppl-iters", type=int, default=40)
    ap.add_argument("--ppl-batch", type=int, default=8)
    ap.add_argument("--max-new", type=int, default=100)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--decode-name", default="greedy")
    ap.add_argument("--temperature", type=float, default=0.0, help="0 = greedy")
    ap.add_argument("--top-k", type=int, default=0)
    ap.add_argument("--top-p", type=float, default=1.0)
    ap.add_argument("--rep-penalty", type=float, default=1.0)
    ap.add_argument("--skip-ppl", action="store_true")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default="reports/2026-11-19-day5-eval.md")
    args = ap.parse_args()

    device = args.device if args.device == "cpu" else ("cuda" if torch.cuda.is_available() else "cpu")
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    tok = Tokenizer.from_file(args.tokenizer)
    tests = json.loads(Path(args.tests).read_text(encoding="utf-8"))
    pre_val = np.memmap(args.pretrain_val, dtype=np.uint16, mode="r")
    sft_val = np.memmap(args.sft_val, dtype=np.uint16, mode="r")
    sft_lab = np.memmap(args.sft_labels, dtype=np.int16, mode="r")

    rows, model_sections = [], []
    head = [f"# 评测报告（{time.strftime('%Y-%m-%d %H:%M')}）", "",
            f"- 预训练 val PPL：{args.pretrain_val}（{len(pre_val):,} token，{args.ppl_iters}×{args.ppl_batch} 窗口）",
            f"- SFT val PPL：{args.sft_val}（只算 assistant token，ignore_index=-100）",
            f"- 测试集：{args.tests}（{len(tests)} 题）· 解码协议 = **{args.decode_name}**"
            f"（T={args.temperature} top_k={args.top_k} top_p={args.top_p} rep={args.rep_penalty}）", ""]

    summary = []
    for spec in args.ckpt:
        name, path = spec.split("=", 1)
        t0 = time.time()
        model, cfg, step = load_model(Path(path), device)
        if args.skip_ppl:
            ppl_pre = ppl_sft = float("nan")
        else:
            ppl_pre = ppl_on_windows(model, pre_val, args.block, args.ppl_iters, args.ppl_batch, device)
            ppl_sft = ppl_on_windows(model, sft_val, args.block, args.ppl_iters, args.ppl_batch, device,
                                     labels=sft_lab)
        outs, passed = [], 0
        for t in tests:
            ans = chat(model, tok, t["prompt"], device, args.max_new, args.temperature,
                       args.top_k, args.top_p, args.rep_penalty)
            ok = any(k.lower() in ans.lower() for k in t["expect_any"])
            passed += ok
            d2, r4 = repetition_metrics(ans)
            outs.append((t["id"], t["tag"], ok, ans, d2, r4))
            rows.append([name, args.decode_name, t["id"], t["tag"], int(ok), round(d2, 3),
                         round(r4, 3), ans.replace("\n", " ")[:1000]])
        acc = passed / len(tests)
        d2_mean = sum(o[4] for o in outs) / len(outs)
        r4_mean = sum(o[5] for o in outs) / len(outs)
        summary.append((name, step, ppl_pre, ppl_sft, passed, acc, time.time() - t0, d2_mean, r4_mean))
        ppl_txt = "跳过" if args.skip_ppl else f"{math_exp(ppl_pre):.3f}"
        ppl_txt2 = "跳过" if args.skip_ppl else f"{math_exp(ppl_sft):.3f}"
        sec = [f"## {name} · {args.decode_name}（step {step}）", "",
               f"- 预训练 val PPL **{ppl_txt}** · SFT val PPL **{ppl_txt2}** · "
               f"测试集 **{passed}/{len(tests)} = {acc:.0%}** · distinct-2 **{d2_mean:.3f}** · "
               f"rep-4 **{r4_mean:.3f}**（{time.time()-t0:.0f}s）", "",
               "| id | tag | 结果 | d2 | rep4 | 输出（截断 120 字） |", "|---|---|---|---|---|---|"]
        for tid, tag, ok, ans, d2, r4 in outs:
            sec.append(f"| {tid} | {tag} | {'✅' if ok else '❌'} | {d2:.3f} | {r4:.3f} | {ans[:120].replace('|', '\\|')} |")
        sec.append("")
        model_sections.append("\n".join(sec))

    md = head + ["## 汇总", "",
                 "| 模型 | 解码 | step | 预训练 PPL | SFT PPL | 测试集 | distinct-2 | rep-4 |",
                 "|---|---|---|---|---|---|---|---|"]
    for name, step, p1, p2, passed, acc, _, d2m, r4m in summary:
        p1s = "跳过" if p1 != p1 else f"{math_exp(p1):.3f}"
        p2s = "跳过" if p2 != p2 else f"{math_exp(p2):.3f}"
        md.append(f"| {name} | {args.decode_name} | {step} | {p1s} | {p2s} | "
                  f"{passed}/{len(tests)} ({acc:.0%}) | {d2m:.3f} | {r4m:.3f} |")
    md.append("")
    md.extend(model_sections)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(md) + "\n", encoding="utf-8")
    csv_path = out.with_suffix(".csv")
    with csv_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["model", "decode", "test_id", "tag", "pass", "distinct2", "rep4", "answer"])
        w.writerows(rows)
    print("\n".join(md[:12]))
    print(f"[done] {out} · {csv_path}")


def math_exp(x: float) -> float:
    """PPL = exp(loss)。"""
    import math
    return math.exp(min(x, 30))


if __name__ == "__main__":
    main()