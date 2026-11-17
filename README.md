# pretrain-lab — 小模型从零训练 10 天行动

> 建立：2026-11-18 · 一句话：本地 5070 Ti 16GB 上，10 天完整经历 **~140M 从零预训练 → SFT → LoRA 对比 → 部署 demo** 全生命周期。**学习导向**。
> 底稿：NoteFlow `WorkingDeck/2026-09/2026-09-22/small-llm-10day-plan.md` · 热身：nl2fem + finetune-lab（均 2026-09-27 收官，SFT 半场已预付，本仓主攻从零预训练半场）。

## 状态快照（2026-11-18 · 立项就绪，待启动）

- **文档就绪**：[PLAN.md](PLAN.md)（D-01~D-10 决策 + 逐日方案 + 风险 + 素材索引）· [HANDOFF.md](HANDOFF.md)（启动入口 + Day 0 清单 + 波次队列）· [LAB_NOTEBOOK.md](LAB_NOTEBOOK.md)（逐日记账）· [notes/lessons.md](notes/lessons.md)（学习者模式）· [data/PROVENANCE.md](data/PROVENANCE.md)（指纹纪律）
- **待办**：①启动时机拍板（10 天连续窗口）；②Day 0 环境预铺（HANDOFF §3 六项清单）；③D-10 SFT 载具（手写 vs ms-swift）Day 4 前拍板
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
| 数据集落位 + 出处指纹 | `data/`（PROVENANCE.md + SHA256SUMS） |
| 模型/checkpoint/语料（gitignore，脚本可再生） | `models/` · `checkpoints/` |

## 工作方式

develop 主干直提为主（提交信息带 `day-N` 标签）+ 大改走 feature 分支；每晚三道概念检验题（学习者模式）；证据只增不改；数据指纹从 Day 2 起立。决策门①（Day 3 吞吐）/②（Day 6 loss）预注册于 PLAN §4，跑前不改。
