"""model.py — pretrain-lab 从零手写 decoder-only Transformer（Day 1 · D-02）

全套现代组件（决策 D-02）：
  - RoPE 旋转位置编码（D-05：支持外推；Day 1 字符级 seq=512，主模型 seq=1024）
  - RMSNorm 预归一化（fp32 内计算，数值稳定）
  - SwiGLU 前馈（hidden ≈ 8/3·d，对齐 multiple_of=64）
  - 词嵌入共享 tied embeddings（输入嵌入 = 输出头，省一份 V·d 参数）
参考实现（D-08，只读借鉴不改其档案）：nanoGPT 的块结构骨架 · minimind `model/model_minimind.py` 的组件选型。
本文件为本仓自建；字符级 20M（Day 1）与 140M 主模型（Day 4）共用同一实现，只换 GPTConfig。
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import torch
import torch.nn as nn
import torch.nn.functional as F


# ---------------------------------------------------------------- RoPE ----

def precompute_rope(head_dim: int, max_seq_len: int, base: float = 10000.0):
    """预计算 RoPE 的 cos/sin 表：两个 (max_seq_len, head_dim//2) 的 fp32 张量。

    频率 θ_i = base^(-2i/head_dim)（i = 维度对编号），位置 t 的旋转角 = t·θ_i。
    """
    inv_freq = base ** (-torch.arange(0, head_dim // 2, dtype=torch.float32) * 2.0 / head_dim)
    t = torch.arange(max_seq_len, dtype=torch.float32)
    freqs = torch.outer(t, inv_freq)  # (T, hd/2)
    return freqs.cos(), freqs.sin()


def apply_rope(x: torch.Tensor, cos: torch.Tensor, sin: torch.Tensor) -> torch.Tensor:
    """对 (B, T, H, hd) 的 q/k 施加旋转：前后半（hd/2 与 hd/2）配对。

    (x1, x2) → (x1·cos − x2·sin, x2·cos + x1·sin)，与 RoFormer 论文的复数旋转等价。
    """
    T = x.size(1)
    cos = cos[:T].to(x.dtype).view(1, T, 1, -1)
    sin = sin[:T].to(x.dtype).view(1, T, 1, -1)
    x1, x2 = x.chunk(2, dim=-1)
    return torch.cat([x1 * cos - x2 * sin, x2 * cos + x1 * sin], dim=-1)


# ---------------------------------------------------------------- 组件 ----

class RMSNorm(nn.Module):
    """RMSNorm：只做均方根缩放，不减均值。"""

    def __init__(self, dim: int, eps: float = 1e-6):
        super().__init__()
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(dim))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x_fp32 = x.float()
        xn = x_fp32 * torch.rsqrt(x_fp32.pow(2).mean(-1, keepdim=True) + self.eps)
        return (xn * self.weight).to(x.dtype)


class CausalSelfAttention(nn.Module):
    """多头因果自注意力 + RoPE。无偏置；用 PyTorch SDPA（is_causal=True，走 flash 路径）。"""

    def __init__(self, cfg: "GPTConfig"):
        super().__init__()
        assert cfg.n_embd % cfg.n_head == 0, "n_embd 必须被 n_head 整除"
        self.n_head = cfg.n_head
        self.head_dim = cfg.n_embd // cfg.n_head
        self.qkv = nn.Linear(cfg.n_embd, 3 * cfg.n_embd, bias=False)
        self.proj = nn.Linear(cfg.n_embd, cfg.n_embd, bias=False)

    def forward(self, x: torch.Tensor, rope_cos: torch.Tensor, rope_sin: torch.Tensor) -> torch.Tensor:
        B, T, C = x.shape
        q, k, v = self.qkv(x).split(C, dim=2)
        q = q.view(B, T, self.n_head, self.head_dim)
        k = k.view(B, T, self.n_head, self.head_dim)
        v = v.view(B, T, self.n_head, self.head_dim)
        q = apply_rope(q, rope_cos, rope_sin)
        k = apply_rope(k, rope_cos, rope_sin)
        y = F.scaled_dot_product_attention(
            q.transpose(1, 2), k.transpose(1, 2), v.transpose(1, 2), is_causal=True
        )  # (B, H, T, hd)
        y = y.transpose(1, 2).contiguous().view(B, T, C)
        return self.proj(y)


class SwiGLU(nn.Module):
    """SwiGLU 前馈：down( silu(gate(x)) ⊙ up(x) )。"""

    def __init__(self, cfg: "GPTConfig"):
        super().__init__()
        hidden = int(8 * cfg.n_embd / 3)
        hidden = ((hidden + cfg.multiple_of - 1) // cfg.multiple_of) * cfg.multiple_of
        self.w_gate = nn.Linear(cfg.n_embd, hidden, bias=False)
        self.w_up = nn.Linear(cfg.n_embd, hidden, bias=False)
        self.w_down = nn.Linear(hidden, cfg.n_embd, bias=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.w_down(F.silu(self.w_gate(x)) * self.w_up(x))


class Block(nn.Module):
    """Pre-norm 块：x + attn(norm1(x)) → x + ffn(norm2(x))。"""

    def __init__(self, cfg: "GPTConfig"):
        super().__init__()
        self.norm1 = RMSNorm(cfg.n_embd)
        self.attn = CausalSelfAttention(cfg)
        self.norm2 = RMSNorm(cfg.n_embd)
        self.ffn = SwiGLU(cfg)

    def forward(self, x: torch.Tensor, rope_cos: torch.Tensor, rope_sin: torch.Tensor) -> torch.Tensor:
        x = x + self.attn(self.norm1(x), rope_cos, rope_sin)
        x = x + self.ffn(self.norm2(x))
        return x


# ---------------------------------------------------------------- 主干 ----

@dataclass
class GPTConfig:
    vocab_size: int = 12000
    n_embd: int = 384
    n_layer: int = 10
    n_head: int = 6          # head_dim = 64
    block_size: int = 512    # 训练上下文长度（主模型 D-05 = 1024）
    rope_base: float = 10000.0
    multiple_of: int = 64    # SwiGLU hidden 对齐粒度


class GPT(nn.Module):
    """Decoder-only 主干。RoPE 表按 block_size 预计算为非持久 buffer（不入 checkpoint 权重）。"""

    def __init__(self, cfg: GPTConfig):
        super().__init__()
        self.cfg = cfg
        self.wte = nn.Embedding(cfg.vocab_size, cfg.n_embd)
        self.blocks = nn.ModuleList([Block(cfg) for _ in range(cfg.n_layer)])
        self.norm_f = RMSNorm(cfg.n_embd)
        self.lm_head = nn.Linear(cfg.n_embd, cfg.vocab_size, bias=False)
        self.lm_head.weight = self.wte.weight  # D-02: tied embeddings（同一 Parameter）
        cos, sin = precompute_rope(self.head_dim, cfg.block_size, cfg.rope_base)
        self.register_buffer("rope_cos", cos, persistent=False)
        self.register_buffer("rope_sin", sin, persistent=False)
        self.apply(self._init_weights)
        # 残差路径输出投影（attn.proj / ffn.w_down）按 1/√(2L) 缩放初始化，稳住深块初始前传
        for name, p in self.named_parameters():
            if name.endswith(("attn.proj.weight", "ffn.w_down.weight")):
                nn.init.normal_(p, mean=0.0, std=0.02 / math.sqrt(2 * cfg.n_layer))

    @property
    def head_dim(self) -> int:
        return self.cfg.n_embd // self.cfg.n_head

    def _init_weights(self, m: nn.Module) -> None:
        if isinstance(m, nn.Linear):
            nn.init.normal_(m.weight, mean=0.0, std=0.02)
            if m.bias is not None:
                nn.init.zeros_(m.bias)
        elif isinstance(m, nn.Embedding):
            nn.init.normal_(m.weight, mean=0.0, std=0.02)

    def forward(self, idx: torch.Tensor, targets: torch.Tensor | None = None,
                ignore_index: int = -100):
        """idx (B,T) → logits；给 targets 时返回 CE loss。

        SFT 用 ignore_index=-100 屏蔽非 assistant token（预训练标签不含 -100，行为不变）。
        """
        B, T = idx.shape
        assert T <= self.cfg.block_size, f"序列长 {T} 超过 block_size {self.cfg.block_size}"
        x = self.wte(idx)
        for blk in self.blocks:
            x = blk(x, self.rope_cos, self.rope_sin)
        x = self.norm_f(x)
        if targets is not None:
            logits = self.lm_head(x)
            loss = F.cross_entropy(logits.view(-1, logits.size(-1)), targets.reshape(-1),
                                   ignore_index=ignore_index)
        else:
            logits = self.lm_head(x[:, -1:, :])  # 无 targets 时只需最后一位（generate 用）
            loss = None
        return logits, loss

    @torch.no_grad()
    def generate(self, idx: torch.Tensor, max_new_tokens: int,
                 temperature: float = 1.0, top_k: int | None = None,
                 greedy: bool = False) -> torch.Tensor:
        """从 idx (B,T) 采样续写。无 KV cache（整段重算）；greedy=True 时取 argmax（评测用，可复现）。"""
        self.eval()
        for _ in range(max_new_tokens):
            idx_cond = idx[:, -self.cfg.block_size:]
            logits, _ = self(idx_cond)
            logits = logits[:, -1, :]
            if greedy:
                next_id = logits.argmax(dim=-1, keepdim=True)
                idx = torch.cat([idx, next_id], dim=1)
                continue
            logits = logits / max(temperature, 1e-8)
            if top_k is not None:
                v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                logits[logits < v[:, [-1]]] = -float("inf")
            probs = F.softmax(logits, dim=-1)
            next_id = torch.multinomial(probs, num_samples=1)
            idx = torch.cat([idx, next_id], dim=1)
        return idx

    def num_params(self, non_embedding: bool = False) -> int:
        """参数量；tied embeddings 下 lm_head 与 wte 共用同一 Parameter，天然不重复计。"""
        n = sum(p.numel() for p in self.parameters())
        if non_embedding:
            n -= self.wte.weight.numel()
        return n
