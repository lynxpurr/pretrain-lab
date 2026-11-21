# pretrain-lab

**一张 16GB 显卡，从零训一个 137.8M 参数中英小模型——以及它做不到的事。**

这不是一个要和开源大模型竞争的模型，而是一次**完整、可复现的案例研究**：
tokenizer → 3B token 预训练 → 六版 SFT → LoRA 消融 → GGUF/Ollama 部署，
每一步的证据都在 [`reports/`](reports/)。最有价值的部分是评测故事：
我们自己发现了训练集污染、修好了去重检查器的假阴性、建了 90 题 holdout，
并如实报告数学/翻译的失败，而不是把它们藏起来。

- **模型**：137,847,552 参数 · d_model 768 · 16 层 · 12 头 · RoPE + RMSNorm + SwiGLU + tied embeddings · 32k BPE · 上下文 1024
- **预训练**：3.0B token（英文 60% FineWeb-Edu / 中文 40% minimind）· 16h07m41s · val **2.7709**
- **SFT**：250M token，assistant-only mask，六版 · 部署 **v2e**（val 1.6065，rep-4 **0.055**）
- **硬件**：单卡 RTX 5070 Ti 16GB · 全本地
- **部署**：Q8_0 GGUF（174 MB）→ Ollama → 零依赖本地聊天页

## 快速开始

> Hugging Face 仓库是 v1.0 发布的一部分。如果 `scripts/download_model.sh`
> 暂时找不到仓库，可从源码构建（[`docs/reproduction.md`](docs/reproduction.md)）
> 或直接使用本地发布文件（`out/gguf/`）。

### A — Ollama + GGUF（最快，不需要 Python 训练栈）

```bash
bash scripts/download_model.sh          # 从 Hugging Face 下载 GGUF + Modelfile
( cd models/pretrain-lab-140m-sft-v2e-GGUF && \
  OLLAMA_HOST=127.0.0.1:11435 ollama create pretrain-lab-sft-v2e-q8 \
  -f Modelfile-sft-v2e-q8 )
bash scripts/run_demo.sh                # http://127.0.0.1:7860
```

### B — Hugging Face `transformers`

```bash
# 先跑 `bash scripts/setup.sh`（或用你自己的 Python 3.12 环境）
uv pip install --python .venv-pre/bin/python -r requirements-hf.txt
.venv-pre/bin/python - <<'PY'
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
repo = "lynxpurr/pretrain-lab-140m-sft-v2e"
tok = AutoTokenizer.from_pretrained(repo)
model = AutoModelForCausalLM.from_pretrained(repo, dtype=torch.float16)
messages = [{"role": "user", "content": "请用一句话介绍杭州。"}]
inputs = tok.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt")
out = model.generate(**inputs, max_new_tokens=80, do_sample=False)
print(tok.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True))
PY
```

### C — 从源码完整重建

见 [`docs/reproduction.md`](docs/reproduction.md)：约 38GB 数据下载、~21 分钟分片、
~16 小时预训练、每版 SFT ~1 小时 20 分钟。

## 结果（诚实版）

全部 greedy 解码、同一 chat 模板、同一 tokenizer。dev 用于迭代，90 题 holdout 用于验收。
`rep-4` = 4-gram 复读率（越低越好）。

| 模型 | dev 18 | holdout 90（人工） | rep-4 ↓ | 备注 |
|---|---|---|---|---|
| base（预训练） | 6/18 | 12/90 | 0.738 | 无指令能力 |
| SFT v1 | 16/18 | 47/90 | 0.248 | 完全干净基线 |
| SFT v2 | 15/18 | 47/90 | 0.168 | 校准/翻译修好，数学回归 |
| SFT v2e（部署） | **17/18**\* | **53/90** | **0.138** | \*2 题已知残留；干净子集 **15/16** |
| LoRA r=12 2ep | 15/18 | 48/90 | 0.283 | 不部署 |

> 表内人工分是原始 audit。2026-11-21 逐题重判为 v2e **52** vs v2 **45**（+7）；
> 配对 McNemar **p=0.0923**（未达 0.05 显著）。详见评测文档 §6。

**能力块（数学 14 / 翻译 14 / calibration 6）：**

| 块 | 最好结果 | 判定 |
|---|---|---|
| 数学 | 0–3 / 14 | ✗ 窄查表，**不是算术**（`13×5`、`17+6`、`100−37` 全错） |
| 翻译 | 0–5 / 14 | ✗ 句式级，**不是通用翻译**（zh→en 简单句可译；en→zh 大多失败） |
| calibration | 5–6 / 6 | ✓ 唯一稳定泛化项（v2 数据系拒绝编造未来事实） |

90 题人工校准：audit **v2e 53 vs v2 47（+6）**；2026-11-21 逐题重判 **v2e 52 vs v2 45（+7）**，
均达到预注册阈值（≥5）。**但配对 McNemar 精确 p=0.0923 > 0.05，统计上不显著**
（bootstrap 95% CI [0.000, 0.156]，下界≈0）。增量集中在英文流畅度（v2e 5/5 vs v2 0/5），
数学 −1、翻译/calibration 持平。对外表述 = **"方向一致、达到预注册阈值，但未达 0.05 显著"**；
30 题"无显著差异"仍是欠功效。判定口径与局限见 [`docs/evaluation.md`](docs/evaluation.md)。
不要把它读成"大幅、可用于生产的提升"。

