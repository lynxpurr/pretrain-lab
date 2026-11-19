# HANDOFF — 新会话交接

> 更新：2026-11-19（Day 6 收官）· 本件是新会话的**唯一启动入口**：开工序 + 状态 + 复现检查 + 当日清单 + 锚点。知识本体在 [PLAN.md](PLAN.md)（D-01~D-10 · 逐日方案 · 决策门 · 风险 · 纪律 · 边界），本件只指路不复述；**仓内操作规程（跑批/故障速查/红线）= [.zcode/skills/pretrain-lab/SKILL.md](.zcode/skills/pretrain-lab/SKILL.md)，新会话优先加载**。

## 0. 新会话开工序（按序执行，不跳步）

1. **加载 skill + 读本件 + PLAN 三节**：`.zcode/skills/pretrain-lab/SKILL.md` → 本件 §1（状态）§5（日程）§7（当日清单）→ PLAN §3（D-01~D-10）§4（逐日 + 决策门①②原文）§4.1（门①／门② 判定）§6（纪律）。缺细节回 PLAN，不臆造。
2. **跑 §2 复现检查**（约 1 分钟）——红项先修再开工，不盲目重装（50 系环境坑已全部压到 Day 0 解决，PLAN §5 风险表）。
3. **读前情**：`LAB_NOTEBOOK.md` 最近一日段 + `notes/qa-day-6.md`（若无则读 qa-day-5：昨晚自答暴露的疑问 = 今日选题池）+ `notes/lessons.md` 顶部「跨日回顾 10 条」。
4. **执行当日清单**：按 §5 日程当日行 + §7 当日清单；决策门判定**跑前不改**（PLAN §4 预注册）。若用户要求提前/延后开工，先改 §5 实际日期再执行。
5. **收波**（当日结束前）：`reports/` 证据三分 → LAB_NOTEBOOK 当日段 → lessons（有新教训才写）→ qa 题目池 → PLAN 变更记录 → README 状态 → 指纹补 PROVENANCE → `git commit -m "day-N: …"` + push。
6. **边界提醒**：nl2fem / finetune-lab 是**知识上游非资产上游**（PLAN §7）——只引用知识不改其档案；本仓数据与代码全自建。

**首次回复向用户汇报四件事**：窗口剩余天数 · 上一日结果 · 今日计划 · 待拍板项（如有）。

**新会话首条消息（可直接粘贴）**：

> 读 `/home/zenz/projects/pretrain-lab/HANDOFF.md` 持卡开工：加载 `.zcode/skills/pretrain-lab/SKILL.md`，按 §0 六步开工序执行——§2 复现检查 → 读前情（`LAB_NOTEBOOK.md` Day 5~6 + `notes/qa-day-5.md` + lessons 顶部跨日回顾）→ 执行 §7 Day 7 清单（SFT 数据 v2 → SFT v2 → LoRA → 部署），全程按 §6 惯例与 skill §3.2/§6 执行与收波。

## 1. 状态一段话

**Day 0~6 已全部收官，下一动作 = Day 7（SFT 数据 v2 → SFT v2 → LoRA → GGUF/Ollama/Gradio）**。项目 = 本地 5070 Ti 16GB 上 10 天从零训一个 ~140M 中英小模型（预训练 → SFT → LoRA 对比 → 部署 demo），**学习导向**；底稿 = NoteFlow `WorkingDeck/2026-09/2026-09-22/small-llm-10day-plan.md`。

**当前手里有什么（都能直接跑）**：
- **底座**：`out/main140m/last.pt`（137,847,552 参数 · 3B token · **val 2.7709** · sha `0c0096cc172e8a58`）+ 46 个等间隔 ckpt 谱系（≈73GB）
- **SFT v1**：`out/sft-v1/last.pt`（**SFT val 1.5515** · sha `853322df4583bfa2`）——已能对话、自报身份、解释概念、写简单代码
- **数据**：`data/shards/`（3B 预训练）· `data/sft-mix/`（250,001,408 token SFT，assistant-only mask + 25% 预训练混入）· `data/eval/tests.json`（18 题 / 9 tag）
- **脚本**：`tools/{model,train,sft,eval,build_sft,build_shards,train_tokenizer,train_char20m}.py`
- **决策门**：① **PASS**（140M 52,250 tok/s ≥ 35k）；② **不触发**（不加训 15 亿，双证据 0.0134 / 0.0051）

