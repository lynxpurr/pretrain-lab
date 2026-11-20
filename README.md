# pretrain-lab — 小模型从零训练 10 天行动

> 建立：2026-11-18 · 一句话：本地 5070 Ti 16GB 上，10 天完整经历 **~140M 从零预训练 → SFT → LoRA 对比 → 部署 demo** 全生命周期。**学习导向**。
> 底稿：NoteFlow `WorkingDeck/2026-09/2026-09-22/small-llm-10day-plan.md` · 热身：nl2fem + finetune-lab（均 2026-09-27 收官，SFT 半场已预付，本仓主攻从零预训练半场）。

## 状态快照（2026-11-20 · **项目收官：Day 10 终检提前 7 天完成** · 140M×3B 底座 + 八版 SFT 对比（部署 v2e-q8）+ LoRA r=8/r=12 + 本地 demo + 定稿报告）

- **窗口**：提前起跑，Day 1 = 2026-11-18（周三）→ **实际 2026-11-20 完成 Day 10 终检（原定 11-27，提前 7 天收官）**；Day 2/Day 3 均为 11-18 当日续跑，Day 9 硬缓冲未用。
- **Day 0（11-18 早）**：`.venv-pre`（uv 托管 3.12.13 + torch 2.11.0+cu128，CUDA/sm_120/bf16 验证过）· minimind@`233d00f` + nanoGPT@`3adf61e` · 数据 37.9GB 预下载（fineweb-edu 27.85G + minimind 10.07G，指纹落 `data/PROVENANCE.md`）。
- **Day 1（11-18）**：手写 `tools/model.py`（RoPE+RMSNorm+SwiGLU+tied，22,220,544 参数）+ 字符级 20M 闭环（30 万/3 万字符切片、词表 11,765）：**33,000 步 / 96.1 分钟 / 187,480 字符/秒 / val loss 1.5599**，采样从字符汤收敛到结构化段落 + 押韵短诗——证据 [reports/2026-11-18-day1-char20m.md](reports/2026-11-18-day1-char20m.md)。
- **Day 2（11-18 续跑）**：32k 中英 BPE（zh 1.841 / en 4.226 chars/token）+ **3,000,000,000 token** memmap 训练集（en:zh = 60:40，6×1GB 片 + val 4M，全部 sha256 入库）+ 换轨冒烟首步 **10.4542** ≈ ln(32000)=10.3735——证据 [reports/2026-11-18-day2-shards.md](reports/2026-11-18-day2-shards.md)（另 tokenizer/smoke 两件同目录）。
- **Day 3（11-18 续跑）**：`tools/train.py` 完整框架（多分片加权取片 / 梯度累积 / 三路 RNG 续训 / 固定 val / 双语采样 / EXIT 标记）+ **50M 30min 预注册跑 120,517 tok/s**（val 3.6377）+ **140M 探针 52,250 tok/s → 决策门① PASS**（3B 单程 **15.9h**）——证据 [reports/2026-11-18-day3-framework.md](reports/2026-11-18-day3-framework.md) · [50m-30min](reports/2026-11-18-day3-50m-30min.md) · [140m-probe](reports/2026-11-18-day3-140m-probe.md)。
- **Day 4~5（11-18 18:46 → 11-19 10:53）**：**140M 主训练收官** — 3,000,041,472 token / 16h07m41s / **val 2.7709** / 52,171 tok/s / 46 ckpt ≈73GB / 0 尖峰；终版采样中英事实已对（"中国的首都是北京"、"The capital of France is Paris"）——证据 [reports/2026-11-19-day4-main140m.md](reports/2026-11-19-day4-main140m.md)。SFT 数据 `data/sft-mix/`（250M token，assistant-only mask）+ `tools/sft.py` 已就绪（CPU 自检过）。
- **Day 5（11-19）**：**SFT v1 收官**（3,815 步 / 1h19m26s / SFT val **1.5515**）+ **base/SFT 对比评测**：题库 **6/18（33%）→ 16/18（89%）**、SFT PPL **9.82 → 4.60**、预训练 PPL 15.35 → 16.31（遗忘 +6.2%）——证据 [reports/2026-11-19-day5-eval.md](reports/2026-11-19-day5-eval.md)（质性缺陷：复读环/编造推理/拒答模板，规则分高估质量）。门② 双证据（最后 10% 降幅 0.0134 + 恒定 lr 探针 0.0051）→ **不加训**。
- **Day 6（11-19）**：**门② 正式判定 = 不加训**（最后 10% 降幅 0.0134 + 恒定 lr 探针 0.0051 双证据）+ **解码对照**：证伪"greedy 放大复读"（采样 rep-4 0.123 vs greedy 0.131）、rp1.3 能压到 0.032 但题库 16→13——**复读来自数据罗列风格，校准/格式缺陷也与解码无关** → SFT v2 走数据侧；评测协议定档（greedy + distinct-2/rep-4 + rubric）——证据 [reports/2026-11-19-day6-decode.md](reports/2026-11-19-day6-decode.md) · [gate2](reports/2026-11-19-day6-gate2.md)。
- **Day 7（11-19）**：**SFT 数据 v2/v2b + LoRA + GGUF/Ollama demo**。SFT v2 val **1.6038** / rep-4 **0.066** / 预训练 PPL +5.4% / 题库 15-18（语义 16-18）；校准（"2027 年没有世界杯"）、翻译方向、一句话、月份编造修好，但数学回归（3+5=15、7×6=72）；v2b 数学保护修回 **8/42** 但 rep-4 0.117（不部署，消融）；LoRA r=8 **1.20%** / peak **9.74GB（-2.3GB）** / ckpt 526MB+adapter 6.5MB / val 1.8253 / rep-4 0.260（1 epoch 欠拟合，不部署）；GGUF **Q4_K_M 103MB** + Ollama 用户级 11435 + demo **7860**——证据 [reports/2026-11-19-day7-sft-v2.md](reports/2026-11-19-day7-sft-v2.md) · [deploy.log](reports/2026-11-19-day7-deploy.log) · 模型卡 [MODEL_CARD.md](MODEL_CARD.md)。
- **Day 8（11-19 晚 → 11-20 晨，提前开工）**：**v2c 选择性数学保护 + 英文再平衡 + 六版评测 + 报告开写**。侦察先行（等式行 ≥3 = 9,693 条练习列表）→ v2c 数据（列表 10.55%）→ **val 1.6018 / 题库 17/18 + rubric 5/8 双历史最高**：math 修回（8/42）、**en-fluency 四版全挂题首次修复**、refuse-unknown 双过；rep-4 0.135 未达 <0.08 判据 + translate-en2zh 回归 → **按预注册保持 v2 部署**，v2c 入档能力最优消融；**[REPORT.md](REPORT.md) 11 章起稿**——证据 [reports/2026-11-20-day8-v2c.md](reports/2026-11-20-day8-v2c.md) · [eval](reports/2026-11-20-day8-eval.md) · [rubric](reports/2026-11-20-day8-eval-rubric.md)。
- **机动窗口（11-20 已跑 v2d）**：**v2d 长答案复读压制 + translate 方向 + 格式补强**——rep-4 **0.084**（SFT 最低档，v2c 0.135 砍 38%）+ rubric **6/8 历史最高**、reason 0.728→**0.088** / en-fluency 0.708→0.371 / zh-fluency 0.516→0.303、math-add 纯数字"8"；未达判据 = rep-4（差 0.004）/ math-mul（回退 72）/ translate 行为（字词解释）/ 关键词题库 15/18（语义 17/18）→ **按预注册不部署，v2 保持部署**；v2e 候选（translate 精确样本 + math 专项 + en_flu 降采样）留 11-22~25 拍板——证据 [reports/2026-11-20-v2d.md](reports/2026-11-20-v2d.md) · 经验 [notes/lessons.md](notes/lessons.md) 机动窗口段 · 概念题 [notes/qa-day-8.md](notes/qa-day-8.md)。
- **机动窗口第 2 轮 v2e（去污轮，11-20）**：**开工发现评测污染**（v2 起 extras 与 18 题原句撞车 → v2~v2d 题库分含记忆成分，v1 的 16/18 反而是干净读数）→ 去污 12 处 + `assert_no_eval_leak` 断言 + translate 精确对 180 + 数学豁免 ×2 + en_flu 降采样 → **rep-4 0.055（全系最低）/ 题库 17/18（去污后）/ rubric 6/8 / translate "我热爱机器学习。" / math 8+42 真泛化 / PPL +5.5%——五项预注册判据全过，全面优于 v2**——证据 [reports/2026-11-20-v2e.md](reports/2026-11-20-v2e.md)。
- **最终阶段 + Day 10（11-20，提前收官）**：**部署切 `pretrain-lab-sft-v2e-q8`**——三档同 prompt 对拍发现 **Q4_K_M 量化吃掉新学能力**（math 42→72 / translate 退回英文原句），Q8_0 全保住 → 部署默认 Q8_0 + 新增"量化保真度抽检"验收红线；REPORT 增 §5.1 评测污染独立章 + §4.7 八版终表（含"含记忆/干净"标注）+ §10 复现对齐 v2e；**终检**：v2e build 重跑 **bit-for-bit 一致**（4/4 sha256 + meta 全字段）、八版表与 eval 报告对账、60 份 md / 173 条链接 **0 断链**、证据 md/csv/log 三件齐；**holdout 复核**（30 题未见题，三层去重 0 撞车）：v2e 与 v2 人工复核同为 24/30，dev 的 17 vs 15 优势不复现，`13×3` 仍答 42 → REPORT §5.2；LoRA r=12 补 G3 容量曲线（1.79% 可训练）——证据 [reports/2026-11-20-deploy-v2e.md](reports/2026-11-20-deploy-v2e.md) · [repro-check](reports/2026-11-20-day10-repro-check.md) · [holdout-audit](reports/2026-11-20-holdout-audit.md) · [REPORT.md](REPORT.md)。
- **路线**：Day 3 框架+门① ✅ → Day 4 140M 主训练 ✅ → Day 5/6 SFT v1 + 门② ✅ → Day 7 SFT v2/v2b + LoRA + 部署 ✅ → Day 8 v2c + 六版评测 + 报告开写 ✅ → 机动窗口 v2d（rep-4 0.084）✅ → **v2e 去污轮（五项全过：rep-4 0.055 / 题库 17-18）✅ → 部署切 v2e-q8 ✅ → Day 10 终检（11-20 提前）✅ 项目收官**。
- 预期管理：140M/30 亿 token ≈ GPT-2 124M 水平（通顺、贫乏）——产出 = 经验 + 亲手训的模型 + 报告 + demo，非对标开源质量

