# HANDOFF — 新会话交接

> 更新：2026-11-18（Day 1 收官 + 校准批 @ `31ee2e4`）· 本件是新会话的**唯一启动入口**：开工序 + 状态 + 复现检查 + 当日清单 + 锚点。知识本体在 [PLAN.md](PLAN.md)（决策 D-01~D-10、逐日方案、决策门、风险、纪律、边界），本件只指路不复述；**仓内操作规程（跑批/故障速查/红线）= [.zcode/skills/pretrain-lab/SKILL.md](.zcode/skills/pretrain-lab/SKILL.md)，新会话优先加载**。

## 0. 新会话开工序（按序执行，不跳步）

1. **加载 skill + 读本件 + PLAN 三节**：`.zcode/skills/pretrain-lab/SKILL.md` → 本件 §1（状态）§5（波次）§7（当日清单）→ PLAN §3（D-01~D-10）§4（逐日 + 决策门①②原文）§6（纪律）。缺细节回 PLAN，不臆造。
2. **跑 §2 复现检查**（约 1 分钟）——红项先修再开工，不盲目重装（50 系环境坑已全部压到 Day 0 解决，PLAN §5 风险表）。
3. **读前情**：`LAB_NOTEBOOK.md` 最近一日段 + `notes/qa-day-(N-1).md`（昨晚自答暴露的疑问 = 今日选题池）+ `notes/lessons.md`（可复用教训）。
4. **执行当日清单**：按 §5 波次队列当日行 + §7 模式化的当日清单；决策门判定**跑前不改**（PLAN §4 预注册）。若用户要求提前/延后开工，先改 §5 实际日期再执行。
5. **收波**（当日结束前）：`reports/` 证据三分 → LAB_NOTEBOOK 当日段 → lessons（有新教训才写）→ qa 题目池 → PLAN 变更记录（有决策/日期变更才写）→ README 状态 → 指纹补 PROVENANCE → `git commit -m "day-N: …"` + push。
6. **边界提醒**：nl2fem / finetune-lab 是**知识上游非资产上游**（PLAN §7）——只引用知识不改其档案；本仓数据与代码全自建。

**首次回复向用户汇报四件事**：窗口剩余天数 · 上一日结果 · 今日计划 · 待拍板项（如有）。

## 1. 状态一段话

**pretrain-lab 进行中：Day 0 + Day 1 已收官，当前无在跑任务，下一动作 = Day 2（§7）**——小模型从零训练 10 天行动（~140M 预训练 → SFT → LoRA 对比 → GGUF/Ollama demo），底稿 = NoteFlow `WorkingDeck/2026-09/2026-09-22/small-llm-10day-plan.md`。**窗口（2026-11-18 晨提前起跑拍板）**：Day 1 = 2026-11-18（周三）~ **Day 10 = 2026-11-27（周四）**，Day 9（11-26）硬缓冲。**D-10 已拍板** = A 手写 SFT 为主、B ms-swift 对照/兜底（PLAN §3）。**Day 1 结果**：手写 `tools/model.py`（D-02 全套，22,220,544 参数）+ 字符级 20M 闭环（33,000 步 / 96.1 min / **187,480 字符/秒** / **val 1.5599**），证据 `reports/2026-11-18-day1-char20m.md`。主战场剩余 = BPE tokenizer + memmap 流水线（Day 2）→ 训练框架 + 决策门①（Day 3）→ 140M 主训练（Day 4 起）。

## 2. 复现检查（约 1 分钟，按序）