**关键现状与已知缺陷（Day 5~6 诊断）**：SFT 后题库 6/18 → 16/18（规则分），但质性复核发现 **复读环**（"文化/艺术/交通…"）、**编造推理**、**拒答模板泄漏**、**译错方向**；解码对照证明 **复读不是解码问题**（采样 rep-4 0.123 vs greedy 0.131），来自 SFT 数据的罗列式风格 → **SFT v2 走数据侧**（校准/拒答样本 + 格式硬约束 + 压列表）。

## 2. 复现检查（约 1 分钟，按序）

```bash
cd /home/zenz/projects/pretrain-lab
git branch --show-current && git fetch -q && git status -sb   # develop；应干净、与 origin 同步
nvidia-smi --query-gpu=memory.free --format=csv,noheader       # 常驻在位 ~14GB 空闲（laya-triage ~1.8G）
df -h /home | tail -1                                          # 余量 ≥100GB（语料 + checkpoint）
which tmux || echo tmux-missing
.venv-pre/bin/python -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
                                                               # 应含 cu128 + True + RTX 5070 Ti
ls ~/projects/minimind ~/projects/nanoGPT >/dev/null 2>&1 && echo ref-repos-ok || echo ref-repos-missing
ls data/raw/SHA256SUMS && ls data/raw/ | head -3                # raw 层 37.9GB + 指纹（入库）
ls data/tokenizer-32k/tokenizer.json data/shards/meta.json      # Day 2 tokenizer / 3B 分片
(cd data/shards && sha256sum -c SHA256SUMS | tail -1)           # 应全 OK（~4s）
ls -la out/main140m/last.pt out/sft-v1/last.pt                  # 底座 + SFT v1（各 1.65GB）
ls data/sft-mix/{meta.json,SHA256SUMS} data/eval/tests.json     # SFT 数据 + 评测题库
ls tools/train.py tools/sft.py tools/eval.py tools/build_sft.py # 主线脚本
tmux ls | grep -E "sft|main140m|train" || echo no-running-training
```

- `bad interpreter` = venv 断链（D-07 uv 托管解释器免疫此坑）。
- 分片 `sha256sum -c` 失败 = 数据被动过——**先查再训**（PROVENANCE 纪律）。
- 检查不过 → PLAN §8 环境快照 / §5 风险表；重建命令见 `reports/2026-11-18-day0-env-snapshot.md`。

## 3. 已完成摘要（Day 0~6，细节在证据与笔记，勿重复劳动）

