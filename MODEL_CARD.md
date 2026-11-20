# Model Card — pretrain-lab 140M（SFT v2e，部署 Q8_0）

> 一个**从零手写并训练**的中英双语 ~140M 小模型：3B token 预训练 + 250M token SFT。定位 = 学习/本地 demo，**不是**生产模型，也不对标开源大模型。**部署模型 = `pretrain-lab-sft-v2e-q8`**（2026-11-20 起；v2 全 tag 保留可回滚）。

## 1. 模型详情

| 项 | 值 |
|---|---|
| 架构 | decoder-only Transformer：RoPE + RMSNorm（pre-norm）+ SwiGLU + tied embeddings |
| 规模 | d_model 768 · 16 层 · 12 头（head_dim 64）· **137,847,552** 参数 |
| 词表 / 上下文 | 32,000 BPE（ByteLevel；specials `<|endoftext|>`=0 / `<|im_start|>`=1 / `<|im_end|>`=2）· 1024 token |
| 预训练 | 3,000,000,000 token（FineWeb-Edu 60% + minimind pretrain_t2t 40%）· 46 个 ckpt 谱系 |
| SFT | `data/sft-mix-v2e` 250,001,408 token（minimind sft_t2t_mini + 合成校准/格式/正例/翻译精确对；assistant-only mask；25% 预训练混入；**extras 已做评测去重**） |
| 底座 / SFT ckpt | `out/main140m/last.pt`（val 2.7709）→ `out/sft-v2e/last.pt`（SFT val 1.6065） |
| 量化 | **部署默认 Q8_0（173MB）**——Q4_K_M 在 v2e 上会吃掉新学能力（math 42→72 / translate 回退），见 `reports/2026-11-20-deploy-v2e.md`；F16 326MB 可选。Ollama 用户级 11435 |
| 训练环境 | 本地 RTX 5070 Ti 16GB · `.venv-pre` torch 2.11.0+cu128 · 预训练 16h08m / SFT v2e 1h19m |

## 2. 预期用途

- **本地学习 demo / 中文英文闲聊**：身份问答、简单解释、翻译、短代码、格式约束（"只回答数字"等）。
- **不适用**：事实性 QA（知识贫乏且会编造）、数学/推理（140M 容量有限）、生产决策、医疗/法律建议。

## 3. 评测（greedy + 关键词 + rubric，2026-11-20 八版）

| 模型 | 预训练 PPL | SFT PPL | 18 题关键词 | rubric(8题) | rep-4 ↓ | 备注 |
|---|---|---|---|---|---|---|
| base（预训练底座） | 15.350 | 9.818 | 6/18 | 1/8 | 0.727 | 无指令能力 |
| SFT v1 | 16.307 | 4.596 | 16/18 | 1/8 | 0.131 | 规则分高估：校准编造/格式差/拒答模板 |
| SFT v2（原部署，至 11-20） | **16.185** | 4.845 | 15/18（语义 16/18） | 4/8 | **0.066** | 校准/翻译/格式修好；数学弱（**含记忆**读数） |
| SFT v2b（消融） | 16.186 | 4.822 | 15/18 | 5/8 | 0.117 | 数学修好；复读/翻译退化 |
| LoRA r=8（v2 数据） | **15.690** | 6.090 | 15/18 | 4/8 | 0.260 | 1.20% 可训练 / peak 9.74GB / ckpt 526MB + adapter 6.5MB；**1 epoch 欠拟合，不部署** |
| SFT v2c（消融） | **16.184** | 4.834 | **17/18（最高）** | **5/8** | 0.135 | math 修回 + en-fluency 首修 + refuse 双过；rep-4/translate-en2zh 未收敛（rep-4 判据未过 → 按预注册不部署） |
| SFT v2d（消融，机动窗口） | **16.181** | 4.851 | 15/18（语义 17/18） | **6/8** | 0.084 | 长答案复读压制 + concise 正例：reason 0.728→0.088；未达 = rep-4 差 0.004 / math-mul 72 / translate 字词解释 → 不部署 |
| **SFT v2e（部署，2026-11-20 起；五项判据全过）** | 16.192 | 4.847 | **17/18（去污后干净读数）** | **6/8** | **0.055（全系最低）** | 去污 + translate 精确对 + math ×2：translate "我热爱机器学习。" / math 8+42 真泛化 / en-fluency 通顺；**全面优于 v2，已切部署（Q8_0）** |

