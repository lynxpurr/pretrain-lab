# pretrain-lab

**ZhenLM-140M——一张 16GB 显卡从零训出的 137.8M 参数中英小模型。**

这不是一个要和开源大模型竞争的模型，而是一条完整、可复现的训练流程：
tokenizer → 3B token 预训练 → 六版 SFT → LoRA 消融 → GGUF/Ollama 部署，
每一步的证据都在 [`reports/`](reports/)。评测部分记录了训练集污染、去重检查器
假阴性的修复、90 题 holdout、47 题第二复核，以及数学/翻译的失败模式。

**命名**：**ZhenLM**（真）是模型家族；"140M" 是家族标签（精确参数
137,847,552）；部署变体为 **SFT v2e**。本仓库是 `pretrain-lab` 项目。

- **模型**：**ZhenLM-140M** · 137,847,552 参数 · d_model 768 · 16 层 · 12 头 · RoPE + RMSNorm + SwiGLU + tied embeddings · 32k BPE · 上下文 1024
- **预训练**：3.0B token（英文 60% FineWeb-Edu / 中文 40% minimind）· 16h07m41s · val **2.7709**
- **SFT**：250M token，assistant-only mask，六版 · 部署 **ZhenLM-140M-SFT-v2e**（val 1.6065，rep-4 **0.055**）
- **硬件**：单卡 RTX 5070 Ti 16GB · 全本地
- **部署**：Q8_0 GGUF（174 MB）→ Ollama（`zhenlm-140m-sft-v2e-q8`）→ 零依赖本地聊天页

## 快速开始