| Day | 内容 | 结果 |
|---|---|---|
| 0（11-18 早） | 环境预铺 + 数据下载 + D-10 拍板 | `.venv-pre`（uv 3.12.13 + torch 2.11.0+cu128）· 数据 37.9GB / 17 条指纹 · 证据 `reports/2026-11-18-day0-env-snapshot.md` |
| 1（11-18） | 手写 `model.py` + 字符级 20M 闭环 | 22,220,544 参数 · val **1.5599** · **187,480 字符/s** · 96.1 min · 证据 `reports/2026-11-18-day1-char20m.*` |
| 2（11-18 续跑） | 32k BPE + 3B memmap 流水线 | zh 1.841 / en 4.226 chars/token · **3,000,000,000 token**（en60/zh40，6×1GB + val 4M）· 构建 20.7min · 冒烟 10.4542 |
| 3（11-18 续跑） | `tools/train.py` + 50M 冒烟/30min + 140M 探针 + **门①** | 50M **120,517 tok/s**（val 3.6377）· 140M **52,250 tok/s → 门① PASS** · 3B 单程 15.9h · 续训 kill→restore val 一字不差 |
| 4（11-18 18:46 → 11-19 10:53） | **140M × 3B 主训练** + SFT 数据 + `sft.py` | **16h07m41s / 52,171 tok/s / val 2.7709 / 0 尖峰 / 46 ckpt ≈73GB** · SFT 数据 250,001,408 token · 证据 `reports/2026-11-19-day4-main140m.md` |
| 5（11-19） | **SFT v1 + 对比评测** | SFT val **1.5515**（3,815 步 / 1h19m）· base→sft：题库 **6/18→16/18**、SFT PPL **9.818→4.596**、预训练 PPL 15.350→16.307（遗忘 +6.2%）· 证据 `reports/2026-11-19-day5-{eval,sft-v1}.*` |
| 6（11-19） | **门② 判定 + 解码对照** | **不加训**（0.0134 / 0.0051 双证据，`reports/2026-11-19-day6-gate2.md`）· 复读归因数据侧（`...-day6-decode.md`）· 评测协议定档 |

## 4. 锚点速查（对账用已知答案）

**环境与数据**

| 锚 | 值 |
|---|---|
| 机器 | .118 · RTX 5070 Ti 16GB · 空闲 ~14GB（laya-triage 1.8G 常驻）· 96GB RAM · 磁盘余 2.2T |
| `.venv-pre` | torch 2.11.0+cu128 · CUDA True · sm_120 · uv CPython 3.12.13 |
| 32k BPE | 词表 32,000 · specials 0/1/2 · zh 1.841 / en 4.226 chars/token · sha `05e9ef17…` |
| 3B 训练集 | 3,000,000,000 token · en 60%/zh 40% · 6×1GB + val 4M · max_id 31999 |
| SFT 集 | **250,001,408 token** = 404,210 会话 + 25% 预训练块 · 监督占比 78.15% · val 2,001,920 token · `data/sft-mix/SHA256SUMS`（4 条） |
| 评测集 | 18 题 / 9 tag · sha `6c5bd1e92e4b4aba` |

**训练与评测**

| 锚 | 值 |
|---|---|
| 主模型配置 | 140M = d768/L16/H12 **137,847,552** · 50M = d576/L8/H9 **50,292,288** · 100M 兜底 = d640/L16/H10 **99,799,680** |
| 门① | 口径 **140M 等效 ≥35k tok/s** → **PASS 52,250**（超 49%）；50M 交叉校验 120,517 ≥ 96k ✓ |
| micro-bs 边界 | 50M = 16（bs24 OOM）· 140M = 8（bs10 需 `expandable_segments`、bs12 OOM；bs16+grad-ckpt 仅 40,449）· `torch.compile` 4,077（弃用） |
| 主训练 | bs8×accum8×T1024 = 65,536 tok/step · 45,777 步 · lr 6e-4/warmup 500/cosine→6e-5 · 16h07m41s · 开销 0.96% · peak 10.51GB |
| 主训练 val | 4.9742@500 → 3.3932@4k → 2.9936@20k → 2.8576@32k → **2.7709@45,777**；末段每 500 步 −0.0009；train 2.677（gap 0.094） |
| 门② | 最后 10% 降幅 **0.0134**（<0.02~0.03）· 恒定 lr 探针 300 步 **0.0051**（上界）→ **不加训** |
| SFT v1 | 3,815 步 / 1h19m26s / 53,004 tok/s / **SFT val 1.5515** / peak 12.09GB |
| 对比评测 | base：预训练 PPL 15.350 · SFT PPL 9.818 · 题库 6/18；sft：16.307（+6.2%）· 4.596 · 16/18（89%） |
| 解码对照 | greedy 16/18（rep-4 0.131）· sample 15/18（0.123）· rp1.1 15/18（0.087）· rp1.2 15/18（0.057）· rp1.3 13/18（0.032） |
| 评测协议 | **greedy + 关键词判分 + distinct-2/rep-4 + 人工 rubric**；demo 端 T0.7/top-p0.9 单独声明 |

