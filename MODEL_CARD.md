# Model Card — pretrain-lab 140M（SFT v2）

> 一个**从零手写并训练**的中英双语 ~140M 小模型：3B token 预训练 + 250M token SFT。定位 = 学习/本地 demo，**不是**生产模型，也不对标开源大模型。

## 1. 模型详情

| 项 | 值 |
|---|---|
| 架构 | decoder-only Transformer：RoPE + RMSNorm（pre-norm）+ SwiGLU + tied embeddings |
| 规模 | d_model 768 · 16 层 · 12 头（head_dim 64）· **137,847,552** 参数 |
| 词表 / 上下文 | 32,000 BPE（ByteLevel；specials `<|endoftext|>`=0 / `<|im_start|>`=1 / `<|im_end|>`=2）· 1024 token |
| 预训练 | 3,000,000,000 token（FineWeb-Edu 60% + minimind pretrain_t2t 40%）· 46 个 ckpt 谱系 |
| SFT | `data/sft-mix-v2` 250,001,408 token（minimind sft_t2t_mini + 合成校准/格式/正例；assistant-only mask；25% 预训练混入） |
| 底座 / SFT ckpt | `out/main140m/last.pt`（val 2.7709）→ `out/sft-v2/last.pt`（SFT val 1.6038） |
| 量化 | GGUF F16 312MB / Q4_K_M 103MB / Q8_0 173MB（Ollama 用户级服务 11435） |
| 训练环境 | 本地 RTX 5070 Ti 16GB · `.venv-pre` torch 2.11.0+cu128 · 预训练 16h08m / SFT v2 1h20m |

## 2. 预期用途

- **本地学习 demo / 中文英文闲聊**：身份问答、简单解释、翻译、短代码、格式约束（"只回答数字"等）。
- **不适用**：事实性 QA（知识贫乏且会编造）、数学/推理（140M 容量有限）、生产决策、医疗/法律建议。

## 3. 评测（greedy + 关键词 + rubric，2026-11-20 八版）

| 模型 | 预训练 PPL | SFT PPL | 18 题关键词 | rubric(8题) | rep-4 ↓ | 备注 |
|---|---|---|---|---|---|---|
| base（预训练底座） | 15.350 | 9.818 | 6/18 | 1/8 | 0.727 | 无指令能力 |
| SFT v1 | 16.307 | 4.596 | 16/18 | 1/8 | 0.131 | 规则分高估：校准编造/格式差/拒答模板 |
| **SFT v2（部署）** | **16.185** | 4.845 | 15/18（语义 16/18） | 4/8 | **0.066** | 校准/翻译/格式修好；数学弱 |
| SFT v2b（消融） | 16.186 | 4.822 | 15/18 | 5/8 | 0.117 | 数学修好；复读/翻译退化 |
| LoRA r=8（v2 数据） | **15.690** | 6.090 | 15/18 | 4/8 | 0.260 | 1.20% 可训练 / peak 9.74GB / ckpt 526MB + adapter 6.5MB；**1 epoch 欠拟合，不部署** |
| SFT v2c（消融） | **16.184** | 4.834 | **17/18（最高）** | **5/8** | 0.135 | math 修回 + en-fluency 首修 + refuse 双过；rep-4/translate-en2zh 未收敛（rep-4 判据未过 → 按预注册不部署） |
| SFT v2d（消融，机动窗口） | **16.181** | 4.851 | 15/18（语义 17/18） | **6/8** | 0.084 | 长答案复读压制 + concise 正例：reason 0.728→0.088；未达 = rep-4 差 0.004 / math-mul 72 / translate 字词解释 → 不部署 |
| SFT v2e（消融，机动窗口第 2 轮，**五项判据全过**） | 16.192 | 4.847 | **17/18（去污后干净读数）** | **6/8** | **0.055（全系最低）** | 去污 + translate 精确对 + math ×2：translate "我热爱机器学习。" / math 8+42 真泛化 / en-fluency 通顺；**全面优于 v2，部署切换待拍板** |