```bash
cd /home/zenz/projects/pretrain-lab
git branch --show-current && git fetch -q && git status -sb   # develop；应干净、与 origin 同步
nvidia-smi --query-gpu=memory.free --format=csv,noheader       # 常驻在位 ~14GB 空闲（laya-triage ~1.8G）
df -h /home | tail -1                                          # 余量 ≥100GB（语料 + checkpoint 滚动）
which tmux || echo tmux-missing
.venv-pre/bin/python -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
                                                               # 应含 cu128 + True + RTX 5070 Ti
ls ~/projects/minimind ~/projects/nanoGPT >/dev/null 2>&1 && echo ref-repos-ok || echo ref-repos-missing
ls data/raw/ | head -3 && ls data/raw/SHA256SUMS                # raw 层 36GB + 指纹（入库）
ls data/day1-char20m/train.bin data/day1-char20m/meta.json      # Day 1 字符级数据
ls -la out/day1-char20m/last.pt                                 # Day 1 终版 checkpoint（267MB）
tmux ls | grep -E "day|train" || echo no-running-training       # 无在跑任务 = 干净起点
```

- `bad interpreter` = venv 断链（D-07 uv 托管解释器免疫此坑；出现即建 venv 时违反 D-07）。
- 检查不过 → 回 PLAN §8 环境快照 / §5 风险表；重建命令见 `reports/2026-11-18-day0-env-snapshot.md`。

## 3. 已完成摘要（Day 0~1，细节在证据与笔记，勿重复劳动）

| Day | 内容 | 结果 |
|---|---|---|
| 0（11-18 早） | 环境预铺：`.venv-pre`（uv 托管 3.12.13 + torch 2.11.0+cu128）· 参考仓 clone · 数据 37.9GB + 17 条指纹 · D-10 拍板 | 全绿，证据 `reports/2026-11-18-day0-env-snapshot.md`；记账 LAB_NOTEBOOK Day 0 |
| 1（11-18） | 手写模型 + 字符级 20M 闭环：`tools/{model,prepare_char20m,train_char20m}.py` | 22.2M 参数；loss 9.4316→val 1.5599；187,480 字符/s；96.1 min；证据 `reports/2026-11-18-day1-char20m.{md,csv,log}` |
| 1 收波校准 | 仓内 skill 建立 · 文档漂移 4 处 + gitignore 指纹漏洞修复 · lessons 8 条 | `31ee2e4` |

## 4. 锚点速查（对账用已知答案）

| 锚 | 值 | 出处 |
|---|---|---|
| 机器基线 | .118 · RTX 5070 Ti 16GB · 空闲 ~14GB（laya-triage 常驻 1.8G）· 96GB RAM · 磁盘余 2.3T | 2026-11-18 实测 |
| `.venv-pre` 栈 | torch 2.11.0+cu128 · CUDA True · sm_120 在 arch list · bf16 矩阵过 · uv CPython 3.12.13 | `reports/2026-11-18-day0-env-snapshot.md` |
| **字符级 20M 基线**（Day 1） | 22.2M 参数 / 词表 11,765 / bs64×512：首步 **9.4316**（vs ln(11765)=9.3727）· val **1.5599** @33k · **187,480 字符/秒** · 96.1 min / 10.8 亿字符 · GPU 57°C / ~15GB | `reports/2026-11-18-day1-char20m.md` |
| 参考实现 | minimind @ `233d00f` · nanoGPT @ `3adf61e`（`~/projects/`；minimind 数据现行名 = `pretrain_t2t(_mini)/sft_t2t(_mini)`） | Day 0 clone |
| 数据指纹 | raw 层 17 条 = `data/raw/SHA256SUMS`（入库）· 字符级 3 条 = `data/day1-char20m/SHA256SUMS`（入库）· checkpoint `last.pt` = `5d97b5f73852a2e9` | `data/PROVENANCE.md` |
| 热身收官 | nl2fem develop @ `1ea5401` · finetune-lab develop @ `cc5201c` | 两仓 git log |
| 待回填 | 50M 吞吐（Day 3）· 140M 总时长（Day 4~6）· 各版评测读数（Day 5~10） | — |

## 5. 波次队列（逐日回填；**实际窗口 = 11-18 ~ 11-27**）