**指纹与待办**

| 项 | 值 |
|---|---|
| 数据指纹 | raw 17 · 字符级 3 · tokenizer 3 · 分片 7 · SFT 4 · 评测 1（全部入库，见 `data/PROVENANCE.md` 与各层 `SHA256SUMS`） |
| ckpt 指纹 | char20m `5d97b5f73852a2e9` · 50M `71fc274be289c3c2` · 140M 探针 `df8fc7ac351415db` · **main140m `0c0096cc172e8a58`** · **sft-v1 `853322df4583bfa2`** |
| 待回填 | LoRA 读数（效果/显存/速度）· GGUF/Ollama 可用性 · 三版最终对比表 · 报告成本核算 |
| 参考实现 | minimind @ `233d00f` · nanoGPT @ `3adf61e`（`~/projects/`） |

## 5. 波次队列与日程（**实际窗口 = 11-18 ~ 11-27**）

| 波次 | 内容 | 状态 |
|---|---|---|
| Day 0（11-18 早） | 环境预铺 | ✅ 完成 |
| Day 1（11-18） | 手写 model.py + 字符级 20M 闭环 | ✅ 完成 |
| Day 2（11-18 续跑） | 32k BPE + 3B memmap 数据流水线 | ✅ 完成 |
| Day 3（11-18 续跑） | 训练框架 + 50M 冒烟/30min + 140M 探针 + **门①** | ✅ 完成（门① PASS 52,250） |
| Day 4（11-18 晚 → 11-19 晨） | **140M × 3B 主训练** + SFT 数据/脚本 | ✅ 完成（val 2.7709 / 16h08m / 46 ckpt） |
| Day 5（11-19） | SFT v1 + 评测框架 + 门② 双证据 | ✅ 完成（SFT val 1.5515；题库 33%→89%） |
| Day 6（11-19） | **门② 正式判定** + 解码对照 | ✅ 完成（不加训；复读归因数据侧） |
| **Day 7（11-19 晚 ~ 11-20）** | **SFT 数据 v2 → SFT v2 → LoRA → GGUF/Ollama/Gradio** | **未开工（下一动作，清单 §7）** |
| Day 8（11-21） | 深化（lr 扫参 / tokenizer 消融 / DPO 三选一）+ 报告开写 | 未开工 |
| 机动（11-22 ~ 11-25） | 补实验 / 修质性缺陷 / 评测扩展 / 模型卡 | 未开工（原 Day 9 提前置换） |
| Day 9（11-26） | 硬缓冲（只在出事时用） | 未开工 |
| Day 10（11-27） | 三版对比（base/SFT/LoRA）+ repo 整理 + 报告 | 未开工 |

**关键路径与缓冲（Day 6 实测重算）**：Day 3 框架 + 门① ✅ → Day 4 主训练 3B ✅ → Day 5 SFT v1 + 评测 ✅ → Day 6 门② 判定（不加训）+ 解码对照 ✅ → **Day 7 SFT v2 + LoRA + 部署** → Day 8 深化 + 报告 → Day 10 收尾。**缓冲 = 11-20 ~ 11-22 三天 + Day 9（11-26）硬缓冲**——G3/G4/G6 都有充裕时间，不需要砍项；即使 SFT v2 失败，也可直接用 SFT v1 进 LoRA/部署（**G1/G2/G5 是底线，G3/G4 可降级**）。

## 6. 惯例与红线

