"""plot_loss.py — 报告配图：预训练 + SFT 数据迭代 loss 曲线（G6，Day 8/机动窗口）

素材（证据三分的 csv 面，只读）：
  reports/2026-11-19-day4-main140m.csv      主训练 train/val 曲线（45,777 步 / 3B token）
  reports/2026-11-19-day5-sft-v1.csv        SFT v1
  reports/2026-11-19-day7-sft-v2.csv        SFT v2（部署）
  reports/2026-11-19-day7-sft-v2b.csv       SFT v2b（消融）
  reports/2026-11-20-day8-sft-v2c.csv       SFT v2c（消融）
  reports/2026-11-20-day8-sft-v2d.csv       SFT v2d（机动窗口，可选 --with-v2d）

输出：reports/figs/loss-curves-<tag>.png（只增不改——重跑换 tag）
用法：.venv-pre/bin/python -I tools/plot_loss.py [--with-v2d] [--tag day8]
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
LN_V = 10.3735  # ln(32000)


def read_curve(path: Path) -> tuple[list[float], list[float], list[float]]:
    steps, train, val = [], [], []
    with path.open() as f:
        for row in csv.DictReader(f):
            steps.append(float(row["tokens_seen"]) / 1e9)  # B token 为 x 轴
            tl = row.get("train_loss") or ""
            vl = row.get("val_loss") or ""
            train.append(float(tl) if tl else None)
            val.append(float(vl) if vl else None)
    return steps, train, val


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--with-v2d", action="store_true", help="附 SFT v2d 曲线（机动窗口第 1 轮）")
    ap.add_argument("--with-v2e", action="store_true", help="附 SFT v2e 曲线（机动窗口第 2 轮）")
    ap.add_argument("--tag", default="day8")
    args = ap.parse_args()

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.6))

    # ---- 左：主训练 ----
    ax = axes[0]
    xs, tr, va = read_curve(ROOT / "reports/2026-11-19-day4-main140m.csv")
    ax.plot(xs, tr, lw=0.8, color="#888", label="train")
    ax.plot(xs, va, lw=1.4, color="#1f77b4", marker="", label="val")
    ax.axhline(LN_V, ls=":", lw=0.8, color="#bbb")
    ax.annotate(f"anchor ln(V)={LN_V:.2f}", (0.02, LN_V + 0.25), fontsize=8, color="#999")
    ax.axvspan(2.72, 3.0, color="#ffefc0", alpha=0.5)
    ax.annotate("gate-2 zone\n(last 10%: dval=0.0134\nconst-lr probe: 0.0051)",
                (2.44, 6.2), fontsize=7.5, color="#8a6d00")
    ax.set_xlabel("tokens seen (B)")
    ax.set_ylabel("loss")
    ax.set_title("Pretrain: 137.8M params x 3.0B tokens (16h07m, 52,171 tok/s)", fontsize=10)
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(alpha=0.25)

    # ---- 右：SFT 四版数据迭代 ----
    ax = axes[1]
    sft_specs = [
        ("v1", "reports/2026-11-19-day5-sft-v1.csv", "#1f77b4"),
        ("v2 (deploy)", "reports/2026-11-19-day7-sft-v2.csv", "#2ca02c"),
        ("v2b (math-protect)", "reports/2026-11-19-day7-sft-v2b.csv", "#d62728"),
        ("v2c (selective+en-rebal)", "reports/2026-11-20-day8-sft-v2c.csv", "#9467bd"),
    ]
    if args.with_v2d:
        sft_specs.append(("v2d (d2: concise+translate)", "reports/2026-11-20-v2d-sft.csv", "#ff7f0e"))
    if args.with_v2e:
        sft_specs.append(("v2e (d3: clean+exact pairs)", "reports/2026-11-20-v2e-sft.csv", "#17becf"))
    finals = []
    for name, rel, color in sft_specs:
        p = ROOT / rel
        if not p.exists():
            print(f"[skip] {rel} 不存在")
            continue
        xs, _, va = read_curve(p)
        pts = [(x, v) for x, v in zip(xs, va) if v is not None]
        ax.plot([x for x, _ in pts], [v for _, v in pts], lw=1.3, color=color, label=name)
        finals.append((name, pts[-1][1]))
    ax.set_xlabel("tokens seen (B)")
    ax.set_ylabel("val loss")
    ax.set_title("SFT: 4 data iterations on the same base (250M tok, 1 epoch each)\n"
                 "val spread 1.55-1.60 — quality moves live in eval dims, not loss", fontsize=9.5)
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(alpha=0.25)
    if finals:
        txt = "final: " + " | ".join(f"{n.split()[0]} {v:.4f}" for n, v in finals)
        ax.set_xlabel("tokens seen (B)")
        ax.text(0.98, 0.03, txt, transform=ax.transAxes, ha="right", va="bottom",
                fontsize=7.5, color="#555")

    out = ROOT / f"reports/figs/loss-curves-{args.tag}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    print(f"[done] {out}")


if __name__ == "__main__":
    main()