| 波次 | 内容 | 状态 |
|---|---|---|
| Day 0（11-18 早） | 环境预铺 | ✅ 完成 |
| Day 1（11-18） | 手写 model.py + 字符级 20M 最小闭环 | ✅ 完成（22.2M / 96.1min / 187,480 字符/s / val 1.5599） |
| Day 2（11-19） | 32k BPE tokenizer + memmap 数据流水线 | **未开工（下一动作，清单 §7）** |
| Day 3（11-20） | 训练框架 + 50M 冒烟 + **决策门①**（≥3.5 万 token/s 否则缩 100M/20 亿） | 未开工 |
| Day 4（11-21） | 140M 主训练启动 + SFT 准备（D-10 = A 主 B 兜底） | 未开工 |
| Day 5（11-22） | 中期 SFT + 评测框架 | 未开工 |
| Day 6（11-23） | 主训练收官 + SFT v2 + **决策门②**（loss 仍陡降 → 加训 15 亿） | 未开工 |
| Day 7（11-24） | LoRA 对比 + GGUF/Ollama/Gradio 部署 | 未开工（超期可砍） |
| Day 8（11-25） | 深化（扫参/tokenizer 消融/DPO）+ 报告开写 | 未开工（超期可砍） |
| Day 9（11-26） | 硬缓冲日 | 未开工 |
| Day 10（11-27） | 收尾：最终对比 + repo 整理 + 报告 | 未开工 |

## 6. 惯例与红线

- **仓内 skill 优先**：跑批/排障/红线按 `SKILL.md` 执行（本件不重复）。
- **每晚三道概念检验题**：`notes/qa-day-N.md` 先自答；空洞回 `notes/lessons.md` 补课（追加制带出处）。
- **证据纪律**：`reports/` 只增不改（改错走勘误追加）；每次 run 证据三分 = 摘要 md + 曲线 csv + 原始 log。
- **指纹纪律**：每份数据落位即录（`SHA256SUMS` 例外入库；数据本体 gitignore）。
- **git**：develop 直提为主（信息带 `day-N` 标签）；大改走 `feature/day-N-<slug>` → `--no-ff`；模型/checkpoint/语料/日志不入库。
- **决策门预注册**：门①（Day 3 吞吐）/门②（Day 6 loss）跑前不改。
- **上游知识指针**：finetune-lab `notes/lessons.md`（四杠杆×四失败轴 + OOD 三层）· `ms-swift-finetune` skill（D-10 选 B 时）· nl2fem `notes/ref-*-concepts.md`。

## 7. Day 2 开工清单（2026-11-19 · 32k BPE tokenizer + memmap 数据流水线）

| # | 事项 | 判据 |
|---|---|---|
| 1 | `tools/train_tokenizer.py`：HF tokenizers 训 32k 中英 BPE（D-03）；语料采样 = pretrain_t2t + fineweb-edu 分片各抽 ~200MB 量级 | 词表 32k 落位（tokenizer.json + vocab）；zh/en 压缩率（chars/token）落 reports/ |
| 2 | 压缩率对拍 minimind 现成 tokenizer（`~/projects/minimind/trainer/train_tokenizer.py` 可参考，D-08） | 同文 token 数 ±30% 内；偏离 = 特殊 token/归一化/字节回退配置错 |
| 3 | 混配比拍板（D-06 补充）：起手 **en:zh ≈ 6:4，目标 30±10 亿 token**，按实测压缩率校准取样量 | 配比 + 依据入 LAB_NOTEBOOK；PROVENANCE 补 token 实测数（qa-day-1 题 3 收口） |
| 4 | 清洗/去重轻量版（精确/哈希；MinHash 全量留 Day 9 缓冲） | 去重率读数落档 |
| 5 | token 化 → uint16 memmap 分片落 `data/shards/` | 分片指纹录 `data/PROVENANCE.md` + `data/shards/SHA256SUMS`（入库） |
| 6 | 换轨检查：BPE 数据喂同款训练脚本短冒烟（只换 `--data-dir`/vocab） | 首步 loss ≈ ln(32000) ≈ **10.37**（锚定检查） |

**Day 2 决策点**：①SkyPile 不预下载——看 6:4 实测缺口再定；②fineweb-edu 27.85GB 已在位，en 缺口优先增抽 sample-10BT 分片；③分片长度/分片数按 96GB 内存定（Day 2 现场拍）。