- **仓内 skill 优先**：跑批/排障/红线按 `SKILL.md` 执行（含 §3 预训练、§3.2 SFT+评测、§6 收波校准清单）。
- **每晚三道概念检验题**：`notes/qa-day-N.md` 先自答；空洞回 `notes/lessons.md` 补课（追加制带出处）。当前待自答：qa-day-2 ~ qa-day-5。
- **证据纪律**：`reports/` 只增不改（改错走勘误追加）；每次 run 证据三分 = 摘要 md + 曲线 csv + 原始 log。
- **指纹纪律**：每份数据/ckpt 落位即录（`SHA256SUMS` 例外入库；数据本体 gitignore）。
- **git**：develop 直提为主（信息带 `day-N` 标签）；大改走 `feature/day-N-<slug>` → `--no-ff`；模型/checkpoint/语料/日志不入库。
- **决策门**：①/② 均已判定且口径跑前未改（PLAN §4.1）——重开条件见同节，**不得事后改口径**。
- **评测协议**：统一 greedy + 关键词 + distinct-2/rep-4 + 人工 rubric；**不许用解码调参替代数据修复**。
- **上游知识指针**：finetune-lab `notes/lessons.md` · `ms-swift-finetune` skill（D-10 选 B 时）· nl2fem `notes/ref-*-concepts.md`。

## 7. Day 7 清单（SFT v2 数据侧修正 + LoRA + 部署）

> Day 6 清单已收官（门② 不加训；解码对照证伪"greedy 放大复读"），证据见 §3/§4 与 `reports/2026-11-19-day6-{gate2,decode}.md`。

| # | 事项 | 判据 |
|---|---|---|
| 1 | **SFT 数据 v2（CPU，新目录 `data/sft-mix-v2/`，不动 v1）**：①**校准/拒答**——从 404k 会话筛含"不知道/无法/不确定/尚未/没有官方记录"的回答，目标 ≥3,000 条（≈1%），不足则手写 100~200 条；②**格式硬约束**——"只回答…/一句话/不超过…/列出 3 条"类样本上采样 2×；③**压罗列癖**——答案含 ≥5 条编号列表的样本降采样 50%（或过滤），目标列表类占比 ≤15%；④其余不变（25% 预训练块 / assistant-only mask / block 1024 / val 2M） | **供给实测（2026-11-19，会话级 grep）**：不知道 9,438 · 不确定 23,564 · 尚未 5,786 · 没有官方 139 · 只回答 1,703 · 一句话 6,203 · 不超过 18,321 · **含"5."的列表类 258,468（28.5%）** → ①② 供给充足，③ 需砍约一半。其余：新旧统计对比落档；段级 mask 自检 0 违规；`SHA256SUMS` + PROVENANCE；**只改数据，不改 tokenizer/模板/混入比例** |
| 2 | **SFT v2（GPU ~1.3h）**：同底座 `out/main140m/last.pt`、同超参（lr 1e-4 / warmup 100 / 1 epoch over 250M） | 题库 **≥16/18** 且 **rep-4 <0.08**（v1 0.131）；`refuse-unknown` 与 `math-mul` 至少各修好一个；预训练 PPL 退化 ≤10%；`EXIT:0` |
| 3 | **LoRA（D-10 A 手写）**：同底座 + 同 SFT 数据，低秩增量（r=8/16，target = qkv/proj/gate/up/down） | 可训练参数 <2%；50 步冒烟 loss 下降；与全参 SFT 同题库对比（效果/显存/速度三读数） |
| 4 | **GGUF → Ollama → Gradio**（G4，超期可砍） | `llama.cpp` 转 Q4_K_M（Q8_0 对照）· Ollama 能对话 · Gradio 本地 URL 可访问 |
| 5 | 评测扩展 | distinct-2/rep-4 已在 `eval.py`；补人工 rubric 表（reports/）供 Day 10 复用 |
| 6 | 收波 | 证据三分 + 笔记本 + PLAN/HANDOFF/README + 指纹 + commit |

**Day 7 决策点**：①SFT v2 校准样本来源（默认先筛现有数据、不足再手写）；②LoRA 秩（默认 r=8）；③量化档位（默认 Q4_K_M，Q8_0 对照）。

**若 SFT v2 来不及**：直接用 SFT v1 进 LoRA/部署（G3/G4 优先），v2 降级为 Day 8 深化项。