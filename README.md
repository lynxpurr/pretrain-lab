# pretrain-lab — 小模型从零训练 10 天行动

> 建立：2026-11-18 · 一句话：本地 5070 Ti 16GB 上，10 天完整经历 **~140M 从零预训练 → SFT → LoRA 对比 → 部署 demo** 全生命周期。**学习导向**。
> 底稿：NoteFlow `WorkingDeck/2026-09/2026-09-22/small-llm-10day-plan.md` · 热身：nl2fem + finetune-lab（均 2026-09-27 收官，SFT 半场已预付，本仓主攻从零预训练半场）。

## 状态快照（2026-11-18 · Day 0~3 已收官：环境 + 字符级闭环 + BPE 数据 + 训练框架/门①）

- **窗口**：提前起跑，Day 1 = 2026-11-18（周三）~ Day 10 = 2026-11-27（周四），Day 9（11-26）硬缓冲；Day 2/Day 3 均为 11-18 当日续跑（**Day 4 起日期不变，机制上已多出两天缓冲**）。
- **Day 0（11-18 早）**：`.venv-pre`（uv 托管 3.12.13 + torch 2.11.0+cu128，CUDA/sm_120/bf16 验证过）· minimind@`233d00f` + nanoGPT@`3adf61e` · 数据 37.9GB 预下载（fineweb-edu 27.85G + minimind 10.07G，指纹落 `data/PROVENANCE.md`）。
- **Day 1（11-18）**：手写 `tools/model.py`（RoPE+RMSNorm+SwiGLU+tied，22,220,544 参数）+ 字符级 20M 闭环（30 万/3 万字符切片、词表 11,765）：**33,000 步 / 96.1 分钟 / 187,480 字符/秒 / val loss 1.5599**，采样从字符汤收敛到结构化段落 + 押韵短诗——证据 [reports/2026-11-18-day1-char20m.md](reports/2026-11-18-day1-char20m.md)。
- **Day 2（11-18 续跑）**：32k 中英 BPE（zh 1.841 / en 4.226 chars/token）+ **3,000,000,000 token** memmap 训练集（en:zh = 60:40，6×1GB 片 + val 4M，全部 sha256 入库）+ 换轨冒烟首步 **10.4542** ≈ ln(32000)=10.3735——证据 [reports/2026-11-18-day2-shards.md](reports/2026-11-18-day2-shards.md)（另 tokenizer/smoke 两件同目录）。
- **Day 3（11-18 续跑）**：`tools/train.py` 完整框架（多分片加权取片 / 梯度累积 / 三路 RNG 续训 / 固定 val / 双语采样 / EXIT 标记）+ **50M 30min 预注册跑 120,517 tok/s**（val 3.6377）+ **140M 探针 52,250 tok/s → 决策门① PASS**（3B 单程 **15.9h**）——证据 [reports/2026-11-18-day3-framework.md](reports/2026-11-18-day3-framework.md) · [50m-30min](reports/2026-11-18-day3-50m-30min.md) · [140m-probe](reports/2026-11-18-day3-140m-probe.md)。
- **Day 4（11-18 晚起跑，进行中）**：**140M 主训练 `main140m` 运行中**（bs8×accum8 · 52.8k tok/s · 1.25s/步 · ETA 11-19 ~10:30；val@500 4.9742）+ **SFT 数据 `data/sft-mix/` 250M token**（404,210 条对话 + 25% 预训练混合，assistant-only mask）+ `tools/sft.py`（CPU 自检过，GPU 冒烟待主训练让出显存）。
- **下一步（Day 5）**：主训练收官后 → SFT GPU 冒烟 → 正式 SFT v1（lr 1e-4 / 1 epoch / ≈1.3h）→ 中期评测框架——清单见 HANDOFF §7 · 经验 [notes/lessons.md](notes/lessons.md) · 概念题 [notes/qa-day-3.md](notes/qa-day-3.md)。
- **路线**：Day 3 框架+门① ✅ → Day 4 140M 主训练起跑 → Day 5/6 收官 + SFT v2 → Day 7 LoRA/部署 → Day 8 深化 + 报告 → Day 9 缓冲 → Day 10 收尾。
- 预期管理：140M/30 亿 token ≈ GPT-2 124M 水平（通顺、贫乏）——产出 = 经验 + 亲手训的模型 + 报告 + demo，非对标开源质量

## 文档地图

| 内容 | 位置 |
|---|---|
| 计划 / 决策 / 逐日方案 / 风险 / 素材索引（唯一计划文档） | [PLAN.md](PLAN.md) |
| 会话交接（复现检查 + Day 0 清单 + 波次队列） | [HANDOFF.md](HANDOFF.md) |
| 逐日记账（决策与现象，每天写） | [LAB_NOTEBOOK.md](LAB_NOTEBOOK.md) |
| 训练/评测/数据脚本（Day 1~7 逐步生长） | `tools/` |
| run 证据（只增不改） | `reports/` |
| 学习者 lessons（追加制）+ 概念检验题答案卡 | `notes/` |
| 仓内操作规程（训练跑批/故障速查/红线，agent 优先加载） | [.zcode/skills/pretrain-lab/SKILL.md](.zcode/skills/pretrain-lab/SKILL.md) |
| 数据集落位 + 出处指纹 | `data/`（PROVENANCE.md + SHA256SUMS） |
| 模型/checkpoint/语料（gitignore，脚本可再生） | `models/` · `checkpoints/` |

## 工作方式

develop 主干直提为主（提交信息带 `day-N` 标签）+ 大改走 feature 分支；每晚三道概念检验题（学习者模式）；证据只增不改；**数据指纹每份落位即录**（raw 层 Day 0 已立、字符级切片 Day 1 已立、tokenizer/分片/val Day 2 已录，共 10 条入库）。决策门①（Day 3 吞吐，**140M 等效 ≥35k tok/s**）/②（Day 6 loss）预注册于 PLAN §4/§4.1，跑前不改。仓内操作规程见 [.zcode/skills/pretrain-lab/SKILL.md](.zcode/skills/pretrain-lab/SKILL.md)。