## 目标进度（G1~G6，2026-11-20）

| 门 | 状态 | 关键读数 |
|---|---|---|
| G1 最小闭环 + 门① | ✅ | 140M 探针 **52,250 tok/s** ≥ 35k（门① PASS） |
| G2 140M 底座 | ✅ | 3B token / 16h08m / **val 2.7709** / 46 ckpt 谱系 |
| G3 SFT + LoRA | ✅ 完成 | **部署 v2e**（val 1.6065 / rep-4 **0.055** / 题库 **17/18 去污后** / math 8-42 / rubric 6-8）；v2/v2b/v2c/v2d 为过程消融（v2 曾部署至 11-20）；LoRA r=8 **1.20% 可训练 / peak 9.74GB / ckpt 526MB / val 1.8253 / rep-4 0.260** + r=12 **1.79% / val 1.8054 / rubric 5-8 / rep-4 0.249**（rank↑ 只补 0.02 val，均不部署，见 REPORT §6） |
| G4 本地 demo | ✅ 完成（**部署已切 v2e-q8**） | GGUF F16 326MB / Q8_0 173MB（部署默认）/ Q4_K_M 103MB（v2e 上不保真）；Ollama 11435 默认 **`pretrain-lab-sft-v2e-q8`**；本地页 **7860**（stdlib 替代 Gradio） |
| G5 评测框架 + 对比 | ✅ 八版 + holdout | base/v1/v2/v2b/lora/v2c/v2d/v2e 同 val 同 18 题同 greedy + rubric + distinct-2/rep-4；**评测污染已识别并去污**（v2e 起为干净读数；八版终表含"含记忆/干净"标注）；**30 题 holdout 三层去重**：v2e 与 v2 人工复核同为 24/30，dev 排名不复现（REPORT §5.2） |
| G6 报告 + repo | ✅ 定稿 | **[REPORT.md](REPORT.md) 11 章定稿（§5.1 评测污染章 + §4.7 八版终表）** + [MODEL_CARD.md](MODEL_CARD.md)（v2e 口径）+ 各日报告/证据三分 + 54 份 md / 152 链接 0 断链 |

