# Release model export — v2e HF fp16 + standalone Q8_0 GGUF（2026-11-21）

> 目的：为公开发布准备两个可直接分发的模型产物——①Hugging Face `transformers` 可加载的 fp16 权重；②独立 Q8_0 GGUF 文件（部署默认）。本文记录导出参数、SHA256、以及"PyTorch vs HF vs Ollama"三链路对拍结果。
> 不改变部署 tag（`pretrain-lab-sft-v2e-q8` 保留）；不修改任何历史读数。

## 1. 产物与指纹

| 产物 | 路径 | 大小 | SHA256 |
|---|---|---|---|
| HF fp16 权重 | `out/hf-sft-v2e/model.safetensors` | 275,711,304 B（262.9 MiB） | `7d1c2f0c4657c2a232d0db76a1d6e82af0dfb9c380631480a774ccff3c496de2` |
| HF config | `out/hf-sft-v2e/config.json` | 532 B | `349dda627876cb2fa7af0ecbc63dcee14135db5343fa4c2f4198b3bc6d30cc1b` |
| GGUF F16 | `out/gguf/pretrain-lab-140m-sft-v2e-f16.gguf` | 326,240,864 B（326 MB） | `eee108223b9c027840f16c657807f1b3d38981888e38f67a20058b603e068dfc` |
| **GGUF Q8_0** | `out/gguf/pretrain-lab-140m-sft-v2e-Q8_0.gguf` | 173,992,608 B（174 MB） | `8b64b66898eef9f5ed4815ad41cadacabc49799b950e9360863798ac5fd16fd5` |

Q8_0 文件来源：Ollama 用户级模型 `pretrain-lab-sft-v2e-q8` 的 blob
`~/.ollama/models/blobs/sha256-8b64b668...`（内容寻址，复制后 sha 不变）。

## 2. HF 导出

```bash
.venv-pre/bin/python -I tools/export_hf.py \
  --ckpt out/sft-v2e/last.pt \
  --out-dir out/hf-sft-v2e \
  --name pretrain-lab-140m-sft-v2e \
  --dtype fp16 --tie-embeddings
```

- **参数**：137,847,552（`--tie-embeddings` 省略独立 `lm_head.weight`，由 HF 在加载时绑定；若不省略则为 162,423,552 存储参数，推理等价但文件大 49MB）。
- **config**：`LlamaForCausalLM` · vocab 32,000 · hidden 768 · 16 层 · 12 头 · head_dim 64 · intermediate 2048 · context 1024 · `rope_theta` 10000 · `tie_word_embeddings: true` · `torch_dtype: float16`。
- **tokenizer**：`data/tokenizer-32k/tokenizer.json` + `tokenizer_config.json`（含 chat_template：`<|im_start|>{role}\n{content}<|im_end|>\n`；generation prompt `<|im_start|>assistant\n`）。
- **generation_config**：`max_new_tokens 200 · do_sample true · temperature 0.3 · top_p 0.9`（与 demo 默认一致；评测仍用 greedy）。

## 3. 三链路对拍（同 prompt / greedy / 同 tokenizer）

Prompt：

```
<|im_start|>user
你好，请介绍一下你自己。<|im_end|>
<|im_start|>assistant
```

| 链路 | 生成 token（前 15 个） | 与 PyTorch 一致 |
|---|---|---|
| PyTorch `out/sft-v2e/last.pt`（fp32） | `[5425, 1315, 10180, 3534, 368, 913, 267, 423, 1169, 1721, 30463, 4467, 10846, 8742, 267]` | — |
| HF `out/hf-sft-v2e-fp32`（untied） | 同上 | **30/30 ✅** |
| HF `out/hf-sft-v2e`（fp16, tied） | 同上 | **30/30 ✅** |

生成文本（HF fp16）：`你好！我是minimind，一个由个人开发者开发的智能助手，我擅长通过思考来帮您解答复杂的数学，代码和逻辑推理等理…`

结论：HF 导出的 RoPE/权重布局与自研模型一致（无需 q/k permute）；fp16 在该 greedy 短程对拍中与 fp32 逐 token 相同。

## 4. Q8_0 GGUF 校验

`gguf.GGUFReader` 读数：

| 字段 | 值 |
|---|---|
| magic | `GGUF` |
| `general.architecture` | `llama` |
| `general.name` | `pretrain-lab-140m-sft-v2e` |
| `general.file_type` | `7`（Q8_0） |
| `general.quantization_version` | `2` |
| `llama.block_count` | `16` |
| `llama.embedding_length` | `768` |
| tensors | 147（114 × Q8_0 + 33 × F32） |

Ollama 从独立文件建模型：

```bash
OLLAMA_HOST=127.0.0.1:11435 ollama create pretrain-lab-sft-v2e-q8-file \
  -f out/Modelfile-sft-v2e-q8
```

对拍（同 prompt / temperature 0）：

| 模型 | 输出 |
|---|---|
| `pretrain-lab-sft-v2e-q8-file`（Q8 文件） | `I love machine learning.` |
| `pretrain-lab-sft-v2e-q8`（已部署 tag） | `I love machine learning.` |

**逐字一致** → 独立 Q8 文件可作为发布资产，且与部署 tag 等价。

## 5. 发布建议

- **HF 权重**：上传 `out/hf-sft-v2e/`（README.md = 英文模型卡、LICENSE、NOTICE、DATA_LICENSE.md、config/tokenizer/generation_config/model.safetensors）。
- **GGUF 仓库**：上传 `pretrain-lab-140m-sft-v2e-Q8_0.gguf` + `Modelfile-sft-v2e-q8`；F16 可选。
- **不要**默认发布 Q4_K_M（v2e 上不保真：math 42→72 / translate 回退）。
- `.pt` 原始 checkpoint（1.65GB）建议一并上传（供 `eval.py` 复现评测）；若空间受限，至少在 model card 说明如何获取。

## 6. 复现命令

```bash
# HF fp16
.venv-pre/bin/python -I tools/export_hf.py --ckpt out/sft-v2e/last.pt \
  --out-dir out/hf-sft-v2e --dtype fp16 --tie-embeddings

# Q8 文件（若已有 Ollama Q8 tag，可直接复制内容寻址 blob；否则从 F16 量化）
cp ~/.ollama/models/blobs/sha256-8b64b66898eef9f5ed4815ad41cadacabc49799b950e9360863798ac5fd16fd5 \
  out/gguf/pretrain-lab-140m-sft-v2e-Q8_0.gguf

# 校验
.venv-pre/bin/python -I - <<'PY'
from gguf import GGUFReader
r = GGUFReader("out/gguf/pretrain-lab-140m-sft-v2e-Q8_0.gguf")
print(r.fields["general.file_type"].contents())  # 7 = Q8_0
print(len(r.tensors))
PY
```

## 7. 结论

- HF fp16（tied）与 PyTorch greedy **30/30 逐 token 一致**；Q8 文件与部署 tag **逐字一致**。
- 发布产物已具备：HF 权重 263MB / Q8 GGUF 174MB / F16 GGUF 326MB；SHA256 已录。
- 未做公网上传（Phase 3 需用户确认与凭据）。