"""train_char20m.py — Day 1 字符级 20M 最小训练闭环

最小可用的训练循环（完整框架 Day 3 才上，这里刻意保持"能看懂"的体量）：
  bf16 autocast · AdamW(fused) · warmup+cosine · grad clip · nanoGPT 式 memmap 随机窗口取批
  每 log 步打点 → logs/loss_curve.csv；每 eval 步算 val loss；每 sample 步采样生成；
  每 ckpt 步存 out/last.pt；--max-minutes 到点优雅收尾。
用法：仓库根目录运行 `.venv-pre/bin/python tools/train_char20m.py --max-steps N ...`
（依赖同目录 model.py，靠 sys.path[0]=tools/ 解析，勿从 data/ 等目录内启动。）
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np
import torch

from model import GPT, GPTConfig


def get_batch(arr: np.memmap, block_size: int, batch_size: int, device: str):
    """随机窗口取批（nanoGPT 式）：x = [i, i+T)，y = x 右移一位。"""
    ix = torch.randint(len(arr) - block_size - 1, (batch_size,))
    x = torch.stack([torch.from_numpy(arr[i:i + block_size].astype(np.int64)) for i in ix])
    y = torch.stack([torch.from_numpy(arr[i + 1:i + 1 + block_size].astype(np.int64)) for i in ix])
    if device == "cuda":
        x = x.pin_memory().to(device, non_blocking=True)
        y = y.pin_memory().to(device, non_blocking=True)
    return x, y


def lr_at(step: int, base_lr: float, warmup: int, max_steps: int, min_frac: float = 0.1) -> float:
    """线性 warmup → cosine 衰减到 base_lr·min_frac。"""
    if step < warmup:
        return base_lr * (step + 1) / warmup
    p = (step - warmup) / max(1, max_steps - warmup)
    p = min(p, 1.0)
    return base_lr * (min_frac + (1 - min_frac) * 0.5 * (1 + math.cos(math.pi * p)))


def make_optimizer(model: GPT, base_lr: float, weight_decay: float):
    """2D 及以上参数吃 weight_decay，1D（norm/偏置）不吃；tied embedding 只出现一次。"""
    decay, no_decay = [], []
    for p in model.parameters():
        if not p.requires_grad:
            continue
        (decay if p.dim() >= 2 else no_decay).append(p)
    return torch.optim.AdamW(
        [{"params": decay, "weight_decay": weight_decay},
         {"params": no_decay, "weight_decay": 0.0}],
        lr=base_lr, betas=(0.9, 0.95), fused=True,
    )


@torch.no_grad()
def estimate_loss(model, data, args, device, n_batches: int = 20) -> float:
    model.eval()
    losses = []
    for _ in range(n_batches):
        x, y = get_batch(data["val"], args.block_size, args.eval_batch_size, device)
        with torch.autocast("cuda", dtype=torch.bfloat16):
            _, loss = model(x, y)
        losses.append(loss.item())
    model.train()
    return sum(losses) / len(losses)


@torch.no_grad()
def sample_text(model, meta: dict, prompt: str, device: str,
                max_new_tokens: int = 200, temperature: float = 0.8, top_k: int = 200) -> str:
    stoi = meta["stoi"]
    itos = {i: s for s, i in stoi.items()}
    unk = stoi["<unk>"]
    ids = torch.tensor([[stoi.get(c, unk) for c in prompt]], dtype=torch.long, device=device)
    out = model.generate(ids, max_new_tokens, temperature=temperature, top_k=top_k)[0].tolist()
    return "".join(itos.get(i, "") for i in out)  # out 含 prompt 前缀，整体解码


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="data/day1-char20m")
    ap.add_argument("--out-dir", default="out/day1-char20m")
    ap.add_argument("--log-dir", default="logs")
    ap.add_argument("--block-size", type=int, default=512)
    ap.add_argument("--batch-size", type=int, default=64)
    ap.add_argument("--eval-batch-size", type=int, default=64)
    ap.add_argument("--n-embd", type=int, default=384)
    ap.add_argument("--n-layer", type=int, default=10)
    ap.add_argument("--n-head", type=int, default=6)
    ap.add_argument("--base-lr", type=float, default=3e-3)
    ap.add_argument("--min-lr-frac", type=float, default=0.1)
    ap.add_argument("--warmup", type=int, default=200)
    ap.add_argument("--weight-decay", type=float, default=0.1)
    ap.add_argument("--grad-clip", type=float, default=1.0)
    ap.add_argument("--max-steps", type=int, default=100000)
    ap.add_argument("--max-minutes", type=float, default=90.0)
    ap.add_argument("--eval-every", type=int, default=200)
    ap.add_argument("--sample-every", type=int, default=500)
    ap.add_argument("--ckpt-every", type=int, default=1000)
    ap.add_argument("--log-every", type=int, default=20)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    assert torch.cuda.is_available(), "Day 1 训练需要 CUDA（D-09 全本地）"
    device = "cuda"
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    torch.set_float32_matmul_precision("high")

    data_dir = Path(args.data_dir)
    meta = json.loads((data_dir / "meta.json").read_text(encoding="utf-8"))
    data = {
        "train": np.memmap(data_dir / "train.bin", dtype=np.uint16, mode="r"),
        "val": np.memmap(data_dir / "val.bin", dtype=np.uint16, mode="r"),
    }

    cfg = GPTConfig(
        vocab_size=meta["vocab_size"],
        n_embd=args.n_embd, n_layer=args.n_layer, n_head=args.n_head,
        block_size=args.block_size,
    )
    model = GPT(cfg).to(device)
    optimizer = make_optimizer(model, args.base_lr, args.weight_decay)

    stamp = time.strftime("%Y%m%d-%H%M%S")
    log_dir = Path(args.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"day1-char20m-{stamp}.log"
    csv_path = log_dir / "loss_curve.csv"
    new_csv = not csv_path.exists()
    csv_f = csv_path.open("a", newline="")
    csv_w = csv.writer(csv_f)
    if new_csv:
        csv_w.writerow(["step", "train_loss", "val_loss", "lr", "tok_per_s", "elapsed_s"])

    def log(msg: str) -> None:
        print(msg, flush=True)
        with log_path.open("a", encoding="utf-8") as f:
            f.write(msg + "\n")

    log(f"[cfg] {json.dumps(asdict(cfg), ensure_ascii=False)}")
    log(f"[model] params={model.num_params():,} (non-emb {model.num_params(non_embedding=True):,}) "
        f"vocab={cfg.vocab_size} train_chars={meta['stats']['train_chars']:,}")
    log(f"[data] train.bin {meta['stats']['train_bin_mb']}MB / val.bin {meta['stats']['val_bin_mb']}MB")

    t0 = time.time()
    tokens_seen = 0
    running_loss = 0.0
    n_since_log = 0
    model.train()
    assert args.max_steps >= 1
    for step in range(args.max_steps):
        lr = lr_at(step, args.base_lr, args.warmup, args.max_steps, args.min_lr_frac)
        for g in optimizer.param_groups:
            g["lr"] = lr

        x, y = get_batch(data["train"], args.block_size, args.batch_size, device)
        with torch.autocast("cuda", dtype=torch.bfloat16):
            _, loss = model(x, y)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), args.grad_clip)
        optimizer.step()

        tokens_seen += x.numel()
        running_loss += loss.item()
        n_since_log += 1

        if (step + 1) % args.log_every == 0 or step == 0:
            elapsed = time.time() - t0
            tps = tokens_seen / elapsed
            avg = running_loss / n_since_log
            running_loss = 0.0
            n_since_log = 0
            log(f"step {step + 1:6d} | loss {avg:.4f} | lr {lr:.2e} "
                f"| {tps:,.0f} tok/s | {elapsed / 60:.1f} min")
            csv_w.writerow([step + 1, round(avg, 4), "", lr, round(tps), round(elapsed)])

        if (step + 1) % args.eval_every == 0:
            val = estimate_loss(model, data, args, device)
            log(f"step {step + 1:6d} | [val] loss {val:.4f}")
            csv_w.writerow([step + 1, "", round(val, 4), lr, "", round(time.time() - t0)])
            csv_f.flush()

        if (step + 1) % args.sample_every == 0:
            log(f"step {step + 1:6d} | [sample] " + "-" * 40)
            for prompt in ("人工智能是", "从前有一座山"):
                log("  " + sample_text(model, meta, prompt, device).replace("\n", "\n  "))
            log("  " + "-" * 46)

        if (step + 1) % args.ckpt_every == 0:
            torch.save({
                "step": step + 1,
                "config": asdict(cfg),
                "model": model.state_dict(),
                "optimizer": optimizer.state_dict(),
                "meta_stats": meta["stats"],
            }, out_dir / "last.pt")
            log(f"step {step + 1:6d} | [ckpt] out/last.pt")

        if (time.time() - t0) > args.max_minutes * 60:
            log(f"[stop] 达到时间预算 {args.max_minutes} min，step {step + 1} 处优雅收尾")
            break

    torch.save({
        "step": step + 1, "config": asdict(cfg), "model": model.state_dict(),
        "optimizer": optimizer.state_dict(), "meta_stats": meta["stats"],
    }, out_dir / "last.pt")
    val = estimate_loss(model, data, args, device)
    elapsed = time.time() - t0
    log(f"[final] step {step + 1} | val loss {val:.4f} | 总用时 {elapsed / 60:.1f} min | "
        f"均值吞吐 {tokens_seen / elapsed:,.0f} tok/s（字符/秒）")
    csv_w.writerow([step + 1, "", round(val, 4), lr, round(tokens_seen / elapsed), round(elapsed)])
    csv_f.close()
    log("[final] checkpoint → out/last.pt")


if __name__ == "__main__":
    main()