> 关键词分与 rubric 并列：v2 的正确回答"2027 年没有世界杯"因 `expect_any` 缺"没有"被判关键词 ❌，rubric 语义 ✅；v1 的"没有官方…1958"含关键词但编造，rubric ❌。**不要只看单一分数。** 关键校正（v2e 开工发现）：**v2~v2d 的题库读数含评测记忆成分**（extras 原句与 18 题撞车，v2 起就有）；**v1 的 16/18 与 v2e 的 17/18 才是干净读数**。v2e 去污后五项判据全过（rep-4 0.055 / translate 真译文 / math 8/42 真泛化）——v2e 是能力最优版，部署切换待拍板。

## 4. 已知限制

1. **事实知识贫乏**：3B token / 140M 参数 ≈ GPT-2 级别；会编造细节（如队名、人口、地理）。
2. **数学弱**：SFT v2 的 `math-add`/`math-mul` 会算错（3+5=15、7×6=72）；v2b/v2c 修回算术（v2c = 8/42），但"只回答数字"的纯数字格式仍未跟随；部署版建议在 UI 上标注"数学不可靠"。
3. **英文良性问题可能拒答**：`en-fluency`（"Tell me about the ocean"）在 v1/v2/v2b/LoRA 触发拒答模板；v2c 已修复（英文正文），但代价是英文长文复读——部署版 v2 仍有此问题。
4. **长回答可能复读**：部署版 v2 的 rep-4 0.066 仍是全七版最低；v2c/v2b 的长答案复读（0.135/0.117）与 v2d 的修复路径（0.084，长答案压制 + concise 正例）见 Day 8 与机动窗口报告——部署模型未更新，复读仍以 v2 行为为准。
5. **身份在采样下不稳定**：T0.7 下偶发"通义千问/小玲"等；greedy 更稳定（minimind/jingyaogong）。demo 已加系统提示。
6. **上下文 1024**；超出会截断。

## 5. 数据与许可

- FineWeb-Edu（ODC-BY v1.0，另受 CommonCrawl ToU 约束）；minimind_dataset（Apache-2.0）；合成补充样本由本仓 `tools/gen_sft_v2_extra.py` 生成。再分发/商用前请自行核对上游许可。
- 指纹与出处：`data/PROVENANCE.md` + 各层 `SHA256SUMS`。

## 6. 复现

```bash
# 数据
.venv-pre/bin/python -I tools/gen_sft_v2_extra.py
.venv-pre/bin/python -I tools/build_sft_v2.py --listy-keep-den 5 --calib-repeat 3 --format-repeat 2 --helpful-repeat 3
# SFT
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True .venv-pre/bin/python -I tools/sft.py \
  --init-from out/main140m/last.pt --data-dir data/sft-mix-v2 --run-name sft-v2 --out-dir out/sft-v2 \
  --batch-size 8 --grad-accum 8 --base-lr 1e-4 --warmup 100 --target-tokens 250e6
# 评测
.venv-pre/bin/python -I tools/eval.py --ckpt sft=out/sft-v2/last.pt --out reports/eval.md
# GGUF / Ollama
.venv-pre/bin/python -I tools/export_gguf.py --ckpt out/sft-v2/last.pt --out out/gguf/sft-v2-f16.gguf
OLLAMA_HOST=127.0.0.1:11435 ollama create pretrain-lab-sft-v2-q4 -f out/Modelfile-sft-v2 -q q4_K_M
# demo
.venv-pre/bin/python -I tools/app_stdlib.py --model pretrain-lab-sft-v2-q4 --port 7860
```

## 7. 引用/出处

- 底稿：NoteFlow `WorkingDeck/2026-09/2026-09-22/small-llm-10day-plan.md`
- 参考实现：minimind @ `233d00f`、nanoGPT @ `3adf61e`（只读借鉴）
- 全部训练/评测证据：`reports/2026-11-18-day*` ~ `reports/2026-11-19-day7-*`