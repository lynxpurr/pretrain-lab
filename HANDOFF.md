# HANDOFF — 新会话交接

> 更新：2026-11-18（**提前起跑：Day 1 = 2026-11-18（周三）~ Day 10 = 2026-11-27（周四）**，Day 9 缓冲 = 11-26；D-10 = A 手写为主 B 兜底；Day 0 环境预铺 + Day 1 字符级 20M 闭环均已收官）· 本件是新会话的**唯一启动入口**：开工序 + 状态一段话 + 复现检查 + Day 0 清单（已留档）+ **Day 2 清单（§7，次日开工看这里）**。知识本体在 [PLAN.md](PLAN.md)（决策 D-01~D-10、逐日方案、风险、纪律、边界），本件只指路不复述；仓内操作规程 = [.zcode/skills/pretrain-lab/SKILL.md](.zcode/skills/pretrain-lab/SKILL.md)。

## 0. 新会话开工序（持本件开工——按序执行，不跳步）

1. **先读本件 + PLAN 三节**：§3（决策 D-01~D-10，特别是 D-07 venv 纪律与 D-10 待拍板项）· §4（逐日方案 + 决策门①②原文）· §6（纪律与边界）。不复述，缺细节回 PLAN。**仓内操作规程（训练跑批/故障速查/红线）= [.zcode/skills/pretrain-lab/SKILL.md](.zcode/skills/pretrain-lab/SKILL.md)**——本仓开工优先加载。
2. **跑 §2 复现检查**（约 1 分钟）——红了先修再开工（50 系环境坑全部压到 Day 0 解决，PLAN §5 风险表）。
3. **与用户确认启动时机**：10 天连续窗口的起止日期（唯一日程性 gate，Day 9 缓冲为硬保险）。拍板后：起止日期写进本件 §1 与 §5 波次队列（换算实际日期）、PLAN 变更记录补一行。
4. **执行 Day 0 环境预铺（§3 六项清单）**——可在 Day 1 前任意时点完成，不占 10 天窗口；其中 `.venv-pre` 必须遵守 D-07（uv 托管解释器，不链 `/usr/bin/python*`——nl2fem 2026-11-18 双 venv 断链教训）。
5. **开工当日（Day 1 起）收波惯例**：LAB_NOTEBOOK 当日记账 · 每晚三道概念检验题（`notes/qa-day-N.md` 先自答）· `reports/` 只增不改 · develop 直提带 `day-N` 标签。
6. **边界提醒**：nl2fem / finetune-lab 是**知识上游非资产上游**（PLAN §7）——素材按 Day 编目取用（PLAN §7 索引），只引用知识不改其档案；本仓数据与代码全自建。

## 1. 状态一段话

