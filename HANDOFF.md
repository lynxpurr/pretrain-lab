# HANDOFF — 新会话交接

> 更新：2026-11-18（Day 3 收官）· 本件是新会话的**唯一启动入口**：开工序 + 状态 + 复现检查 + 当日清单 + 锚点。知识本体在 [PLAN.md](PLAN.md)（决策 D-01~D-10、逐日方案、决策门、风险、纪律、边界），本件只指路不复述；**仓内操作规程（跑批/故障速查/红线）= [.zcode/skills/pretrain-lab/SKILL.md](.zcode/skills/pretrain-lab/SKILL.md)，新会话优先加载**。

## 0. 新会话开工序（按序执行，不跳步）

1. **加载 skill + 读本件 + PLAN 三节**：`.zcode/skills/pretrain-lab/SKILL.md` → 本件 §1（状态）§5（波次）§7（当日清单）→ PLAN §3（D-01~D-10）§4（逐日 + 决策门①②原文）§4.1（门①口径校准）§6（纪律）。缺细节回 PLAN，不臆造。
2. **跑 §2 复现检查**（约 1 分钟）——红项先修再开工，不盲目重装（50 系环境坑已全部压到 Day 0 解决，PLAN §5 风险表）。
3. **读前情**：`LAB_NOTEBOOK.md` 最近一日段 + `notes/qa-day-(N-1).md`（昨晚自答暴露的疑问 = 今日选题池）+ `notes/lessons.md`（可复用教训）。
4. **执行当日清单**：按 §5 波次队列当日行 + §7 模式化的当日清单；决策门判定**跑前不改**（PLAN §4 预注册）。若用户要求提前/延后开工，先改 §5 实际日期再执行。
5. **收波**（当日结束前）：`reports/` 证据三分 → LAB_NOTEBOOK 当日段 → lessons（有新教训才写）→ qa 题目池 → PLAN 变更记录（有决策/日期变更才写）→ README 状态 → 指纹补 PROVENANCE → `git commit -m "day-N: …"` + push。
6. **边界提醒**：nl2fem / finetune-lab 是**知识上游非资产上游**（PLAN §7）——只引用知识不改其档案；本仓数据与代码全自建。

**首次回复向用户汇报四件事**：窗口剩余天数 · 上一日结果 · 今日计划 · 待拍板项（如有）。

**新会话首条消息（可直接粘贴，日期/前情按实际改）**：

> 读 `/home/zenz/projects/pretrain-lab/HANDOFF.md` 持卡开工：加载 `.zcode/skills/pretrain-lab/SKILL.md`，按 §0 六步开工序执行——§2 复现检查 → 读前情（`LAB_NOTEBOOK.md` 最近日 + `notes/qa-day-3.md`）→ **先确认 140M 主训练是否在跑**（§1/§5）→ 执行 §7 Day 4 清单（主训练起跑监控 + SFT 数据与脚本），全程按 §6 惯例与 skill §6 校准清单收波。

## 1. 状态一段话

**pretrain-lab 进行中：Day 0~3 已收官，决策门① PASS，140M 主训练已于 2026-11-18 18:46 起跑（进行中）**——小模型从零训练 10 天行动（~140M 预训练 → SFT → LoRA 对比 → GGUF/Ollama demo），底稿 = NoteFlow `WorkingDeck/2026-09/2026-09-22/small-llm-10day-plan.md`。**窗口（2026-11-18 提前起跑拍板）**：Day 1 = 2026-11-18（周三）~ **Day 10 = 2026-11-27（周四）**，Day 9（11-26）硬缓冲；Day 2/Day 3 均为 11-18 当日续跑（**Day 4 起日期不变，机制上已多出两天缓冲**）。**D-10 已拍板** = A 手写 SFT 为主、B ms-swift 对照/兜底（PLAN §3）。**Day 1**：手写 `tools/model.py`（D-02 全套，22,220,544 参数）+ 字符级 20M 闭环（val 1.5599 / 187,480 字符/秒）。**Day 2**：32k BPE（zh 1.841 / en 4.226 chars/token）+ **3,000,000,000 token** 训练集（en:zh=6:4，6×1GB 分片 + val 4M）。**Day 3**：`tools/train.py` 完整框架 · **50M 30min 120,517 tok/s** · **140M 探针 52,250 tok/s ≥ 35k → 门① PASS** · 3B 单程 15.9h · 主训练定档 bs8×accum8（65,536 tok/step · 45,777 步 · ckpt 46 件 ≈76GB）。