> 关键词分与 rubric 并列：v2 的正确回答"2027 年没有世界杯"因 `expect_any` 缺"没有"被判关键词 ❌，rubric 语义 ✅；v1 的"没有官方…1958"含关键词但编造，rubric ❌。**不要只看单一分数。** 关键校正（v2e 开工发现）：**v2~v2d 的题库读数含评测记忆成分**（extras 原句与 18 题撞车，v2 起就有）；**v1 的 16/18 与 v2e 的 17/18 才是干净读数**。v2e 去污后五项判据全过（rep-4 0.055 / translate 真译文 / math 8/42 真泛化）——v2e 是能力最优版，**部署已于 2026-11-20 切至 v2e-q8**。

## 4. 已知限制

1. **事实知识贫乏**：3B token / 140M 参数 ≈ GPT-2 级别；会编造细节（如队名、人口、地理）。
2. **数学弱（格式与泛化两层）**：v2e 去污后 `math-add` 8 / `math-mul` 42 是**真泛化**（训练集已排除对应组合），但"只回答数字"的纯数字格式仍未跟随（输出带加粗算式）、组合记忆对数据分布扰动敏感（v2d 曾退回 72）；部署版建议在 UI 上标注"数学不可靠"。
3. **英文长文可能复读**：v2e 已修复英文拒答（`en-fluency` 输出通顺英文正文），该题 rep-4 0.208 仍高于全库均值——140M 的长文连贯能力有限，英文尤甚。
4. **长回答复读已大幅改善**：v2e decoder rep-4 **0.055（全系最低）**；残余格式瑕疵 = `list-3` 段落式编号（未用行内编号）、`math-mul` 带加粗算式——内容正确、格式未跟随。
5. **身份在采样下不稳定**：较高温度下偶发"通义千问/小玲"等；greedy 更稳定（minimind/jingyaogong）。demo 已加系统提示，且 Day 10 终检把 demo 默认温度从 0.7 降到 **0.3**（translate 方向漂移 4/20 → 0/20）。
6. **上下文 1024**；超出会截断。

## 5. 数据与许可

- FineWeb-Edu（ODC-BY v1.0，另受 CommonCrawl ToU 约束）；minimind_dataset（Apache-2.0）；合成补充样本由本仓 `tools/gen_sft_v2_extra.py` 生成。再分发/商用前请自行核对上游许可。
- 指纹与出处：`data/PROVENANCE.md` + 各层 `SHA256SUMS`。

## 6. 复现

```bash
# 数据（v2e = 部署数据；含 extras 评测去重断言 assert_no_eval_leak）
.venv-pre/bin/python -I tools/gen_sft_v2_extra.py
.venv-pre/bin/python -I tools/build_sft_v2.py --listy-keep-den 5 --protect-math-short --en-refusal-keep-den 2 \
  --en-helpful-upsample 5 --concise-repeat 3 --translate-upsample 3 --long-answer-keep-den 2 \
  --format-repeat 3 --translate-ex-repeat 6 --math-upsample 2 --en-flu-no-upsample --out-dir data/sft-mix-v2e
# SFT（v2e）
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True .venv-pre/bin/python -I tools/sft.py \
  --init-from out/main140m/last.pt --data-dir data/sft-mix-v2e --run-name sft-v2e --out-dir out/sft-v2e \
  --batch-size 8 --grad-accum 8 --base-lr 1e-4 --warmup 100 --target-tokens 250e6
# 评测（八版同库同 greedy）
.venv-pre/bin/python -I tools/eval.py --ckpt v2e=out/sft-v2e/last.pt --out reports/eval.md
.venv-pre/bin/python -I tools/eval_format.py --csv reports/eval.csv --out reports/eval-rubric.md
# GGUF / Ollama（部署默认 Q8_0；F16 对拍通过后建 -q8）
.venv-pre/bin/python -I tools/export_gguf.py --ckpt out/sft-v2e/last.pt --out out/gguf/pretrain-lab-140m-sft-v2e-f16.gguf
OLLAMA_HOST=127.0.0.1:11435 ollama create pretrain-lab-sft-v2e-q8 -f out/Modelfile-sft-v2e -q q8_0
# demo
.venv-pre/bin/python -I tools/app_stdlib.py --model pretrain-lab-sft-v2e-q8 --port 7860
```

## 7. 引用/出处

- 底稿：NoteFlow `WorkingDeck/2026-09/2026-09-22/small-llm-10day-plan.md`
- 参考实现：minimind @ `233d00f`、nanoGPT @ `3adf61e`（只读借鉴）
- 全部训练/评测证据：`reports/2026-11-18-day*` ~ `reports/2026-11-19-day7-*`