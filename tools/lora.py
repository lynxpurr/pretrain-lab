"""lora.py — Day 7: LoRA 低秩增量（D-10 选 A：手写为主）

实现方式：把目标 `nn.Linear` 包成 `LoRALinear`（base 权重冻结 + 低秩 A/B 可训练），
训练结束后 `merge_lora` 把 `B·A·scaling` 加回 base 权重并替换回普通 Linear，
这样 `last.pt` 的 state_dict 键与底座完全一致，`tools/eval.py` / GGUF 导出无需改代码。

默认目标 = qkv / proj / gate / up / down（覆盖注意力和 FFN 的全部线性层）；
r=8 / alpha=16 → 可训练参数 ≈1.21%（<2%，Day 7 判据）。
"""
from __future__ import annotations

import math

import torch
import torch.nn as nn
import torch.nn.functional as F

DEFAULT_TARGETS = ("attn.qkv", "attn.proj", "ffn.w_gate", "ffn.w_up", "ffn.w_down")


class LoRALinear(nn.Module):
    """base(x) + scaling · B(A(x))；A ~ kaiming，B=0 → 初始增量恒为 0。"""

    def __init__(self, base: nn.Linear, rank: int, alpha: float):
        super().__init__()
        assert rank > 0 and base.weight.dim() == 2
        self.base = base
        for p in self.base.parameters():
            p.requires_grad = False
        self.rank = rank
        self.scaling = alpha / rank
        # 必须建在 base 权重的 device/dtype 上：apply_lora 在 model.to(cuda) 之后调用，
        # 默认 CPU 会让 F.linear 的 mat2 与激活 device 不一致（Day 7 冒烟实测）。
        self.lora_A = nn.Parameter(torch.empty(rank, base.in_features,
                                               device=base.weight.device, dtype=base.weight.dtype))
        self.lora_B = nn.Parameter(torch.zeros(base.out_features, rank,
                                               device=base.weight.device, dtype=base.weight.dtype))
        nn.init.kaiming_uniform_(self.lora_A, a=math.sqrt(5))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = self.base(x)
        delta = F.linear(F.linear(x, self.lora_A), self.lora_B) * self.scaling
        return out + delta

    @torch.no_grad()
    def merged_weight(self) -> torch.Tensor:
        return self.base.weight.data + (self.lora_B.data @ self.lora_A.data) * self.scaling

    @torch.no_grad()
    def merge(self) -> nn.Linear:
        self.base.weight.data.copy_(self.merged_weight())
        return self.base


def apply_lora(model: nn.Module, rank: int, alpha: float,
               targets: tuple[str, ...] = DEFAULT_TARGETS) -> dict:
    """冻结全部底座参数，把命中的 Linear 换成 LoRALinear；返回读数。"""
    for p in model.parameters():
        p.requires_grad = False
    replaced: list[str] = []
    for name, module in list(model.named_modules()):
        if not isinstance(module, nn.Linear):
            continue
        if not any(name == t or name.endswith("." + t) for t in targets):
            continue
        parent_name, _, child_name = name.rpartition(".")
        parent = model.get_submodule(parent_name) if parent_name else model
        setattr(parent, child_name, LoRALinear(module, rank, alpha))
        replaced.append(name)
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    return {"rank": rank, "alpha": alpha, "scaling": alpha / rank,
            "targets": list(targets), "replaced": replaced,
            "trainable": trainable, "total": total,
            "ratio": round(trainable / max(total, 1), 6)}


@torch.no_grad()
def merge_lora(model: nn.Module) -> int:
    """把所有 LoRALinear 的增量合并回 base，并替换回普通 Linear；返回合并层数。"""
    count = 0
    for name, module in list(model.named_modules()):
        if not isinstance(module, LoRALinear):
            continue
        parent_name, _, child_name = name.rpartition(".")
        parent = model.get_submodule(parent_name) if parent_name else model
        setattr(parent, child_name, module.merge())
        count += 1
    return count


def adapter_state_dict(model: nn.Module) -> dict:
    """只取 LoRA 参数（lora_A/lora_B），供单独存档/分析。"""
    return {k: v.detach().cpu() for k, v in model.state_dict().items()
            if ".lora_A" in k or ".lora_B" in k}