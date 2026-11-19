"""sft.py — Day 4: 全参 SFT 训练脚本（与 train.py 同源，D-10 选 A 手写为主）

与预训练框架的差异（其余全部复用 tools/train.py 的组件与纪律）：
  1) **数据**：`data/sft-mix/{train,val}.bin`（uint16 输入）+ `*.labels.bin`（int16，-100 = 不算 loss）；
     不再"右移一位造标签"，标签由 build_sft.py 生成（assistant-only mask）。
  2) **初始化**：`--init-from out/main140m/last.pt` 载入底座权重（只载 model，不载 optimizer——SFT 重开优化器）；
     `--init-from none` 时随机初始化小模型（管线自检用，不起训练作用）。
  3) **损失**：`F.cross_entropy(..., ignore_index=-100)`；日志同时报"监督 token 占比"。
  4) **采样**：固定 chat 模板 prompt（`<|im_start|>user\\n…<|im_end|>\\n<|im_start|>assistant\\n`），
     解码在 `<|im_end|>` 处截断（`skip_special_tokens=False` 才能看见停止符）。

用法（仓库根目录）：
  # 管线自检（CPU/GPU 均可，随机小模型，2 步）
  .venv-pre/bin/python -I tools/sft.py --init-from none --run-name sft-selftest --max-steps 2 --batch-size 2
  # 正式 SFT（底座 = 主训练终版）
  .venv-pre/bin/python -I tools/sft.py --init-from out/main140m/last.pt --run-name sft-v1 \\
      --batch-size 8 --grad-accum 8 --base-lr 1e-4 --warmup 100 --target-tokens 250e6
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
import torch.nn.functional as F
from tokenizers import Tokenizer

sys.path.insert(0, str(Path(__file__).resolve().parent))

from model import GPT, GPTConfig  # noqa: E402
from lora import adapter_state_dict, apply_lora, merge_lora  # noqa: E402
from train import fmt_dur, lr_at, make_optimizer  # noqa: E402

PROMPTS = [
    "你叫什么名字？",
    "请用一句话解释什么是机器学习。",
    "What is the capital of France?",
]


class SFTPairedData:
    """配对读取：tokens 与 labels 同一偏移（labels 已含 -100 mask）。"""

    def __init__(self, data_dir: Path, block_size: int, seed: int):
        self.x = np.memmap(data_dir / "train.bin", dtype=np.uint16, mode="r")
        self.y = np.memmap(data_dir / "train.labels.bin", dtype=np.int16, mode="r")
        assert len(self.x) == len(self.y), "tokens/labels 长度不一致"
        self.block = block_size
        self.rng = np.random.default_rng(seed)

    def batch(self, bs: int, device: str):
        offs = self.rng.integers(0, len(self.x) - self.block - 1, size=bs)
        xs = np.stack([self.x[o:o + self.block].astype(np.int64) for o in offs])
        ys = np.stack([self.y[o:o + self.block].astype(np.int64) for o in offs])
        return (torch.from_numpy(xs).to(device), torch.from_numpy(ys).to(device))


class FixedSFTVal:
    def __init__(self, data_dir: Path, block_size: int, n_iters: int, bs: int, seed: int):
        self.x = np.memmap(data_dir / "val.bin", dtype=np.uint16, mode="r")
        self.y = np.memmap(data_dir / "val.labels.bin", dtype=np.int16, mode="r")
        self.block = block_size
        n_blocks = max(1, len(self.x) // block_size)
        need = n_iters * bs
        if need > n_blocks:
            raise ValueError(f"val 块不够：需要 {need}，只有 {n_blocks}")
        rng = np.random.default_rng(seed)
        self.offsets = rng.permutation(n_blocks)[:need].reshape(n_iters, bs) * block_size

    def batch(self, it: int, device: str):
        offs = self.offsets[it]
        xs = np.stack([self.x[o:o + self.block].astype(np.int64) for o in offs])
        ys = np.stack([self.y[o:o + self.block].astype(np.int64) for o in offs])
        return (torch.from_numpy(xs).to(device), torch.from_numpy(ys).to(device))


@torch.no_grad()
def estimate_loss(model, val: FixedSFTVal, device: str, n_iters: int) -> float:
    model.eval()
    losses = []
    for it in range(n_iters):
        x, y = val.batch(it, device)
        with torch.autocast("cuda", dtype=torch.bfloat16, enabled=(device == "cuda")):
            _, loss = model(x, y, ignore_index=-100)
        losses.append(loss.item())
    model.train()
    return sum(losses) / len(losses)


@torch.no_grad()
def chat_sample(model, tok: Tokenizer, question: str, device: str,
                max_new: int = 100, temperature: float = 0.7, top_k: int = 50) -> str:
    prompt = f"<|im_start|>user\n{question}<|im_end|>\n<|im_start|>assistant\n"
    ids = tok.encode(prompt, add_special_tokens=False).ids
    idx = torch.tensor([ids], dtype=torch.long, device=device)
    out = model.generate(idx, max_new, temperature=temperature, top_k=top_k)
    text = tok.decode(out[0].tolist(), skip_special_tokens=False)
    model.train()
    return text[len(prompt):].split("<|im_end|>")[0]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-name", default="sft")
    ap.add_argument("--init-from", default="out/main140m/last.pt", help="底座 checkpoint | none")
    ap.add_argument("--data-dir", default="data/sft-mix")
    ap.add_argument("--out-dir", default="")
    ap.add_argument("--log-dir", default="logs")
    ap.add_argument("--tokenizer", default="data/tokenizer-32k/tokenizer.json")
    ap.add_argument("--device", default="cuda")
    # LoRA（0 = 全参 SFT；>0 = 冻结底座，只训低秩增量）
    ap.add_argument("--lora-rank", type=int, default=0)
    ap.add_argument("--lora-alpha", type=float, default=16.0)
    ap.add_argument("--lora-targets", default="attn.qkv,attn.proj,ffn.w_gate,ffn.w_up,ffn.w_down")
    # 随机小模型（--init-from none 时生效，仅管线自检）
    ap.add_argument("--n-embd", type=int, default=128)
    ap.add_argument("--n-layer", type=int, default=2)
    ap.add_argument("--n-head", type=int, default=2)
    # 优化
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--grad-accum", type=int, default=8)
    ap.add_argument("--base-lr", type=float, default=1e-4)
    ap.add_argument("--min-lr-frac", type=float, default=0.1)
    ap.add_argument("--warmup", type=int, default=100)
    ap.add_argument("--weight-decay", type=float, default=0.1)
    ap.add_argument("--grad-clip", type=float, default=1.0)
    ap.add_argument("--target-tokens", type=float, default=250e6)
    ap.add_argument("--max-steps", type=int, default=0)
    ap.add_argument("--max-minutes", type=float, default=0.0)
    # 记录
    ap.add_argument("--log-every", type=int, default=20)
    ap.add_argument("--eval-every", type=int, default=250)
    ap.add_argument("--eval-iters", type=int, default=20)
    ap.add_argument("--eval-batch-size", type=int, default=8)
    ap.add_argument("--sample-every", type=int, default=500)
    ap.add_argument("--sample-tokens", type=int, default=100)
    ap.add_argument("--ckpt-every", type=int, default=250)
    ap.add_argument("--resume", default="")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--notes", default="")
    args = ap.parse_args()
    device = args.device
    assert device == "cpu" or torch.cuda.is_available(), "CUDA 不可用"

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    if device == "cuda":
        torch.backends.cuda.matmul.allow_tf32 = True
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

    if exit_path.exists():
        exit_path.unlink()

    try:
        data_meta = json.loads((Path(args.data_dir) / "meta.json").read_text(encoding="utf-8"))
        block_size = data_meta["block_size"]
        data = SFTPairedData(Path(args.data_dir), block_size, args.seed)
        val = FixedSFTVal(Path(args.data_dir), block_size, args.eval_iters, args.eval_batch_size,
                          args.seed ^ 0x9E3779B9)
        tok = Tokenizer.from_file(args.tokenizer)
        vocab_size = tok.get_vocab_size()

        # ---- 底座 ----
        start_step, tokens_seen = 0, 0
        ckpt_path = None
        if args.init_from.lower() == "none":
            cfg = GPTConfig(vocab_size=vocab_size, n_embd=args.n_embd, n_layer=args.n_layer,
                            n_head=args.n_head, block_size=block_size)
            model = GPT(cfg).to(device)
            log(f"[init] 随机初始化小模型（管线自检用）{asdict(cfg)}")
        else:
            ckpt_path = Path(args.init_from)
            assert ckpt_path.exists(), f"底座 checkpoint 不存在：{ckpt_path}"
            ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
            saved = ckpt["config"]
            cfg = GPTConfig(**{k: saved[k] for k in
                               ("vocab_size", "n_embd", "n_layer", "n_head", "block_size",
                                "rope_base", "multiple_of") if k in saved})
            assert cfg.vocab_size == vocab_size, f"底座词表 {cfg.vocab_size} ≠ 数据词表 {vocab_size}"
            assert cfg.block_size == block_size, f"底座 seq {cfg.block_size} ≠ 数据块 {block_size}"
            model = GPT(cfg).to(device)
            model.load_state_dict(ckpt["model"])
            log(f"[init] 底座 {ckpt_path}（step={ckpt.get('step')}）→ SFT 重新开优化器")

        lora_info = None
        if args.lora_rank > 0:
            targets = tuple(s.strip() for s in args.lora_targets.split(",") if s.strip())
            lora_info = apply_lora(model, args.lora_rank, args.lora_alpha, targets)
            log(f"[lora] r={lora_info['rank']} alpha={lora_info['alpha']:.0f} "
                f"scaling={lora_info['scaling']:.2f} targets={','.join(lora_info['targets'])} "
                f"replaced={len(lora_info['replaced'])}")
            log(f"[lora] trainable {lora_info['trainable']:,} / {lora_info['total']:,} "
                f"= {lora_info['ratio']:.2%}")

        if args.resume:
            rp = out_dir / "last.pt" if args.resume == "auto" else Path(args.resume)
            rck = torch.load(rp, map_location=device, weights_only=False)
            model.load_state_dict(rck["model"])
            start_step = rck["step"]
            tokens_seen = rck.get("tokens_seen", 0)
            log(f"[resume] {rp} → step={start_step} tokens_seen={tokens_seen:,}")

        optimizer = make_optimizer(model, args.base_lr, args.weight_decay)
        if args.resume and "optimizer" in rck:
            optimizer.load_state_dict(rck["optimizer"])

        tokens_per_step = args.batch_size * block_size * args.grad_accum
        total_steps = args.max_steps if args.max_steps > 0 else math.ceil(args.target_tokens / tokens_per_step)

        csv_f = csv_path.open("a", newline="")
        csv_w = csv.writer(csv_f)
        if csv_path.stat().st_size == 0:
            csv_w.writerow(["step", "train_loss", "val_loss", "lr", "tok_per_s",
                            "tokens_seen", "elapsed_s", "peak_gb"])
        log(f"[cfg] {json.dumps(asdict(cfg))} bs={args.batch_size}×accum{args.grad_accum}"
            f"×T{block_size} = {tokens_per_step:,} tok/step · total_steps={total_steps:,}")
        log(f"[data] {args.data_dir} train={data_meta['train']['tokens']:,} tok "
            f"（监督占比 {data_meta['train']['supervised_ratio']:.2%}，预训练混入 "
            f"{data_meta['pretrain_mix']['ratio_blocks']:.0%}）· val={data_meta['val']['tokens']:,}")
        log(f"[opt] lr={args.base_lr:.1e} warmup={args.warmup} cosine→{args.min_lr_frac:.0%} "
            f"ignore_index=-100 · notes={args.notes or '-'}")

        t0 = time.time()
        running_loss, n_loss = 0.0, 0
        last_log_t, last_log_tokens = t0, tokens_seen
        overhead_s = 0.0
        peak_gb = 0.0
        stop_reason = "completed"

        def do_eval(step: int, lr: float):
            nonlocal overhead_s, peak_gb
            te = time.time()
            v = estimate_loss(model, val, device, args.eval_iters)
            if device == "cuda":
                peak_gb = max(peak_gb, torch.cuda.max_memory_allocated() / 2**30)
            log(f"step {step:6d} | [val] loss {v:.4f} | peak {peak_gb:.2f} GB | {fmt_dur(time.time() - t0)}")
            csv_w.writerow([step, "", round(v, 4), f"{lr:.3e}", "", tokens_seen,
                            round(time.time() - t0), round(peak_gb, 2)])
            csv_f.flush()
            overhead_s += time.time() - te
            return v

        def do_sample(step: int):
            nonlocal overhead_s
            ts = time.time()
            log(f"step {step:6d} | [chat] " + "-" * 40)
            for q in PROMPTS:
                log(f"  Q: {q}\n  A: {chat_sample(model, tok, q, device, args.sample_tokens).strip()}")
            log("  " + "-" * 46)
            overhead_s += time.time() - ts

        def do_ckpt(step: int):
            nonlocal overhead_s
            tc = time.time()
            torch.save({"step": step, "config": asdict(cfg), "tokens_seen": tokens_seen,
                        "model": model.state_dict(), "optimizer": optimizer.state_dict(),
                        "data": {"dir": args.data_dir, "meta": data_meta},
                        "init_from": args.init_from, "lora": lora_info}, out_dir / "last.pt")
            log(f"step {step:6d} | [ckpt] last.pt")
            overhead_s += time.time() - tc

        if args.resume:
            do_eval(start_step, lr_at(start_step, args.base_lr, args.warmup, total_steps, args.min_lr_frac))

        model.train()
        step = start_step - 1
        for step in range(start_step, total_steps):
            lr = lr_at(step, args.base_lr, args.warmup, total_steps, args.min_lr_frac)
            for g in optimizer.param_groups:
                g["lr"] = lr
            optimizer.zero_grad(set_to_none=True)
            for _ in range(args.grad_accum):
                x, y = data.batch(args.batch_size, device)
                with torch.autocast("cuda", dtype=torch.bfloat16, enabled=(device == "cuda")):
                    _, loss = model(x, y, ignore_index=-100)
                (loss / args.grad_accum).backward()
                tokens_seen += x.numel()
                running_loss += loss.item()
                n_loss += 1
                if step == start_step and n_loss == 1:
                    sup = float((y != -100).float().mean())
                    log(f"[anchor] micro-step 1 loss {loss.item():.4f} | 监督占比 {sup:.2%} "
                        f"| 随机基线 ln(V)={math.log(cfg.vocab_size):.4f}")
            torch.nn.utils.clip_grad_norm_(model.parameters(), args.grad_clip)
            optimizer.step()

            done = step + 1
            if done % args.log_every == 0 or step == start_step:
                now = time.time()
                win_tps = (tokens_seen - last_log_tokens) / max(now - last_log_t, 1e-9)
                elapsed = now - t0
                train_tps = (tokens_seen - start_step * tokens_per_step) / max(elapsed - overhead_s, 1e-9)
                log(f"step {done:6d} | loss {running_loss / max(n_loss, 1):.4f} | lr {lr:.2e} "
                    f"| {win_tps:,.0f} tok/s (纯训练 {train_tps:,.0f}) | {fmt_dur(elapsed)}")
                csv_w.writerow([done, round(running_loss / max(n_loss, 1), 4), "", f"{lr:.3e}",
                                round(win_tps), tokens_seen, round(elapsed), round(peak_gb, 2)])
                csv_f.flush()
                running_loss, n_loss = 0.0, 0
                last_log_t, last_log_tokens = now, tokens_seen
            if args.eval_every > 0 and done % args.eval_every == 0:
                do_eval(done, lr)
            if args.sample_every > 0 and done % args.sample_every == 0:
                do_sample(done)
            if args.ckpt_every > 0 and done % args.ckpt_every == 0:
                do_ckpt(done)
            if args.max_minutes > 0 and (time.time() - t0) > args.max_minutes * 60:
                stop_reason = f"max_minutes({args.max_minutes})"
                log(f"[stop] 达到墙钟预算，step {done} 处收尾")
                break

        final_step = step + 1
        v = do_eval(final_step, lr_at(final_step, args.base_lr, args.warmup, total_steps, args.min_lr_frac))
        do_ckpt(final_step)
        if lora_info:
            ap_path = out_dir / "adapter.pt"
            torch.save({"lora": adapter_state_dict(model), "info": lora_info}, ap_path)
            log(f"[lora] adapter → {ap_path}")
            n_merged = merge_lora(model)
            torch.save({"step": final_step, "config": asdict(cfg), "tokens_seen": tokens_seen,
                        "model": model.state_dict(), "init_from": args.init_from,
                        "lora": lora_info, "lora_merged": True}, out_dir / "last.pt")
            log(f"[lora] merged {n_merged} layers → {out_dir / 'last.pt'}（eval/deploy 用）")
        elapsed = time.time() - t0
        train_tps = (tokens_seen - start_step * tokens_per_step) / max(elapsed - overhead_s, 1e-9)
        log(f"[final] step {final_step}/{total_steps} | val {v:.4f} | 用时 {fmt_dur(elapsed)} "
            f"| 纯训练 {train_tps:,.0f} tok/s | peak {peak_gb:.2f} GB | stop={stop_reason}")
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