"""export_gguf.py — Day 7: 把本仓 checkpoint 直接导出为 llama.cpp GGUF（F16/F32）

为什么不用 HF 转换脚本：本仓模型是 Llama 同构但参数名自建；这里直接把
`wte / qkv / proj / gate / up / down / norms / lm_head` 映射成 GGUF 的 Llama
张量名（token_embd / blk.N.attn_q… / output 等），tokenizer 从
`data/tokenizer-32k/tokenizer.json` 的 BPE vocab+merges 写入（model=gpt2）。

用法：
  .venv-pre/bin/python -I tools/export_gguf.py --ckpt out/sft-v2/last.pt \
      --out out/gguf/pretrain-lab-140m-sft-v2-f16.gguf --name pretrain-lab-140m-sft-v2
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gguf import GGMLQuantizationType, GGUFWriter, TokenType  # noqa: E402

CHAT_TEMPLATE = ("{% for message in messages %}<|im_start|>{{ message['role'] }}\n"
                 "{{ message['content'] }}<|im_end|>\n{% endfor %}"
                 "{% if add_generation_prompt %}<|im_start|>assistant\n{% endif %}")


def permute_qk(w: torch.Tensor, n_head: int, head_dim: int) -> torch.Tensor:
    """与 llama.cpp convert_hf_to_gguf.py 的 LlamaModel.permute 同款：
    q/k 权重按 head 重排 [n_head, 2, head_dim/2, in] → swapaxes(1,2) → 还原。
    不做这一步，llama.cpp 的 RoPE 会看到错位的 q/k（症状 = 前几个词正常、随后复读）。"""
    out_dim, in_dim = w.shape
    assert out_dim == n_head * head_dim, (out_dim, n_head, head_dim)
    return (w.reshape(n_head, 2, head_dim // 2, in_dim)
             .swapaxes(1, 2)
             .reshape(out_dim, in_dim)
             .contiguous())


def load_tokenizer_meta(path: Path) -> tuple[list[str], list[str], list[int]]:
    t = json.loads(path.read_text(encoding="utf-8"))
    vocab = t["model"]["vocab"]
    n = max(vocab.values()) + 1
    tokens = [None] * n
    for tok, idx in vocab.items():
        tokens[idx] = tok
    assert all(x is not None for x in tokens), "vocab id 不连续"
    merges = [" ".join(pair) for pair in t["model"]["merges"]]
    types = [int(TokenType.NORMAL)] * n
    for a in t.get("added_tokens", []):
        if a.get("special"):
            types[a["id"]] = int(TokenType.CONTROL)
    return tokens, merges, types


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default="out/sft-v2/last.pt")
    ap.add_argument("--out", default="out/gguf/pretrain-lab-140m-sft-v2-f16.gguf")
    ap.add_argument("--name", default="pretrain-lab-140m-sft-v2")
    ap.add_argument("--tokenizer", default="data/tokenizer-32k/tokenizer.json")
    ap.add_argument("--dtype", choices=["f16", "f32"], default="f16")
    args = ap.parse_args()

    ck = torch.load(args.ckpt, map_location="cpu", weights_only=False)
    cfg = ck["config"]
    sd = ck["model"]
    d, L, H = cfg["n_embd"], cfg["n_layer"], cfg["n_head"]
    ffn = sd["blocks.0.ffn.w_gate.weight"].shape[0]
    V = cfg["vocab_size"]
    assert (d, L, H, ffn, V) == (768, 16, 12, 2048, 32000), (d, L, H, ffn, V)

    tokens, merges, types = load_tokenizer_meta(Path(args.tokenizer))
    assert len(tokens) == V, (len(tokens), V)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    w = GGUFWriter(str(out), arch="llama")
    w.add_name(args.name)
    w.add_context_length(cfg["block_size"])
    w.add_embedding_length(d)
    w.add_block_count(L)
    w.add_feed_forward_length(ffn)
    w.add_head_count(H)
    w.add_head_count_kv(H)
    w.add_rope_dimension_count(d // H)
    w.add_rope_freq_base(float(cfg["rope_base"]))
    w.add_layer_norm_rms_eps(1e-6)
    w.add_vocab_size(V)
    w.add_file_type(1 if args.dtype == "f16" else 0)
    w.add_tokenizer_model("gpt2")
    w.add_tokenizer_pre("gpt-2")
    w.add_token_list(tokens)
    w.add_token_merges(merges)
    w.add_token_types(types)
    w.add_bos_token_id(0)
    w.add_eos_token_id(0)
    w.add_pad_token_id(0)
    w.add_unk_token_id(0)
    w.add_add_bos_token(False)
    w.add_add_eos_token(False)
    w.add_add_space_prefix(False)
    w.add_chat_template(CHAT_TEMPLATE)

    qt = GGMLQuantizationType.F16 if args.dtype == "f16" else GGMLQuantizationType.F32

    def put(name: str, tensor: torch.Tensor, quant=qt) -> None:
        arr = tensor.detach().to(torch.float32).numpy().astype(np.float32, copy=False)
        if quant == GGMLQuantizationType.F16:
            arr = arr.astype(np.float16).view(np.uint16)  # gguf 的 F16 以 uint16 存储
        w.add_tensor(name, arr, raw_dtype=quant)

    put("token_embd.weight", sd["wte.weight"])
    for i in range(L):
        qkv = sd[f"blocks.{i}.attn.qkv.weight"]
        q, k, v = qkv.split(d, dim=0)
        put(f"blk.{i}.attn_q.weight", permute_qk(q, H, d // H))
        put(f"blk.{i}.attn_k.weight", permute_qk(k, H, d // H))
        put(f"blk.{i}.attn_v.weight", v)
        put(f"blk.{i}.attn_output.weight", sd[f"blocks.{i}.attn.proj.weight"])
        put(f"blk.{i}.ffn_gate.weight", sd[f"blocks.{i}.ffn.w_gate.weight"])
        put(f"blk.{i}.ffn_up.weight", sd[f"blocks.{i}.ffn.w_up.weight"])
        put(f"blk.{i}.ffn_down.weight", sd[f"blocks.{i}.ffn.w_down.weight"])
        put(f"blk.{i}.attn_norm.weight", sd[f"blocks.{i}.norm1.weight"], GGMLQuantizationType.F32)
        put(f"blk.{i}.ffn_norm.weight", sd[f"blocks.{i}.norm2.weight"], GGMLQuantizationType.F32)
    put("output_norm.weight", sd["norm_f.weight"], GGMLQuantizationType.F32)
    put("output.weight", sd["lm_head.weight"])

    w.write_header_to_file()
    w.write_kv_data_to_file()
    w.write_tensors_to_file()
    w.close()
    size_gb = out.stat().st_size / 2**30
    print(f"[done] {out} · {L*9+3} tensors · {size_gb:.2f} GB · dtype={args.dtype}", flush=True)


if __name__ == "__main__":
    main()