## 文档地图

| 内容 | 位置 |
|---|---|
| 计划 / 决策 / 逐日方案 / 风险 / 素材索引（唯一计划文档） | [PLAN.md](PLAN.md) |
| 会话交接（复现检查 + 波次队列 + 当日清单） | [HANDOFF.md](HANDOFF.md) |
| 逐日记账（决策与现象，每天写） | [LAB_NOTEBOOK.md](LAB_NOTEBOOK.md) |
| 模型卡（架构/数据/评测/限制/复现） | [MODEL_CARD.md](MODEL_CARD.md) |
| 训练/评测/数据/部署脚本（Day 1~10 逐步生长） | `tools/` |
| run 证据（只增不改） | `reports/` |
| 学习者 lessons（追加制）+ 概念检验题答案卡/评分要点 | `notes/`（`qa-rubric.md` = 18 题判分要点） |
| 仓内操作规程（训练跑批/故障速查/红线，agent 优先加载） | [.zcode/skills/pretrain-lab/SKILL.md](.zcode/skills/pretrain-lab/SKILL.md) |
| 数据集落位 + 出处指纹 | `data/`（PROVENANCE.md + SHA256SUMS） |
| 模型/checkpoint/语料（gitignore，脚本可再生） | `models/` · `checkpoints/` |

## 工作方式

develop 主干直提为主（提交信息带 `day-N` 标签）+ 大改走 feature 分支；每晚三道概念检验题（学习者模式）；证据只增不改；**数据指纹每份落位即录**（raw 层 17 条 · 字符级 3 条 · tokenizer 3 条 · 分片 7 条 · SFT v1/v2/v2b/v2c/v2d/v2e 各 4 条 + 补充样本 5 条 · 评测集 2 条（dev 18 + holdout 30）· ckpt 12 条）。决策门①（**140M 等效 ≥35k tok/s**）**已判 PASS（52,250）**、②（加训判定）**已判不触发**（最后 10% 0.0134 + 恒定 lr 探针 0.0051），口径跑前未改。仓内操作规程见 [.zcode/skills/pretrain-lab/SKILL.md](.zcode/skills/pretrain-lab/SKILL.md)；demo/Ollama 启动命令见 HANDOFF §2 与 [reports/2026-11-19-day7-deploy.log](reports/2026-11-19-day7-deploy.log)。
