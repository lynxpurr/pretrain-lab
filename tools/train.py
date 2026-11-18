"""train.py — Day 3 完整训练框架（多分片 memmap + 梯度累积 + 续训闭环 + 采样/评估）

相比 train_char20m.py（Day 1 最小闭环）新增六件：
  1) 多分片随机窗口取批——直接从 data/shards/ 的 6 个 1GB 片训练，不拼单文件；
     按分片 token 数加权选片，片内均匀取窗口（片与片同分布，跨片拼接无收益）。
  2) 梯度累积 + 按 **token 预算** 定总步数：LR 调度由 total_steps 决定，
     与 --max-minutes 解耦——中断续训后 cosine 曲线仍落在同一条上。
  3) 续训闭环：last.pt 含 model/optimizer/step/tokens_seen/RNG；--resume auto 断点续训。
  4) 固定 val 窗口（跨 step、跨 resume 可比；非重叠块 + 固定种子）+ 固定 prompt 采样
     （HF tokenizer decode(skip_special_tokens=False)，中英各两条）。
  5) 吞吐双读数：窗口 tok/s（含 eval/sample 开销，实时）+ 纯训练 tok/s（扣掉开销墙钟，
     决策门①判定用后者）。
  6) logs/<run>.exit 退出标记（EXIT:0 / EXIT:1:...）——stale exit 教训的机制化。

用法（仓库根目录运行；依赖同目录 model.py，靠 sys.path[0]=tools/ 解析）：
  .venv-pre/bin/python -I tools/train.py --run-name day3-50m --data-dir data/shards \\
      --n-embd 576 --n-layer 8 --n-head 9 --block-size 1024 \\
      --batch-size 16 --grad-accum 4 --base-lr 6e-4 --warmup 500 --max-minutes 30
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import time
import traceback
from dataclasses import asdict
from pathlib import Path

import numpy as np
import torch
from tokenizers import Tokenizer

# -I（隔离模式）不把脚本目录加进 sys.path——显式补上以便 import 同目录 model.py
sys.path.insert(0, str(Path(__file__).resolve().parent))

from model import GPT, GPTConfig  # noqa: E402

PROMPTS_ZH = ["人工智能是", "中国的首都是"]
PROMPTS_EN = ["The capital of France is", "Once upon a time,"]


# ------------------------------------------------------------- 数据侧 ----

class ShardedTrainData:
    """多分片 memmap：按 token 数加权选片 → 片内均匀随机窗口 → (x, y=x 右移一位)。"""

    def __init__(self, data_dir: Path, seed: int):
        meta = json.loads((data_dir / "meta.json").read_text(encoding="utf-8"))
        self.vocab_size = meta["vocab_size"]
        names = [s["name"] for s in meta["shards"]] if "shards" in meta else ["train.bin"]
        self.arrays = [np.memmap(data_dir / n, dtype=np.uint16, mode="r") for n in names]
        self.lens = np.asarray([len(a) for a in self.arrays], dtype=np.float64)
        self.probs = self.lens / self.lens.sum()
        self.rng = np.random.default_rng(seed)
        self.win: np.ndarray | None = None

    def batch(self, batch_size: int, block_size: int, device: str):
        if self.win is None or self.win.shape != (batch_size, block_size + 1):
            self.win = np.empty((batch_size, block_size + 1), dtype=np.uint16)
        win = self.win
        shard_ids = self.rng.choice(len(self.arrays), size=batch_size, p=self.probs)
        for j, si in enumerate(shard_ids):
            a = self.arrays[si]
            off = int(self.rng.integers(0, len(a) - block_size - 2))
            win[j] = a[off:off + block_size + 1]  # 一次读 T+1，x/y 共享（省一半拷贝）
        x = torch.from_numpy(win[:, :block_size].astype(np.int64))
        y = torch.from_numpy(win[:, 1:].astype(np.int64))
        return x.to(device), y.to(device)

    def rng_state(self):
        return self.rng.bit_generator.state

    def set_rng_state(self, state):
        self.rng.bit_generator.state = state


class FixedValData:
    """固定 val 窗口：块编号固定种子抽样、块不重叠——保证不同 step / 不同 run 的 val 可比。"""

    def __init__(self, path: Path, block_size: int, n_iters: int, batch_size: int, seed: int):
        self.arr = np.memmap(path, dtype=np.uint16, mode="r")
        self.block_size = block_size
        n_blocks = max(1, (len(self.arr) - 1) // block_size)
        need = n_iters * batch_size
        if need > n_blocks:
            raise ValueError(f"val 窗口不够：需要 {need} 块，val.bin 只有 {n_blocks} 块")
        rng = np.random.default_rng(seed)
        self.offsets = rng.permutation(n_blocks)[:need].reshape(n_iters, batch_size) * block_size

    def batch(self, it: int, device: str):
        offs = self.offsets[it]
        x = np.stack([self.arr[o:o + self.block_size].astype(np.int64) for o in offs])
        y = np.stack([self.arr[o + 1:o + 1 + self.block_size].astype(np.int64) for o in offs])
        return torch.from_numpy(x).to(device), torch.from_numpy(y).to(device)


# ------------------------------------------------------------- 训练侧 ----

def lr_at(step: int, base_lr: float, warmup: int, total_steps: int, min_frac: float = 0.1) -> float:
    """线性 warmup → cosine 衰减到 base_lr·min_frac（step 为已完成步数）。"""
    if step < warmup:
        return base_lr * (step + 1) / max(1, warmup)
    p = (step - warmup) / max(1, total_steps - warmup)
    p = min(p, 1.0)
    return base_lr * (min_frac + (1 - min_frac) * 0.5 * (1 + math.cos(math.pi * p)))


def make_optimizer(model: GPT, base_lr: float, weight_decay: float):
    """2D 及以上吃 weight_decay，1D（norm/偏置）不吃；tied embedding 只出现一次。"""
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
def estimate_loss(model, val: FixedValData, batch_size: int, device: str, n_iters: int) -> float:
    model.eval()
    losses = []
    for it in range(n_iters):
        x, y = val.batch(it, device)
        with torch.autocast("cuda", dtype=torch.bfloat16):
            _, loss = model(x, y)
        losses.append(loss.item())
    model.train()
    return sum(losses) / len(losses)


@torch.no_grad()
def sample_text(model, tok: Tokenizer, prompt: str, device: str,
                max_new_tokens: int = 80, temperature: float = 0.8, top_k: int = 200) -> str:
    ids = tok.encode(prompt, add_special_tokens=False).ids
    idx = torch.tensor([ids], dtype=torch.long, device=device)
    out = model.generate(idx, max_new_tokens, temperature=temperature, top_k=top_k)
    model.train()
    return tok.decode(out[0].tolist(), skip_special_tokens=False)


def fmt_dur(sec: float) -> str:
    sec = int(sec)
    return f"{sec // 3600}h{sec % 3600 // 60:02d}m{sec % 60:02d}s"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-name", default="day3-run")
    ap.add_argument("--data-dir", default="data/shards")
    ap.add_argument("--out-dir", default="")
    ap.add_argument("--log-dir", default="logs")
    ap.add_argument("--tokenizer", default="data/tokenizer-32k/tokenizer.json")
    # 模型
    ap.add_argument("--n-embd", type=int, default=576)
    ap.add_argument("--n-layer", type=int, default=8)
    ap.add_argument("--n-head", type=int, default=9)
    ap.add_argument("--block-size", type=int, default=1024)
    # 优化
    ap.add_argument("--batch-size", type=int, default=16, help="micro-batch（单次前向）")
    ap.add_argument("--grad-accum", type=int, default=4)
    ap.add_argument("--base-lr", type=float, default=6e-4)
    ap.add_argument("--min-lr-frac", type=float, default=0.1)
    ap.add_argument("--warmup", type=int, default=500)
    ap.add_argument("--weight-decay", type=float, default=0.1)
    ap.add_argument("--grad-clip", type=float, default=1.0)
    ap.add_argument("--target-tokens", type=float, default=3.0e9, help="总训练 token 预算（定 LR 调度）")
    ap.add_argument("--max-steps", type=int, default=0, help=">0 时直接指定总步数（覆盖 token 预算）")
    ap.add_argument("--max-minutes", type=float, default=0.0, help="墙钟兜底；0 = 不限")
    # 记录/存档
    ap.add_argument("--log-every", type=int, default=20)
    ap.add_argument("--eval-every", type=int, default=500)
    ap.add_argument("--eval-iters", type=int, default=40)
    ap.add_argument("--eval-batch-size", type=int, default=16)
    ap.add_argument("--sample-every", type=int, default=2000)
    ap.add_argument("--sample-tokens", type=int, default=80)
    ap.add_argument("--ckpt-every", type=int, default=1000)
    ap.add_argument("--keep-ckpts", type=int, default=0, help=">0 = 只保留最近 N 个滚动 ckpt")
    ap.add_argument("--resume", default="", help="auto | path/to/last.pt")
    ap.add_argument("--compile", action="store_true", help="torch.compile（实验项）")
    ap.add_argument("--grad-ckpt", action="store_true", help="激活检查点（省显存，慢 ~10~20%）")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--notes", default="")
    args = ap.parse_args()

    assert torch.cuda.is_available(), "需要 CUDA（D-09 全本地）"
    device = "cuda"
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    torch.set_float32_matmul_precision("high")
    torch.cuda.reset_peak_memory_stats()

    out_dir = Path(args.out_dir or f"out/{args.run_name}")
    log_dir = Path(args.log_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    log_path = log_dir / f"{args.run_name}-{stamp}.log"
    exit_path = log_dir / f"{args.run_name}.exit"
    csv_path = log_dir / f"{args.run_name}-loss_curve.csv"

    def log(msg: str) -> None:
        print(msg, flush=True)
        with log_path.open("a", encoding="utf-8") as f:
            f.write(msg + "\n")

    def finish(code: str, msg: str) -> None:
        exit_path.write_text(f"EXIT:{code} {msg}\n", encoding="utf-8")

    if exit_path.exists():  # stale exit 标记（lesson Day 2）
        exit_path.unlink()

    try:
        data = ShardedTrainData(Path(args.data_dir), args.seed)
        val = FixedValData(Path(args.data_dir) / "val.bin", args.block_size,
                           args.eval_iters, args.eval_batch_size, args.seed ^ 0x9E3779B9)
        tok = Tokenizer.from_file(args.tokenizer)

        cfg = GPTConfig(vocab_size=data.vocab_size, n_embd=args.n_embd,
                        n_layer=args.n_layer, n_head=args.n_head, block_size=args.block_size)
        model = GPT(cfg).to(device)
        tokens_per_step = args.batch_size * args.block_size * args.grad_accum
        total_steps = args.max_steps if args.max_steps > 0 else math.ceil(args.target_tokens / tokens_per_step)
        optimizer = make_optimizer(model, args.base_lr, args.weight_decay)

        # ---- 续训 ----
        start_step, tokens_seen = 0, 0
        ckpt_path = None
        if args.resume:
            ckpt_path = out_dir / "last.pt" if args.resume == "auto" else Path(args.resume)
            assert ckpt_path.exists(), f"续训点不存在：{ckpt_path}"
            ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
            saved_cfg = ckpt["config"]
            for key in ("vocab_size", "n_embd", "n_layer", "n_head", "block_size"):
                assert saved_cfg[key] == getattr(cfg, key), \
                    f"续训配置不匹配 {key}: ckpt={saved_cfg[key]} args={getattr(cfg, key)}"
            model.load_state_dict(ckpt["model"])
            optimizer.load_state_dict(ckpt["optimizer"])
            start_step = ckpt["step"]
            tokens_seen = ckpt.get("tokens_seen", start_step * tokens_per_step)
            if "torch_rng" in ckpt:
                # map_location 会把 RNG 字节张量也搬到 GPU，set_rng_state 要求 CPU ByteTensor
                torch.set_rng_state(ckpt["torch_rng"].cpu())
                torch.cuda.set_rng_state(ckpt["cuda_rng"].cpu())
            if "data_rng" in ckpt:
                data.set_rng_state(ckpt["data_rng"])
            log(f"[resume] {ckpt_path} → step={start_step} / total={total_steps} "
                f"tokens_seen={tokens_seen:,}")

        if args.grad_ckpt:
            import functools
            from torch.utils.checkpoint import checkpoint as _ckpt
            for blk in model.blocks:
                blk.forward = functools.partial(_ckpt, blk.__class__.forward, blk, use_reentrant=False)
            log("[opt] 激活检查点开启（每块重算 forward）")
        if args.compile:
            model = torch.compile(model)
            log("[opt] torch.compile 开启")

        raw_model = model._orig_mod if hasattr(model, "_orig_mod") else model

        csv_f = csv_path.open("a", newline="")
        csv_w = csv.writer(csv_f)
        if csv_path.stat().st_size == 0:
            csv_w.writerow(["step", "train_loss", "val_loss", "lr", "tok_per_s",
                            "tokens_seen", "elapsed_s", "peak_gb"])

        log(f"[cfg] {json.dumps(asdict(cfg), ensure_ascii=False)} "
            f"bs={args.batch_size}×accum{args.grad_accum}×T{args.block_size} "
            f"= {tokens_per_step:,} tok/step · total_steps={total_steps:,} "
            f"· target_tokens={args.target_tokens:,.0f}")
        log(f"[model] params={raw_model.num_params():,} (non-emb {raw_model.num_params(non_embedding=True):,}) "
            f"vocab={cfg.vocab_size} · shards={len(data.arrays)} · "
            f"train_tokens={int(data.lens.sum()):,}")
        log(f"[opt] lr={args.base_lr:.1e} warmup={args.warmup} cosine→{args.min_lr_frac:.0%} "
            f"wd={args.weight_decay} clip={args.grad_clip} bf16 · "
            f"max_minutes={args.max_minutes or '∞'} · notes={args.notes or '-'}")

        run_meta = {
            "run_name": args.run_name, "args": vars(args), "config": asdict(cfg),
            "tokens_per_step": tokens_per_step, "total_steps": total_steps,
            "data_dir": str(args.data_dir), "started": stamp,
            "resumed_from": str(ckpt_path) if ckpt_path else None,
        }
        (out_dir / "run_meta.json").write_text(json.dumps(run_meta, ensure_ascii=False, indent=2),
                                               encoding="utf-8")

        t0 = time.time()
        micro = 0
        running_loss, n_loss = 0.0, 0
        last_log_t, last_log_tokens = t0, tokens_seen
        overhead_s = 0.0        # eval/sample/ckpt 墙钟（纯训练吞吐扣掉它）
        peak_gb = 0.0
        last_eval_step, last_ckpt_step = -1, -1
        last_val = float("nan")
        stop_reason = "completed"

        def do_eval(step: int, lr: float):
            nonlocal overhead_s, peak_gb, last_eval_step, last_val
            if step == last_eval_step:
                return None
            last_eval_step = step
            te = time.time()
            v = estimate_loss(model, val, args.eval_batch_size, device, args.eval_iters)
            last_val = v
            peak_gb = max(peak_gb, torch.cuda.max_memory_allocated() / 2**30)
            log(f"step {step:6d} | [val] loss {v:.4f} | peak {peak_gb:.2f} GB | "
                f"{fmt_dur(time.time() - t0)}")
            csv_w.writerow([step, "", round(v, 4), f"{lr:.3e}", "", tokens_seen,
                            round(time.time() - t0), round(peak_gb, 2)])
            csv_f.flush()
            overhead_s += time.time() - te
            return v

        def do_sample(step: int):
            nonlocal overhead_s
            ts = time.time()
            log(f"step {step:6d} | [sample] " + "-" * 40)
            for prompt in PROMPTS_ZH + PROMPTS_EN:
                txt = sample_text(model, tok, prompt, device, args.sample_tokens)
                log("  " + txt.replace("\n", "\\n "))
            log("  " + "-" * 46)
            overhead_s += time.time() - ts

        def do_ckpt(step: int):
            nonlocal overhead_s, last_ckpt_step
            if step == last_ckpt_step:
                return
            last_ckpt_step = step
            tc = time.time()
            state = {
                "step": step, "config": asdict(cfg), "tokens_seen": tokens_seen,
                "model": raw_model.state_dict(), "optimizer": optimizer.state_dict(),
                "torch_rng": torch.get_rng_state(), "cuda_rng": torch.cuda.get_rng_state(),
                "data_rng": data.rng_state(),
            }
            torch.save(state, out_dir / "last.pt")
            torch.save(state, out_dir / f"ckpt-{step:07d}.pt")
            if args.keep_ckpts > 0:
                kept = sorted(out_dir.glob("ckpt-*.pt"))
                for old in kept[:-args.keep_ckpts]:
                    old.unlink()
            ckpt_gb = sum(p.numel() for p in raw_model.parameters()) * 4 * 3 / 2**30
            log(f"step {step:6d} | [ckpt] ckpt-{step:07d}.pt（≈{ckpt_gb:.2f} GB：fp32 权重+Adam 态）")
            overhead_s += time.time() - tc

        if args.resume and start_step < total_steps:
            do_eval(start_step, lr_at(start_step, args.base_lr, args.warmup, total_steps, args.min_lr_frac))

        model.train()
        step = start_step - 1
        for step in range(start_step, total_steps):
            lr = lr_at(step, args.base_lr, args.warmup, total_steps, args.min_lr_frac)
            for g in optimizer.param_groups:
                g["lr"] = lr
            optimizer.zero_grad(set_to_none=True)
            for _ in range(args.grad_accum):
                x, y = data.batch(args.batch_size, args.block_size, device)
                with torch.autocast("cuda", dtype=torch.bfloat16):
                    _, loss = model(x, y)
                (loss / args.grad_accum).backward()
                tokens_seen += x.numel()
                running_loss += loss.item()
                n_loss += 1
                micro += 1
                # 首步锚：loss 应 ≈ ln(vocab_size)
                if micro == 1:
                    log(f"[anchor] micro-step 1 loss {loss.item():.4f} vs ln(V)={math.log(cfg.vocab_size):.4f} "
                        f"({loss.item() - math.log(cfg.vocab_size):+.3f})")
            torch.nn.utils.clip_grad_norm_(raw_model.parameters(), args.grad_clip)
            optimizer.step()

            done = step + 1
            if done % args.log_every == 0 or step == start_step:
                now = time.time()
                dt = now - last_log_t
                win_tps = (tokens_seen - last_log_tokens) / max(dt, 1e-9)
                elapsed = now - t0
                train_tps = (tokens_seen - start_step * tokens_per_step) / max(elapsed - overhead_s, 1e-9)
                avg = running_loss / max(n_loss, 1)
                eta = (total_steps - done) * tokens_per_step / max(win_tps, 1e-9)
                log(f"step {done:6d} | loss {avg:.4f} | lr {lr:.2e} | {win_tps:,.0f} tok/s "
                    f"(纯训练 {train_tps:,.0f}) | {fmt_dur(elapsed)} | ETA {fmt_dur(eta)}")
                csv_w.writerow([done, round(avg, 4), "", f"{lr:.3e}", round(win_tps),
                                tokens_seen, round(elapsed), round(peak_gb, 2)])
                csv_f.flush()
                running_loss, n_loss = 0.0, 0
                last_log_t, last_log_tokens = now, tokens_seen

            if done % args.eval_every == 0:
                do_eval(done, lr)
            if args.sample_every > 0 and done % args.sample_every == 0:
                do_sample(done)
            if args.ckpt_every > 0 and done % args.ckpt_every == 0:
                do_ckpt(done)

            if args.max_minutes > 0 and (time.time() - t0) > args.max_minutes * 60:
                stop_reason = f"max_minutes({args.max_minutes})"
                log(f"[stop] 达到墙钟预算 {args.max_minutes} min，step {done} 处优雅收尾")
                break

        # ---- 收尾 ----
        final_step = step + 1
        v = do_eval(final_step, lr_at(final_step, args.base_lr, args.warmup, total_steps, args.min_lr_frac))
        if v is None:  # 末步已由 eval_every 评估过（避免重复读数）
            v = last_val
        do_ckpt(final_step)
        elapsed = time.time() - t0
        train_tps = (tokens_seen - start_step * tokens_per_step) / max(elapsed - overhead_s, 1e-9)
        log(f"[final] step {final_step}/{total_steps} | val {v:.4f} | 用时 {fmt_dur(elapsed)} "
            f"(开销 {fmt_dur(overhead_s)}) | 纯训练吞吐 {train_tps:,.0f} tok/s "
            f"| 总 token {tokens_seen:,} | peak {torch.cuda.max_memory_allocated() / 2**30:.2f} GB "
            f"| stop={stop_reason}")
        csv_f.close()
        finish("0", f"step={final_step} val={v:.4f} tps={train_tps:.0f} stop={stop_reason}")
    except Exception:
        err = traceback.format_exc()
        try:
            log("[error]\n" + err)
        finally:
            finish("1", "exception")
        raise


if __name__ == "__main__":
    main()