**pretrain-lab 已开工（2026-11-18），Day 0 + Day 1 已收官**——小模型从零训练 10 天行动（~140M 手写预训练 → SFT → LoRA 对比 → GGUF/Ollama demo），底稿 = NoteFlow `WorkingDeck/2026-09/2026-09-22/small-llm-10day-plan.md`（2026-09-22 定稿）。热身两仓（nl2fem + finetune-lab，均 2026-09-27 收官）已把 SFT 半场预付完毕（素材按 Day 编目，PLAN §7 素材索引）；本仓主战场 = 从零预训练三件套（手写 model.py ✓ / BPE tokenizer / memmap 数据流水线）+ 部署链 + 训练报告。**窗口已拍板（2026-11-18 晨两道拍板：提前起跑）：Day 1 = 2026-11-18（周三）~ Day 10 = 2026-11-27（周四），Day 0 = 同日早（不占窗口）；Day 9 缓冲日 = 11-26 硬保险。D-10 已拍板 = A 手写为主、B ms-swift 兜底（PLAN §3）。Day 1（11-18）✅ 收官：手写 model.py（22.2M 参数）+ 字符级 20M 闭环（96.1min / 187,480 字符/s / val 1.5599），证据 reports/2026-11-18-day1-char20m.md；下一步 = Day 2 BPE tokenizer + memmap 流水线（§7 清单）。**

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
ls data/day1-char20m/train.bin data/day1-char20m/meta.json     # Day 1 字符级数据在位
ls -la out/day1-char20m/last.pt                                # Day 1 终版 checkpoint（267MB）
```

- **venv 断链检查内嵌**：`.venv-pre/bin/python` 若报 `bad interpreter` = 底层 python 消失（nl2fem 2026-11-18 教训，PLAN 风险表）——D-07 规定 uv 托管解释器免疫此坑，出现即说明建 venv 时违反 D-07。
- 检查不过 → 回 PLAN §8 环境快照与 §5 风险表（50 系环境坑全部压到 Day 0 解决），不要盲目重装。
- 新会话开工前重读本件 + PLAN §3（决策）+ §6（纪律）+ 当日 `LAB_NOTEBOOK.md` 前情。

## 3. 启动清单（Day 0，约一晚）

| # | 事项 | 判据 |
|---|---|---|
| 0 | **启动时机拍板**（用户）：✅ 2026-11-18 两道拍板——先定 11-19~11-28，同日晨用户改判"现在开工"提前起跑 = **Day 1 = 2026-11-18（周三）~ Day 10 = 2026-11-27（周四）**（原判作废，§1/§5 已换算） | 起止日期落档 ✓ |
| 1 | 驱动/CUDA/torch cu128 栈验证：✅ `.venv-pre` 建立（D-07：uv 托管 CPython 3.12.13，`UV_TORCH_BACKEND=cu128` + 阿里云双镜像，装法平移 finetune-lab PLAN §9） | ✅ CUDA True + sm_120 在 arch list + bf16 矩阵过（torch 2.11.0+cu128；证据 = reports/2026-11-18-day0-env-snapshot.md） |
| 2 | tmux 就绪 + 激进风扇曲线 | tmux ✅（/usr/bin/tmux）；**风扇曲线 = 用户侧待办**（明日开训前调好） |
| 3 | clone 参考实现：✅ minimind @ `233d00f` + nanoGPT @ `3adf61e`（D-08，落 `~/projects/`） | 两目录在位 ✓ |
| 4 | 数据集预下载：✅ FineWeb-Edu sample-10BT 27.85GB + minimind pretrain_t2t 8.28GB + sft_t2t_mini 1.74GB + dpo 0.05GB（D-06；ModelScope 无 minimind_dataset → 回落 hf-mirror） | 落 `data/raw/` ✓；指纹录 `data/raw/SHA256SUMS`（17 条）+ `data/PROVENANCE.md` ✓ |
| 5 | D-10 SFT 载具拍板：✅ 2026-11-18 拍板 = **A 手写为主、B ms-swift 对照/兜底**（PLAN §3 已更新） | 决策入 PLAN §3 ✓ |
| 6 | `LAB_NOTEBOOK.md` Day 0 段落记：✅ | 当日决策与现象入册 ✓ |

## 4. 锚点速查（对账用的已知答案，随执行回填）

| 锚 | 值 | 出处 |
|---|---|---|
| 机器基线 | .118 · RTX 5070 Ti 16GB · 空闲 ~14GB（laya-triage 常驻 ~1.8G，tei 容器不在位） | 2026-11-18 实测（finetune-lab 复现检查同日留痕） |
| 50 系栈验证 | cu128/sm_120 全套（ms-swift 4.5.3 + torch 2.11.0+cu128）在 finetune-lab `.venv-swift` 实证可用 | finetune-lab PLAN §9 |
| 本仓 `.venv-pre` 栈验证 | torch 2.11.0+cu128 · CUDA True · sm_120 在 arch list · bf16 矩阵过（uv 托管 3.12.13，GPU 空闲 13.4GiB） | reports/2026-11-18-day0-env-snapshot.md（2026-11-18） |
| 热身收官锚 | nl2fem develop @ `1ea5401`（Phase 5 全收）· finetune-lab develop @ `cc5201c`（收尾复核批） | 两仓 git log 2026-11-18 |
| （执行中回填：字符级 20M loss 轨迹 / 50M 吞吐 / 140M 总时长 / 各版评测读数） | | |
| 字符级 20M（Day 1，22.2M 参数 / 词表 11,765 / bs64×512） | 首步 loss 9.4316（vs ln(11765)=9.3727）· val 2.0414(2.5k)→1.6865(20k)→**1.5599(33k)** · **187,480 字符/秒** · 96.1 min / 10.8 亿字符 · GPU 57°C | reports/2026-11-18-day1-char20m.md |

## 5. 波次队列（预注册，开工后逐日回填状态）

| 波次 | 内容 | 状态 |
|---|---|---|
| Day 0（11-18 早） | 环境预铺（§3 清单） | ✅ 完成 |
| Day 1（11-18） | 手写 model.py + 字符级 20M 最小闭环 | ✅ 完成（22.2M 参数 / 96.1min / 187,480 字符/s / val 1.5599） |
| Day 2（11-19） | 32k BPE tokenizer + memmap 数据流水线 | 未开工（清单见 §7） |
| Day 3（11-20） | 训练框架 + 50M 冒烟 + **决策门①** | 未开工 |
| Day 4（11-21） | 140M 主训练启动 + SFT 准备（D-10 已拍：A 主 B 兜底） | 未开工 |
| Day 5（11-22） | 中期 SFT + 评测框架 | 未开工 |
| Day 6（11-23） | 主训练收官 + SFT v2 + **决策门②** | 未开工 |
| Day 7（11-24） | LoRA 对比 + GGUF/Ollama/Gradio 部署 | 未开工（超期可砍） |
| Day 8（11-25） | 深化（扫参/tokenizer 消融/DPO）+ 报告开写 | 未开工（超期可砍） |
| Day 9（11-26） | 硬缓冲日 | 未开工 |
| Day 10（11-27） | 收尾：最终对比 + repo 整理 + 报告 | 未开工 |

## 6. 惯例

- 每晚三道概念检验题（`notes/qa-day-N.md`，先自答；理解空洞回 `notes/lessons.md` 补课，追加制带出处）。
- 证据纪律：`reports/` 只增不改；数据/模型指纹录 `data/PROVENANCE.md`。
- 提交：develop 直提为主（信息带 `day-N` 标签）；大改走 `feature/day-N-<slug>` → `--no-ff`。
- 远端：GitHub `lynxpurr/pretrain-lab`（**私有**）· 默认分支 = **develop**。
- 上游知识指针：finetune-lab `notes/lessons.md`（四杠杆×四失败轴地图 v4 + OOD 三层分解）· `ms-swift-finetune` skill · nl2fem `notes/ref-*-concepts.md`（按需回看）。

## 7. Day 2 开工清单（2026-11-19 · 32k BPE tokenizer + memmap 数据流水线）

> 直接沿用 §0 开工序：读本件 + PLAN 三节 → §2 复现检查 → 收波惯例；逐日事项看本表。

| # | 事项 | 判据 |
|---|---|---|
| 1 | `tools/train_tokenizer.py`：HF tokenizers 训 32k 中英 BPE（D-03）；语料采样 = pretrain_t2t 抽样 + fineweb-edu 前若干分片抽样（en/zh 各 ~200MB 量级即可） | 词表 32k 落位（tokenizer.json + vocab）；zh/en 压缩率读数（chars/token）落 reports/ |
| 2 | 压缩率对拍：与 minimind 现成 tokenizer（其 `trainer/train_tokenizer.py` 可参考 D-08）对拍同一段中英文本 | 同文 token 数同量级（±30% 内）；显著偏离 = 特殊 token/归一化/字节回退配置错 |
| 3 | 数据混配比拍板（D-06 补充决策）：起手值 **en:zh ≈ 6:4，目标 30±10 亿 token**；用实测压缩率校准取样量 | 配比 + 依据入 LAB_NOTEBOOK；PROVENANCE 预训练语料表补 token 实测数（qa-day-1 题 3 收口） |
| 4 | 清洗/去重轻量版（Day 2 范围收敛：精确/哈希去重即可，MinHash 全量可吃 Day 9 缓冲） | 去重率读数落档 |
| 5 | token 化 → uint16 memmap 分片落 `data/shards/`（PLAN §6-6 指纹纪律今日起立） | 分片指纹录 `data/PROVENANCE.md` + `data/shards/SHA256SUMS` |
| 6 | 换轨检查：BPE 流水线喂同款 `tools/train_char20m.py` 短冒烟（模型实现 tokenizer 无关，只换 vocab_size） | loss 曲线形态正常（首步 ≈ ln(32000) ≈ 10.4） |

**Day 2 决策点提醒**：中文主力 = pretrain_t2t（已下 8.28GB）——SkyPile 是否补下载看实测混配比缺口再定，不预下载；fineweb-edu 27.85GB 已在位，若 6:4 配比下 en 缺口大，优先增抽 sample-10BT 分片复用而非另开渠道。