## 它做不到什么

- **数学**：记住了几个 dev 答案，不是算术；未见组合会错。
- **翻译**：只学会了少量指令句式，不是翻译模型；`Knowledge is power` 常被原样回英文。
- **事实**：140M / 3B token ≈ GPT-2 级知识；会编造人名、年份、细节，不要当知识源。
- **生产**：没有安全对齐、RLHF、长上下文（1024 token），不保证事实/风格质量。
- **身份**：SFT 语料来自 minimind，模型常自称 "minimind"（greedy 下也是）；
  自述身份不可靠。

## 最有意思的部分：评测方法学

1. **发现并去除训练集污染**：早期 SFT "修复"把评测原句写进了补充样本，
   所以 v2~v2d 的 dev 分含记忆成分；v1 是干净基线，v2e 是"部分干净"
   （2 题残留，干净子集 15/16）。
2. **检查器自己也会假阴性**：旧的 `len(prompt) >= 8` 守卫跳过了短 prompt，
   "0 撞车"是假的；修法是去掉长度守卫、norm 去掉所有非单词字符、
   内置"已知撞车必须被抓"的自测。见 `tools/check_eval_leak.py`。
3. **holdout 比 dev 可信**：90 题显示 dev 排名只部分复现；数学/翻译/calibration
   用 10~14 题的能力块判定，不用单题代表能力。
4. **量化保真度**：Q4_K_M 在 v2e 上会吃掉新学能力（math 42→72、翻译回退）；
   部署默认 Q8_0，F16 在 5/5 抽检中逐字一致。
5. **LoRA 容量曲线**：r=8→r=12 只买 −0.020 val；1→2 epochs 只买 −0.013；
   都补不上距全参的 0.19。LoRA 适合领域增量，不适合首次对齐。

完整叙事见 [`REPORT.md`](REPORT.md) · 模型卡 [`MODEL_CARD.md`](MODEL_CARD.md)
（英文 [`MODEL_CARD.en.md`](MODEL_CARD.en.md)）· 评测细节 [`docs/evaluation.md`](docs/evaluation.md)。

## 复现

```bash
bash scripts/setup.sh                  # venv + torch 2.11.0+cu128 + 依赖
bash scripts/download_data.sh          # 37.9GB，SHA256 校验
.venv-pre/bin/python -I tools/train_tokenizer.py   # 32k BPE，~4.5 分钟
.venv-pre/bin/python -I tools/build_shards.py      # 3B token memmap，~21 分钟
# 预训练 16 小时；命令见 docs/reproduction.md
# SFT v2e ~1 小时 20 分钟；命令见 docs/reproduction.md
bash scripts/reproduce_eval.sh         # dev + 90 题 holdout
```

可复现性证据：v2e 数据重建 bit-for-bit（4/4 SHA256）、评测 18/18 行逐字节一致、
F16 GGUF 与 PyTorch 5/5 逐字一致。见 `reports/2026-11-20-day10-repro-check.md`。

## 仓库地图

| 路径 | 内容 |
|---|---|
| `tools/` | 模型、训练、SFT、LoRA、评测、GGUF、demo 脚本 |
| `data/eval/` | dev 18 + holdout 30 + holdout 90 题库 |
| `data/PROVENANCE.md` | 数据来源、许可证、SHA256 指纹 |
| `reports/` | 证据：摘要、CSV、原始 log（只增不改） |
| `docs/` | quickstart、reproduction、evaluation、architecture、FAQ |
| `REPORT.md` | 完整中文报告 |
| `MODEL_CARD.md` / `MODEL_CARD.en.md` | 模型卡（中/英） |

## 实现说明

AI 辅助代码与文档；范围、实验、评测与发布由人主导。每个关键结论独立验证（bit-for-bit 数据、18/18 逐字节、F16 5/5、已知撞车阳性对照、McNemar）。

## 许可与引用

- **代码与模型权重**：Apache License 2.0 — 见 [`LICENSE`](LICENSE)。
- **文档与评测集**：CC BY 4.0 — 见 [`docs/LICENSE-CC-BY-4.0.txt`](docs/LICENSE-CC-BY-4.0.txt) 与 [`data/LICENSE`](data/LICENSE)。
- **上游数据**：FineWeb-Edu（ODC-BY 1.0 + Common Crawl ToU）、minimind_dataset（Apache-2.0）。
  见 [`NOTICE`](NOTICE)；原始语料不再分发。
- 引用格式见 [`CITATION.cff`](CITATION.cff)。

## 致谢

架构与数据格式参考 [minimind](https://github.com/jingyaogong/minimind)（Apache-2.0）、
[nanoGPT](https://github.com/karpathy/nanoGPT)（MIT）；
GGUF 布局参考 [llama.cpp](https://github.com/ggml-org/llama.cpp)（MIT）；
数据来自 [FineWeb-Edu](https://huggingface.co/datasets/HuggingFaceFW/fineweb-edu) 与
[minimind_dataset](https://huggingface.co/datasets/jingyaogong/minimind_dataset)。

*本项目是学习/研究产物，与上述项目无隶属或背书关系，也不替代它们。*