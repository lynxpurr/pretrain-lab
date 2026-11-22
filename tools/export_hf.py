"""export_hf.py — Day 7: 把本仓 GPT checkpoint 导出为 HF Llama 格式（供 Ollama/llama.cpp 转换）

本仓模型是 Llama 同构（RoPE + RMSNorm + SwiGLU + tied embeddings），只是参数名不同：
  wte.weight                  → model.embed_tokens.weight
  blocks.N.attn.qkv.weight    → q/k/v_proj.weight（按输出维三等分）
  blocks.N.attn.proj.weight   → o_proj.weight
  blocks.N.ffn.w_gate/w_up/w_down → mlp.gate_proj/up_proj/down_proj.weight
  blocks.N.norm1/norm2.weight → input_layernorm/post_attention_layernorm.weight
  norm_f.weight               → model.norm.weight
  lm_head.weight              → lm_head.weight（tied，数值同 embed_tokens）

输出目录（`out/hf-<name>/`）：config.json · model.safetensors · tokenizer.json ·
tokenizer_config.json · special_tokens_map.json · generation_config.json

用法：
  .venv-pre/bin/python -I tools/export_hf.py --ckpt out/sft-v1/last.pt --out-dir out/hf-sft-v1
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import torch
from safetensors.torch import save_file

sys.path.insert(0, str(Path(__file__).resolve().parent))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default="out/sft-v1/last.pt")
    ap.add_argument("--out-dir", default="out/hf-sft-v1")
    ap.add_argument("--tokenizer", default="data/tokenizer-32k/tokenizer.json")
    ap.add_argument("--name", default="ZhenLM-140M")
    ap.add_argument("--dtype", choices=["fp32", "fp16", "bf16"], default="fp32",
                    help="safetensors dtype (fp16 is recommended for release)")
    ap.add_argument("--tie-embeddings", action="store_true",
                    help="omit lm_head.weight and set tie_word_embeddings=True (smaller file)")
    args = ap.parse_args()

    dtype_map = {"fp32": torch.float32, "fp16": torch.float16, "bf16": torch.bfloat16}
    dtype = dtype_map[args.dtype]

    ck = torch.load(args.ckpt, map_location="cpu", weights_only=False)
    cfg = ck["config"]
    sd = ck["model"]
    d = cfg["n_embd"]
    L = cfg["n_layer"]
    assert d == 768 and L == 16, f"预期 140M 配置，得到 d={d} L={L}"

    tensors: dict[str, torch.Tensor] = {
        "model.embed_tokens.weight": sd["wte.weight"].contiguous(),
    }
    for i in range(L):
        qkv = sd[f"blocks.{i}.attn.qkv.weight"]
        q, k, v = qkv.split(d, dim=0)
        tensors[f"model.layers.{i}.self_attn.q_proj.weight"] = q.contiguous()
        tensors[f"model.layers.{i}.self_attn.k_proj.weight"] = k.contiguous()
        tensors[f"model.layers.{i}.self_attn.v_proj.weight"] = v.contiguous()
        tensors[f"model.layers.{i}.self_attn.o_proj.weight"] = sd[f"blocks.{i}.attn.proj.weight"].contiguous()
        tensors[f"model.layers.{i}.mlp.gate_proj.weight"] = sd[f"blocks.{i}.ffn.w_gate.weight"].contiguous()
        tensors[f"model.layers.{i}.mlp.up_proj.weight"] = sd[f"blocks.{i}.ffn.w_up.weight"].contiguous()
        tensors[f"model.layers.{i}.mlp.down_proj.weight"] = sd[f"blocks.{i}.ffn.w_down.weight"].contiguous()
        tensors[f"model.layers.{i}.input_layernorm.weight"] = sd[f"blocks.{i}.norm1.weight"].contiguous()
        tensors[f"model.layers.{i}.post_attention_layernorm.weight"] = sd[f"blocks.{i}.norm2.weight"].contiguous()
    tensors["model.norm.weight"] = sd["norm_f.weight"].contiguous()
    # 本仓 tied embedding：默认 clone 一份作为独立 lm_head（数值相同，推理等价），
    # 避免 safetensors 拒绝共享内存，也兼容只认 output.weight 的转换器。
    # --tie-embeddings 则省略 lm_head 并让 HF 在加载时绑定（文件更小，参数量准确）。
    if not args.tie_embeddings:
        tensors["lm_head.weight"] = sd["lm_head.weight"].clone().contiguous()

    # Cast once, after all tensors are collected (safetensors rejects shared
    # memory, so the clone above is also required for tied embeddings).
    tensors = {k: v.to(dtype).contiguous() for k, v in tensors.items()}

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    save_file(tensors, out / "model.safetensors", metadata={"format": "pt"})
    shutil.copyfile(args.tokenizer, out / "tokenizer.json")

    config = {
        "architectures": ["LlamaForCausalLM"],
        "model_type": "llama",
        "vocab_size": cfg["vocab_size"],
        "hidden_size": d,
        "intermediate_size": sd["blocks.0.ffn.w_gate.weight"].shape[0],
        "num_hidden_layers": L,
        "num_attention_heads": cfg["n_head"],
        "num_key_value_heads": cfg["n_head"],
        "head_dim": d // cfg["n_head"],
        "max_position_embeddings": cfg["block_size"],
        "rms_norm_eps": 1e-6,
        "rope_theta": cfg["rope_base"],
        "hidden_act": "silu",
        "tie_word_embeddings": bool(args.tie_embeddings),
        "torch_dtype": {"fp32": "float32", "fp16": "float16", "bf16": "bfloat16"}[args.dtype],
        "use_cache": True,
        "attention_bias": False,
        "bos_token_id": 0,
        "eos_token_id": 0,
        "pad_token_id": 0,
    }
    (out / "config.json").write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")

    tokenizer_config = {
        "tokenizer_class": "PreTrainedTokenizerFast",
        "bos_token": "<|endoftext|>",
        "eos_token": "<|endoftext|>",
        "unk_token": "<|endoftext|>",
        "pad_token": "<|endoftext|>",
        "add_bos_token": False,
        "add_eos_token": False,
        "clean_up_tokenization_spaces": False,
        "chat_template": ("{% for message in messages %}<|im_start|>{{ message['role'] }}\n"
                          "{{ message['content'] }}<|im_end|>\n{% endfor %}"
                          "{% if add_generation_prompt %}<|im_start|>assistant\n{% endif %}"),
    }
    (out / "tokenizer_config.json").write_text(
        json.dumps(tokenizer_config, ensure_ascii=False, indent=2), encoding="utf-8")
    special_map = {
        "bos_token": "<|endoftext|>", "eos_token": "<|endoftext|>",
        "unk_token": "<|endoftext|>", "pad_token": "<|endoftext|>",
        "additional_special_tokens": ["<|im_start|>", "<|im_end|>"],
    }
    (out / "special_tokens_map.json").write_text(
        json.dumps(special_map, ensure_ascii=False, indent=2), encoding="utf-8")
    gen_config = {
        "bos_token_id": 0, "eos_token_id": 0, "pad_token_id": 0,
        "max_new_tokens": 200, "do_sample": True, "temperature": 0.3, "top_p": 0.9,
        "repetition_penalty": 1.0,
    }
    (out / "generation_config.json").write_text(
        json.dumps(gen_config, ensure_ascii=False, indent=2), encoding="utf-8")

    n_params = sum(t.numel() for t in tensors.values())
    size_mb = (out / "model.safetensors").stat().st_size / 2**20
    print(f"[done] {out}/ · {len(tensors)} tensors · {n_params:,} params · "
          f"{size_mb:.1f} MB ({args.dtype})", flush=True)


if __name__ == "__main__":
    main()