**Day 4（11-18 晚起跑，进行中）**：**主训练 `main140m` 运行中**（tmux 会话 `main140m`，日志 `logs/main140m-*.log`，`out/main140m/last.pt` 每 1000 步滚动）——起跑读数 `[anchor] 10.5431 (+0.170)` · **52.8k tok/s** · 1.25s/步 · val@500 **4.9742** · ETA **11-19 ~10:30**（16h 单程）。同时已完成 **SFT 数据 `data/sft-mix/`**（250,001,408 token = 404,210 条对话 + 25% 预训练块，assistant-only mask，val 2M，指纹入库）与 **`tools/sft.py`**（底座载入 + `ignore_index=-100`；CPU 3 步自检 `EXIT:0`，GPU 冒烟待主训练让出显存）。

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
ls data/tokenizer-32k/tokenizer.json data/tokenizer-32k/meta.json  # Day 2 tokenizer（32k BPE）
ls data/shards/meta.json data/shards/SHA256SUMS                    # Day 2 3B 分片清单/指纹
(cd data/shards && sha256sum -c SHA256SUMS | tail -1)              # 应全 OK（~4s）
ls data/bpe-smoke/train.bin                                        # 换轨冒烟切片（50M token）
ls tools/train.py                                                  # Day 3 完整训练框架
ls -la out/day3-50m/last.pt out/day3-140m-probe/last.pt            # Day 3 checkpoint（0.6GB / 1.65GB）
tmux ls | grep -E "main140m|day|train" || echo no-running-training  # 主训练起跑后这里应看到 main140m
```

- `bad interpreter` = venv 断链（D-07 uv 托管解释器免疫此坑；出现即建 venv 时违反 D-07）。
- 分片 `sha256sum -c` 失败 = 数据被动过——先查再训，勿在坏分片上跑批（PROVENANCE 纪律）。
- 检查不过 → 回 PLAN §8 环境快照 / §5 风险表；重建命令见 `reports/2026-11-18-day0-env-snapshot.md`。

## 3. 已完成摘要（Day 0~3，细节在证据与笔记，勿重复劳动）

| Day | 内容 | 结果 |
|---|---|---|
| 0（11-18 早） | 环境预铺：`.venv-pre`（uv 托管 3.12.13 + torch 2.11.0+cu128）· 参考仓 clone · 数据 37.9GB + 17 条指纹 · D-10 拍板 | 全绿，证据 `reports/2026-11-18-day0-env-snapshot.md`；记账 LAB_NOTEBOOK Day 0 |
| 1（11-18） | 手写模型 + 字符级 20M 闭环：`tools/{model,prepare_char20m,train_char20m}.py` | 22.2M 参数；loss 9.4316→val 1.5599；187,480 字符/s；96.1 min；证据 `reports/2026-11-18-day1-char20m.{md,csv,log}` |
| 1 收波校准 | 仓内 skill 建立 · 文档漂移 4 处 + gitignore 指纹漏洞修复 · lessons 8 条 | `31ee2e4` |
| 2（11-18 续跑） | 32k BPE tokenizer + 3B memmap 流水线：`tools/{train_tokenizer,build_shards}.py` | 32k（zh 1.841 / en 4.226 chars/token）· 3,000,000,000 token（en 60%/zh 40%，6×1GB + val 4M，指纹入库）· 构建 20.7 min · 冒烟首步 10.4542；证据 `reports/2026-11-18-day2-{tokenizer,shards,smoke}.{md,csv,log}` |
| 2 盘点校准 | 门①口径（140M 等效 ≥35k）+ 配置/时长/ckpt 预算 + G1~G6 进度 + zh 供给预案 + lessons 4 条 + skill §3.1/§6 | `0366874` |
| 3（11-18 续跑） | 完整训练框架 `tools/train.py` + 50M 定档/冒烟/30min + 140M 探针 + **决策门①** | 50M 50,292,288 @bs16 封顶 · **120,517 tok/s**（215.7M token / val 3.6377）· **140M 52,250 tok/s → 门① PASS** · 3B 单程 **15.9h** · 续训 kill→restore val 一字不差 · 证据 `reports/2026-11-18-day3-{framework,50m-30min,140m-probe}.md` |

## 4. 锚点速查（对账用已知答案）

| 锚 | 值 | 出处 |
|---|---|---|
| 机器基线 | .118 · RTX 5070 Ti 16GB · 空闲 ~14GB（laya-triage 常驻 1.8G）· 96GB RAM · 磁盘余 2.3T | 2026-11-18 实测 |
| `.venv-pre` 栈 | torch 2.11.0+cu128 · CUDA True · sm_120 在 arch list · bf16 矩阵过 · uv CPython 3.12.13 | `reports/2026-11-18-day0-env-snapshot.md` |
| **字符级 20M 基线**（Day 1） | 22.2M 参数 / 词表 11,765 / bs64×512：首步 **9.4316**（vs ln(11765)=9.3727）· val **1.5599** @33k · **187,480 字符/秒** · 96.1 min / 10.8 亿字符 · GPU 57°C / ~15GB | `reports/2026-11-18-day1-char20m.md` |
| **32k BPE tokenizer**（Day 2） | 词表 32,000 · specials 0/1/2 · 留出压缩率 zh **1.841** / en **4.226** chars/token（minimind-6400 的 0.721×/0.696×）· sha `05e9ef17…` | `reports/2026-11-18-day2-tokenizer.md` |
| **3B 训练集**（Day 2） | 3,000,000,000 token · en 60.0%/zh 40.0% · 6×1GB 片（536,870,912 tok/片）+ val 4M · uint16 max_id 31999 · 构建 2.42M tok/s | `reports/2026-11-18-day2-shards.md` · `data/shards/SHA256SUMS` |
| **BPE 冒烟锚**（Day 2） | 29.99M 参数 · 首步 **10.4542** vs ln(32000)=**10.3735**（+0.081）· 60 步 10.45→7.75 / val 7.77 | `reports/2026-11-18-day2-smoke.md` |
| **主模型配置**（Day 2 校准） | 140M = d768/L16/H12 **137,847,552** 参数 · 50M 探针 = d576/L8/H9 **50,292,288** · 100M 兜底 = d640/L16/H10 **99,799,680** | PLAN §4.1 |
| **门①口径**（Day 2 校准） | **140M 等效 ≥35k tok/s**（50M 需 ≥96k 折算；直接跑 140M 20~30 步探针）· 3B 单程 35k→~23.8h / 40k→~20.8h | PLAN §4.1 |
| **门①判定**（Day 3） | **PASS = 140M 实测 52,250 tok/s**（超门限 49%，100M/2B 兜底不启用）· 50M 交叉校验 120,517 tok/s ≥ 96k ✓ | `reports/2026-11-18-day3-140m-probe.md` |
| **训练框架基线**（Day 3） | `tools/train.py`：多分片加权取片 · 梯度累积 · token 预算定 cosine · 三路 RNG 续训 · 固定块 val · 双语固定 prompt · `EXIT:0/1` · eval+sample+ckpt 开销 0.6% | `reports/2026-11-18-day3-framework.md` |
| **50M 吞吐锚**（Day 3） | 50,292,288 @ bs16×accum4×T1024 = 65,536 tok/step → **120,517 tok/s**（36.4 TFLOPS 6N 口径）· 215.7M token / 30m01s · val **3.6377** · peak 10.72GB | `reports/2026-11-18-day3-50m-30min.md` |
| **140M 吞吐锚**（Day 3） | 137,847,552 @ bs8×accum8×T1024 = 65,536 tok/step → **52,250 tok/s**（43.2 TFLOPS）· 40 步 peak 10.51GB · 3B 单程 **15.9h** | `reports/2026-11-18-day3-140m-probe.md` |
| **主训练定档**（Day 3） | bs8×accum8 · **65,536 tok/step · 45,777 步 · 1.25s/步** · lr 6e-4 / warmup 500 / cosine→6e-5 / wd0.1 / clip1.0 · ckpt 每 1000 步 **46 件 ≈76GB** · 命令见报告 §6 | `reports/2026-11-18-day3-140m-probe.md` §6 |
| micro-bs 边界（Day 3） | 50M = **16**（bs24 OOM）· 140M = **8**（bs10 需 `expandable_segments`，bs12 OOM；bs16+grad-ckpt 仅 40,449 tok/s）· `torch.compile` 4,077 tok/s（弃用） | `reports/2026-11-18-day3-{memsweep,framework}.log/md` |
| 参考实现 | minimind @ `233d00f` · nanoGPT @ `3adf61e`（`~/projects/`；minimind 数据现行名 = `pretrain_t2t(_mini)/sft_t2t(_mini)`） | Day 0 clone |
| 数据指纹 | raw 层 17 条 = `data/raw/SHA256SUMS` · 字符级 3 条 = `data/day1-char20m/SHA256SUMS` · tokenizer 3 条 = `data/tokenizer-32k/SHA256SUMS` · 分片 7 条 = `data/shards/SHA256SUMS`（全部入库）· Day 1 checkpoint `last.pt` = `5d97b5f73852a2e9` · **Day 3：50M `out/day3-50m/last.pt` = `71fc274be289c3c2`（603.6MB）· 140M 探针 `out/day3-140m-probe/last.pt` = `df8fc7ac351415db`（1.65GB）** | `data/PROVENANCE.md` |
| 热身收官 | nl2fem develop @ `1ea5401` · finetune-lab develop @ `cc5201c` | 两仓 git log |
| 待回填 | 主训练实际总时长（Day 4/5）· 各版评测读数（Day 5~10）· 主训练 val 曲线锚（Day 6 门②定标用） | — |

## 5. 波次队列（逐日回填；**实际窗口 = 11-18 ~ 11-27**）

| 波次 | 内容 | 状态 |
|---|---|---|
| Day 0（11-18 早） | 环境预铺 | ✅ 完成 |
| Day 1（11-18） | 手写 model.py + 字符级 20M 最小闭环 | ✅ 完成（22.2M / 96.1min / 187,480 字符/s / val 1.5599） |
| Day 2（11-18 当日续跑） | 32k BPE tokenizer + memmap 数据流水线 | ✅ 完成（32k / zh 1.841 · en 4.226 chars/token；3B token 6 片 + val 4M；构建 20.7min；冒烟 10.4542） |
| Day 3（11-18 当日续跑） | 训练框架 + 50M 冒烟/30min + 140M 探针 + **决策门①** | ✅ 完成（门① **PASS**：140M 52,250 tok/s；50M 120,517；3B 单程 15.9h） |
| Day 4（11-18 晚起跑） | **140M 主训练起跑** + SFT 数据/脚本（D-10 = A 主 B 兜底） | **进行中**：主训练 18:46 起跑（52.8k tok/s，ETA 11-19 ~10:30）· SFT 数据 250M + `tools/sft.py` 已完成（CPU 自检过）· GPU 冒烟待让出显存 |
| Day 5（11-22） | 中期 SFT + 评测框架 | 未开工 |
| Day 6（11-23） | 主训练收官 + SFT v2 + **决策门②**（loss 仍陡降 → 加训 15 亿） | 未开工 |
| Day 7（11-24） | LoRA 对比 + GGUF/Ollama/Gradio 部署 | 未开工（超期可砍） |
| Day 8（11-25） | 深化（扫参/tokenizer 消融/DPO）+ 报告开写 | 未开工（超期可砍） |
| Day 9（11-26） | 硬缓冲日 | 未开工 |
| Day 10（11-27） | 收尾：最终对比 + repo 整理 + 报告 | 未开工 |

**关键路径与缓冲（Day 3 实测重算）**：Day 3 框架 + 门① ✅ → **Day 4 140M 起跑（15.9h 单程）→ 次日收官** → Day 5/6 SFT v2 + 门② → Day 7 部署 → Day 10 报告。**主训练须在 Day 6（11-23）中午前完成**——按实测 16h 单程，Day 4~5 任意时点起跑都有充足余量；若 Day 4 起跑，主训练最早 11-19 晚/11-20 晨收官。缓冲 = **11-19/11-20 两天（Day 2/3 均为 11-18 提前完成置换）** + Day 9（11-26）硬缓冲。门①口径已判定（PASS，见 §4）；门②加训 1.5B 的 zh 供给预案见 PLAN §5。主训练占 GPU 期间，白天 SFT 数据/评测框架工作以 CPU 为主，避免争抢。

## 6. 惯例与红线

- **仓内 skill 优先**：跑批/排障/红线按 `SKILL.md` 执行（本件不重复；含 §3.1 数据管线标准动作、§6 收波校准清单）。
- **每晚三道概念检验题**：`notes/qa-day-N.md` 先自答；空洞回 `notes/lessons.md` 补课（追加制带出处）。
- **证据纪律**：`reports/` 只增不改（改错走勘误追加）；每次 run 证据三分 = 摘要 md + 曲线 csv + 原始 log。
- **指纹纪律**：每份数据落位即录（`SHA256SUMS` 例外入库；数据本体 gitignore）。
- **git**：develop 直提为主（信息带 `day-N` 标签）；大改走 `feature/day-N-<slug>` → `--no-ff`；模型/checkpoint/语料/日志不入库。
- **决策门预注册**：门①（Day 3 吞吐）/门②（Day 6 loss）跑前不改。
- **上游知识指针**：finetune-lab `notes/lessons.md`（四杠杆×四失败轴 + OOD 三层）· `ms-swift-finetune` skill（D-10 选 B 时）· nl2fem `notes/ref-*-concepts.md`。

## 7. Day 4 清单（140M 主训练起跑 + SFT 数据/脚本）——进度

> Day 3 清单已全部收官，证据见 §3 与 `reports/2026-11-18-day3-*.md`。**Day 4 状态：1/2/3/4 已完成或进行中，5 进行中，6 待主训练收官后做。**

| # | 事项 | 判据 | 状态 |
|---|---|---|---|
| 1 | **启动 140M 主训练**（命令 = `reports/2026-11-18-day3-140m-probe.md` §6，tmux 后台） | 首 10 分钟：`[anchor]` 10.37~10.62 · tok/s ≥48k · peak ≤11GB | ✅ 18:46 起跑：anchor **10.5431** · **52.8k tok/s** · peak 10.51GB |
| 2 | 起跑后 30 分钟对账 | tok/s ≥50k · 1.25s/步 · val@500 · ≤70°C · 无 EXIT:1 | ✅ val@500 **4.9742**（比预估 8.5~9.0 低得多，属正常——500 步=32.8M token，比探针多 12.5×）· 58°C · SM 2797MHz |
| 3 | **SFT 数据构建**（CPU）：chat 模板 + 混 20~30% 预训练语料 | 抽检/mask 正确；`SHA256SUMS` + PROVENANCE | ✅ `data/sft-mix/` **250,001,408 token**（404,210 会话 + 25% 预训练块，监督 78.15%）+ val 2M · 段级 mask 自检 0 违规 · 指纹入库 |
| 4 | **`tools/sft.py`**（与 `train.py` 同源，loss 只算 assistant token） | 冒烟：loss 从 ln(V) 起降；mask 覆盖正确 | ⚠️ **CPU 3 步自检过**（`EXIT:0`，anchor 10.3615）；**GPU 冒烟待主训练完成后做**（现仅余 ~2.8GB 显存） |
| 5 | 主训练监控（每 30~60 min）+ 采样检查 | val 单调下行无尖峰；ckpt 谱系按时生成 | 进行中（ckpt@1000 起每 1000 步） |
| 6 | 收波：证据三分 + 指纹 + 笔记本 | 同 §6 校准清单五面 | 待主训练收官后 |

**Day 4 决策点**：①主训练 loss 尖峰（窗口均值 >2× 基线）→ 从最近 ckpt 降 LR 重启（`--resume auto --base-lr 3e-4`）；②SFT chat 模板 = `<|im_start|>{role}\n{content}<|im_end|>\n`（对齐 minimind 原格式，specials 1/2），已定；③SFT 序列长度 = 1024（与预训练一致），长会话截断 0.11%。

**主训练收官后（Day 5 开局三件事）**：①`--resume auto` 不适用——直接读 `out/main140m/last.pt` 作为 SFT 底座；②先跑 GPU 冒烟（`tools/sft.py --init-from out/main140m/last.pt --max-steps 50 --batch-size 4`）验证显存/loss/mask，再决定正式 SFT 的 bs；③SFT v1 预注册：lr 1e-4 / warmup 100 / 1 epoch over 250M（≈3,815 步 ≈ 1.3h @ 52k tok/s）。
