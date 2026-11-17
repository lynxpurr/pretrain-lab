# HANDOFF — 新会话交接

> 更新：2026-11-18（立项建立，文档就绪，待启动拍板）· 本件是新会话的**唯一启动入口**：状态一段话 + 复现检查 + 启动清单。知识本体在 [PLAN.md](PLAN.md)（决策 D-01~D-10、逐日方案、风险、纪律、边界），本件只指路不复述。

## 1. 状态一段话

**pretrain-lab 已立项（2026-11-18），文档就绪，尚未开工**——小模型从零训练 10 天行动（~140M 手写预训练 → SFT → LoRA 对比 → GGUF/Ollama demo），底稿 = NoteFlow `WorkingDeck/2026-09/2026-09-22/small-llm-10day-plan.md`（2026-09-22 定稿）。热身两仓（nl2fem + finetune-lab，均 2026-09-27 收官）已把 SFT 半场预付完毕（素材按 Day 编目，PLAN §7 素材索引）；本仓主战场 = 从零预训练三件套（手写 model.py / BPE tokenizer / memmap 数据流水线）+ 部署链 + 训练报告。**当前待办：①启动时机拍板（10 天连续窗口是日程性约束，Day 9 缓冲日为硬保险）；②Day 0 环境预铺（见 §3 清单）；③D-10 SFT 载具（手写 vs ms-swift）Day 4 前拍板即可，不阻塞开工。**

## 2. 复现检查（约 1 分钟，按序）

```bash
cd /home/zenz/projects/pretrain-lab
git branch --show-current && git fetch -q && git status -sb   # develop；应干净
nvidia-smi --query-gpu=memory.free --format=csv,noheader       # 常驻在位 ~14GB 空闲（laya-triage ~1.8G）
df -h /home | tail -1                                          # 磁盘余量 ≥100GB（语料 + checkpoint 滚动存档）
which tmux || echo tmux-missing                                # Day 0 前应装好
# Day 0 完成后追加：
.venv-pre/bin/python -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
                                                               # 应含 cu128 + True + RTX 5070 Ti
ls ~/projects/minimind ~/projects/nanoGPT >/dev/null 2>&1 && echo ref-repos-ok || echo ref-repos-missing
ls data/raw/ >/dev/null 2>&1 && ls data/raw | head -3          # 数据集预下载落位
```

- **venv 断链检查内嵌**：`.venv-pre/bin/python` 若报 `bad interpreter` = 底层 python 消失（nl2fem 2026-11-18 教训，PLAN 风险表）——D-07 规定 uv 托管解释器免疫此坑，出现即说明建 venv 时违反 D-07。
- 检查不过 → 回 PLAN §8 环境快照与 §5 风险表（50 系环境坑全部压到 Day 0 解决），不要盲目重装。
- 新会话开工前重读本件 + PLAN §3（决策）+ §6（纪律）+ 当日 `LAB_NOTEBOOK.md` 前情。

## 3. 启动清单（Day 0，约一晚）

| # | 事项 | 判据 |
|---|---|---|
| 0 | **启动时机拍板**（用户）：确认 10 天连续窗口的起止日期，填入本表与 PLAN 变更记录 | 起止日期落档 |
| 1 | 驱动/CUDA/torch cu128 栈验证：`.venv-pre` 建立（**D-07：uv 托管解释器**，`UV_TORCH_BACKEND=cu128` + 阿里云双镜像，命令参照 finetune-lab PLAN §9 换 venv 名） | `torch.cuda.is_available()` True + sm_120 在 arch list + 小矩阵运算过 |
| 2 | tmux 就绪 + 激进风扇曲线 | 复现检查绿 |
| 3 | clone 参考实现：minimind + nanoGPT（D-08） | 两目录在位 |
| 4 | 数据集预下载（D-06：FineWeb-Edu sample / SkyPile 或 minimind pretrain_hq / SFT 数据；`HF_ENDPOINT=hf-mirror` 或 ModelScope 直连） | 落 `data/raw/`，指纹录 `data/PROVENANCE.md` |
| 5 | D-10 SFT 载具拍板（可推迟到 Day 4 前；倾向 = A 手写为主 B 对照兜底，PLAN D-10） | 决策入 PLAN §3 |
| 6 | `LAB_NOTEBOOK.md` Day 0 段落记 | 当日决策与现象入册 |

## 4. 锚点速查（对账用的已知答案，随执行回填）

| 锚 | 值 | 出处 |
|---|---|---|
| 机器基线 | .118 · RTX 5070 Ti 16GB · 空闲 ~14GB（laya-triage 常驻 ~1.8G，tei 容器不在位） | 2026-11-18 实测（finetune-lab 复现检查同日留痕） |
| 50 系栈验证 | cu128/sm_120 全套（ms-swift 4.5.3 + torch 2.11.0+cu128）在 finetune-lab `.venv-swift` 实证可用 | finetune-lab PLAN §9 |
| 热身收官锚 | nl2fem develop @ `1ea5401`（Phase 5 全收）· finetune-lab develop @ `cc5201c`（收尾复核批） | 两仓 git log 2026-11-18 |
| （执行中回填：字符级 20M loss 轨迹 / 50M 吞吐 / 140M 总时长 / 各版评测读数） | | |

## 5. 波次队列（预注册，开工后逐日回填状态）

| 波次 | 内容 | 状态 |
|---|---|---|
| Day 0 | 环境预铺（§3 清单） | 待启动拍板 |
| Day 1 | 手写 model.py + 字符级 20M 最小闭环 | 未开工 |
| Day 2 | 32k BPE tokenizer + memmap 数据流水线 | 未开工 |
| Day 3 | 训练框架 + 50M 冒烟 + **决策门①** | 未开工 |
| Day 4 | 140M 主训练启动 + SFT 准备（D-10 拍板） | 未开工 |
| Day 5 | 中期 SFT + 评测框架 | 未开工 |
| Day 6 | 主训练收官 + SFT v2 + **决策门②** | 未开工 |
| Day 7 | LoRA 对比 + GGUF/Ollama/Gradio 部署 | 未开工（超期可砍） |
| Day 8 | 深化（扫参/tokenizer 消融/DPO）+ 报告开写 | 未开工（超期可砍） |
| Day 9 | 硬缓冲日 | 未开工 |
| Day 10 | 收尾：最终对比 + repo 整理 + 报告 | 未开工 |

## 6. 惯例

- 每晚三道概念检验题（`notes/qa-day-N.md`，先自答；理解空洞回 `notes/lessons.md` 补课，追加制带出处）。
- 证据纪律：`reports/` 只增不改；数据/模型指纹录 `data/PROVENANCE.md`。
- 提交：develop 直提为主（信息带 `day-N` 标签）；大改走 `feature/day-N-<slug>` → `--no-ff`。
- 远端：GitHub `lynxpurr/pretrain-lab`（**私有**）· 默认分支 = **develop**。
- 上游知识指针：finetune-lab `notes/lessons.md`（四杠杆×四失败轴地图 v4 + OOD 三层分解）· `ms-swift-finetune` skill · nl2fem `notes/ref-*-concepts.md`（按需回看）。