权重与 GGUF：[`lynxpurr/ZhenLM-140M-SFT-v2e`](https://huggingface.co/lynxpurr/ZhenLM-140M-SFT-v2e) ·
[`...-GGUF`](https://huggingface.co/lynxpurr/ZhenLM-140M-SFT-v2e-GGUF)。从源码构建见
[`docs/reproduction.md`](docs/reproduction.md)。

### Ollama + GGUF（推荐）

```bash
bash scripts/download_model.sh
( cd models/ZhenLM-140M-SFT-v2e-GGUF && \
  OLLAMA_HOST=127.0.0.1:11435 ollama create zhenlm-140m-sft-v2e-q8 \
  -f Modelfile-ZhenLM-140M-SFT-v2e-q8 )
bash scripts/run_demo.sh                # http://127.0.0.1:7860
```

### Hugging Face `transformers`

```bash
# 先跑 `bash scripts/setup.sh`（或用你自己的 Python 3.12 环境）
uv pip install --python .venv-pre/bin/python -r requirements-hf.txt
.venv-pre/bin/python - <<'PY'
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
repo = "lynxpurr/ZhenLM-140M-SFT-v2e"
tok = AutoTokenizer.from_pretrained(repo)
model = AutoModelForCausalLM.from_pretrained(repo, dtype=torch.float16)
messages = [{"role": "user", "content": "请用一句话介绍杭州。"}]
inputs = tok.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt")
out = model.generate(**inputs, max_new_tokens=80, do_sample=False)
print(tok.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True))
PY
```

从源码构建：[`docs/reproduction.md`](docs/reproduction.md)（约 38GB 数据，
~16 小时预训练）。

## 结果

全部 greedy 解码、同一 chat 模板、同一 tokenizer。dev 用于迭代，90 题 holdout
用于验收。`rep-4` = 4-gram 复读率（越低越好）。

| 模型 | dev 18 | holdout 90（人工） | rep-4 ↓ | 备注 |
|---|---|---|---|---|
| base（预训练） | 6/18 | 12/90 | 0.738 | 无指令能力 |
| SFT v1 | 16/18 | 47/90 | 0.248 | 完全干净基线 |
| SFT v2 | 15/18 | 47/90 | 0.168 | 校准/翻译修好，数学回归 |
| SFT v2e（部署） | **17/18**\* | **53/90** | **0.138** | \*2 题已知残留；干净子集 **15/16** |
| LoRA r=12 2ep | 15/18 | 48/90 | 0.283 | 不部署 |

> 表内人工分是原始 audit。2026-11-21 逐题重判为 v2e **52** vs v2 **45**（+7），
> 但 McNemar **p=0.0923**（不显著）。2026-11-22 的 47 题第二复核**未复现**
> 该优势：v2e **11 vs 11**（kappa 0.660/0.453；paired p=1.000），即使放宽口径
> 最多 +2。+6/+7 对 rubric 敏感，不是稳定的能力提升。见
> [`docs/evaluation.md`](docs/evaluation.md) §6.1。

**能力块**（数学 14 / 翻译 14 / calibration 6）：

| 块 | 分数 | 含义 |
|---|---|---|
| 数学 | 0–3 / 14 | 窄查表，**不是算术**（`13×5`、`17+6`、`100−37` 全错） |
| 翻译 | 0–5 / 14 | 句式级，**不是通用翻译**（zh→en 简单句可译；en→zh 大多失败） |
| calibration | 5–6 / 6 宽松；1–3 / 6 严格 | 拒绝编造，但前提纠正常事实错误（2044/2046 都是赛事年） |

能力块是验收单位；单题修复不代表能力。

## 限制

- **数学**：记住了几个 dev 答案，不是算术。
- **翻译**：只学会了少量指令句式；`Knowledge is power` 常被原样回英文。
- **知识**：140M / 3B token ≈ GPT-2 级；会编造人名、年份、细节。
- **身份**：SFT 语料来自 minimind，模型常自称 "minimind"（greedy 下也是）。
- **上下文 / 安全**：1024 token；没有安全对齐、RLHF 或偏差评测。

## 评测记录

- **污染**：早期 SFT "修复"把评测原句写进了补充样本，所以 v2~v2d 的 dev 分
  含记忆成分；v1 是干净基线，v2e 有 2 题残留（干净子集 15/16）。
- **检查器假阴性**：首版去重检查器跳过短 prompt；现在的版本去掉长度守卫、
  norm 去掉非单词字符，并内置"已知撞车必须被抓"的自测
  （[`tools/check_eval_leak.py`](tools/check_eval_leak.py)）。
- **holdout + 第二复核**：dev 排名只部分复现；90 题 holdout 是验收集，
  47 题第二复核未复现 +7（11 vs 11）。见 [`docs/evaluation.md`](docs/evaluation.md) §6.1。
- **量化**：Q4_K_M 在 v2e 上不保真；Q8_0 是默认；F16 在 5/5 抽检中逐字一致。

## 复现

```bash
bash scripts/setup.sh
bash scripts/download_data.sh
.venv-pre/bin/python -I tools/train_tokenizer.py   # 32k BPE
.venv-pre/bin/python -I tools/build_shards.py      # 3B token memmap
# 预训练 / SFT 命令：docs/reproduction.md
bash scripts/reproduce_eval.sh                     # dev + 90 题 holdout
```

可复现性证据：v2e 数据重建 4/4 SHA256、评测 18/18 行逐字节一致、F16 5/5。
见 `reports/2026-11-20-day10-repro-check.md`。

## 仓库地图

| 路径 | 内容 |
|---|---|
| `tools/` | 模型、训练、SFT、LoRA、评测、GGUF、demo |
| `data/eval/` | dev 18 + holdout 30 + holdout 90 题库 |
| `data/PROVENANCE.md` | 数据来源、许可证、SHA256 指纹 |
| `reports/` | 证据：摘要、CSV、原始 log（只增不改） |
| `docs/` | quickstart、reproduction、evaluation、architecture、FAQ |
| `REPORT.md` / `HISTORY.md` | 完整报告 / 历史 commit 说明 |
| `MODEL_CARD.md` / `MODEL_CARD.en.md` | 模型卡（中/英） |

## 实现说明

AI 辅助代码与文档；范围、实验、评测与发布由人主导。关键结论做了独立验证
（bit-for-bit 数据、18/18 逐字节、F16 5/5、已知撞车阳性对照、McNemar）。

## 许可与引用

- **代码与模型权重**：Apache License 2.0 — 见 [`LICENSE`](LICENSE)。
- **文档与评测集**：CC BY 4.0 — 见 [`docs/LICENSE-CC-BY-4.0.txt`](docs/LICENSE-CC-BY-4.0.txt) 与 [`data/LICENSE`](data/LICENSE)。
- **上游数据**：FineWeb-Edu（ODC-BY 1.0 + Common Crawl ToU）、minimind_dataset（Apache-2.0）。见 [`NOTICE`](NOTICE)。
- 引用格式见 [`CITATION.cff`](CITATION.cff)。

## 致谢

架构与数据格式参考 [minimind](https://github.com/jingyaogong/minimind)（Apache-2.0）、
[nanoGPT](https://github.com/karpathy/nanoGPT)（MIT）；GGUF 布局参考
[llama.cpp](https://github.com/ggml-org/llama.cpp)（MIT）；数据来自
[FineWeb-Edu](https://huggingface.co/datasets/HuggingFaceFW/fineweb-edu) 与
[minimind_dataset](https://huggingface.co/datasets/jingyaogong/minimind_dataset)。

*本项目是学习/研究产物，与上述项目无隶属或背书关系，也不替代它们。*