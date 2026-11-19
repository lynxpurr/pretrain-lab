# HANDOFF — 新会话交接

> 更新：2026-11-19（Day 6 收官：主训练 3B + SFT v1 + 门② 判不加训）· 本件是新会话的**唯一启动入口**：开工序 + 状态 + 复现检查 + 当日清单 + 锚点。知识本体在 [PLAN.md](PLAN.md)（决策 D-01~D-10、逐日方案、决策门、风险、纪律、边界），本件只指路不复述；**仓内操作规程（跑批/故障速查/红线）= [.zcode/skills/pretrain-lab/SKILL.md](.zcode/skills/pretrain-lab/SKILL.md)，新会话优先加载**。

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

**pretrain-lab 进行中：Day 0~6 已收官（门① PASS、主训练 3B、SFT v1、门② 判"不加训"），下一动作 = Day 7（SFT v2 数据侧修正 + LoRA + GGUF/部署）**——小模型从零训练 10 天行动（~140M 预训练 → SFT → LoRA 对比 → GGUF/Ollama demo），底稿 = NoteFlow `WorkingDeck/2026-09/2026-09-22/small-llm-10day-plan.md`。**窗口（2026-11-18 提前起跑拍板）**：Day 1 = 2026-11-18（周三）~ **Day 10 = 2026-11-27（周四）**，Day 9（11-26）硬缓冲；Day 2/Day 3 均为 11-18 当日续跑（**Day 4 起日期不变，机制上已多出两天缓冲**）。**D-10 已拍板** = A 手写 SFT 为主、B ms-swift 对照/兜底（PLAN §3）。**Day 1**：手写 `tools/model.py`（D-02 全套，22,220,544 参数）+ 字符级 20M 闭环（val 1.5599 / 187,480 字符/秒）。**Day 2**：32k BPE（zh 1.841 / en 4.226 chars/token）+ **3,000,000,000 token** 训练集（en:zh=6:4，6×1GB 分片 + val 4M）。**Day 3**：`tools/train.py` 完整框架 · **50M 30min 120,517 tok/s** · **140M 探针 52,250 tok/s ≥ 35k → 门① PASS** · 3B 单程 15.9h · 主训练定档 bs8×accum8（65,536 tok/step · 45,777 步 · ckpt 46 件 ≈76GB）。

**Day 4（11-18 18:46 → 11-19 10:53）：140M 主训练完成** — 16h07m41s · **3,000,041,472 token** · **val 2.7709**（train 2.677）· **52,171 tok/s**（全程无衰减）· 46 个 ckpt ≈73GB · 0 尖峰 · `EXIT:0` · 终版 `last.pt` sha `0c0096cc172e8a58`。终版采样：中文"中国的首都是北京"、英文"The capital of France is Paris"（事实已对），并自发执行翻译/总结指令。同时完成 **SFT 数据 `data/sft-mix/`**（250,001,408 token = 404,210 条对话 + 25% 预训练块，assistant-only mask，val 2M，指纹入库）与 **`tools/sft.py`**。

**Day 5（11-19）：SFT v1 收官 + base/SFT 对比评测 + 门② 双证据。** SFT v1（`out/sft-v1/last.pt`，sha `853322df4583bfa2`）= 3,815 步 / 1h19m26s / 53,004 tok/s / SFT val **1.5515** / `EXIT:0`。评测（`reports/2026-11-19-day5-eval.md`）：**base = 预训练 PPL 15.350 · SFT PPL 9.818 · 题库 6/18（33%）**；**sft = 预训练 PPL 16.307（遗忘 +6.2%）· SFT PPL 4.596（2.1×↓）· 题库 16/18（89%）**——但质性复核发现复读环/编造推理/拒答模板等问题（详见 LAB_NOTEBOOK Day 5 补记），**规则分高估质量**。门② 双证据 = 最后 10% 降幅 0.0134 + 恒定 lr 探针 0.0051（上界）→ **判"不加训"**。

**Day 6（11-19）：门② 正式落档 + 解码对照。** 判定 = **不加训**（`reports/2026-11-19-day6-gate2.md`，含重开条件）。解码对照（`reports/2026-11-19-day6-decode.md`）**证伪"greedy 放大复读"**：采样 rep-4 0.123 vs greedy 0.131；rp1.3 能把 rep-4 压到 0.032 但题库 16→13。**复读来自数据罗列风格；校准缺失（`refuse-unknown` 5 配置全挂）与格式跟随（`math-mul`）也与解码无关** → SFT v2 走数据侧。评测协议定档 = greedy + 关键词判分 + distinct-2/rep-4 + 人工 rubric。

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
ls tools/train.py tools/sft.py tools/eval.py                       # Day 3~5 主线脚本
ls -la out/main140m/last.pt out/sft-v1/last.pt                     # 底座与 SFT v1（各 1.65GB）
ls data/sft-mix/meta.json data/sft-mix/SHA256SUMS data/eval/tests.json  # SFT 数据 + 评测题库
tmux ls | grep -E "sft|main140m|train" || echo no-running-training  # 有跑批时这里应看到对应会话
```

- `bad interpreter` = venv 断链（D-07 uv 托管解释器免疫此坑；出现即建 venv 时违反 D-07）。
- 分片 `sha256sum -c` 失败 = 数据被动过——先查再训，勿在坏分片上跑批（PROVENANCE 纪律）。
- 检查不过 → 回 PLAN §8 环境快照 / §5 风险表；重建命令见 `reports/2026-11-18-day0-env-snapshot.md`。

## 3. 已完成摘要（Day 0~6，细节在证据与笔记，勿重复劳动）

| Day | 内容 | 结果 |
|---|---|---|
| 0（11-18 早） | 环境预铺：`.venv-pre`（uv 托管 3.12.13 + torch 2.11.0+cu128）· 参考仓 clone · 数据 37.9GB + 17 条指纹 · D-10 拍板 | 全绿，证据 `reports/2026-11-18-day0-env-snapshot.md`；记账 LAB_NOTEBOOK Day 0 |
| 1（11-18） | 手写模型 + 字符级 20M 闭环：`tools/{model,prepare_char20m,train_char20m}.py` | 22.2M 参数；loss 9.4316→val 1.5599；187,480 字符/s；96.1 min；证据 `reports/2026-11-18-day1-char20m.{md,csv,log}` |
| 1 收波校准 | 仓内 skill 建立 · 文档漂移 4 处 + gitignore 指纹漏洞修复 · lessons 8 条 | `31ee2e4` |
| 2（11-18 续跑） | 32k BPE tokenizer + 3B memmap 流水线：`tools/{train_tokenizer,build_shards}.py` | 32k（zh 1.841 / en 4.226 chars/token）· 3,000,000,000 token（en 60%/zh 40%，6×1GB + val 4M，指纹入库）· 构建 20.7 min · 冒烟首步 10.4542；证据 `reports/2026-11-18-day2-{tokenizer,shards,smoke}.{md,csv,log}` |
| 2 盘点校准 | 门①口径（140M 等效 ≥35k）+ 配置/时长/ckpt 预算 + G1~G6 进度 + zh 供给预案 + lessons 4 条 + skill §3.1/§6 | `0366874` |
| 3（11-18 续跑） | 完整训练框架 `tools/train.py` + 50M 定档/冒烟/30min + 140M 探针 + **决策门①** | 50M 50,292,288 @bs16 封顶 · **120,517 tok/s**（215.7M token / val 3.6377）· **140M 52,250 tok/s → 门① PASS** · 3B 单程 **15.9h** · 续训 kill→restore val 一字不差 · 证据 `reports/2026-11-18-day3-{framework,50m-30min,140m-probe}.md` |
| 4（11-18 晚 → 11-19 晨） | **140M 主训练 3B token** + SFT 数据 250M + `tools/sft.py` | **val 2.7709** · 16h07m41s · 52,171 tok/s · 46 ckpt ≈73GB · 0 尖峰 · 终版事实采样已对 · 证据 `reports/2026-11-19-day4-main140m.md` |
| 5（11-19） | **SFT v1** + 对比评测 + 门② 双证据 | SFT val **1.5515** · 1h19m26s / 3,815 步 · **base 6/18 → sft 16/18（89%）** · SFT PPL 9.82→4.60 · 预训练 PPL 15.35→16.31（遗忘 +6.2%）· 探针 300 步只降 0.0051 · 证据 `reports/2026-11-19-day5-{eval,sft-v1}.md/log` |
| 6（11-19） | **门② 正式判定** + 解码对照 | **不加训**（0.0134 / 0.0051 双证据）· 复读非解码问题（采样 0.123 vs greedy 0.131）· rp1.3 压复读到 0.032 但题库 16→13 · 证据 `reports/2026-11-19-day6-{gate2,decode}.md` |

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
| **主训练 val 锚**（Day 4~5 实测，门② 定标用） | @4k **3.3932** · @8k 3.2052 · @12k 3.1104 · @16k 3.0459 · @20k **2.9936** · @24k 2.9424 · @28k 2.8996 · @32k 2.8576 · @34k **2.8384**；最近 500 步降幅 −0.0050（4.5k 时为 −0.046，9× 变平）· train 窗口 2.75 · **0 尖峰**（1711 窗口） | `logs/main140m-*.log` · `logs/main140m-loss_curve.csv` |
| **主训练终版**（Day 5） | **val 2.7709** · 3,000,041,472 token / 16h07m41s / **52,171 tok/s** · 46 ckpt ≈73GB · 最后 10% 降幅 **0.0134**（门② 阈值 0.02~0.03）· `last.pt` sha `0c0096cc172e8a58` | `reports/2026-11-19-day4-main140m.md` |
| **SFT v1**（Day 5） | SFT val **1.5515** · 3,815 步 / 1h19m26s / 53,004 tok/s · `last.pt` sha `853322df4583bfa2` | `reports/2026-11-19-day5-sft-v1.log` |
| **对比评测**（Day 5） | base：预训练 PPL **15.350** / SFT PPL 9.818 / 题库 **6-18**；sft：预训练 PPL **16.307**（+6.2%）/ SFT PPL **4.596** / 题库 **16-18（89%）**（规则分，质性复核见笔记本） | `reports/2026-11-19-day5-eval.md` |
| **门② 双证据**（Day 5） | 最后 10% val 降幅 **0.0134**（<0.02）· 恒定 lr 6e-5 探针 300 步 **0.0051**（上界，逐段衰减） → **判定：不加训**（已落档 Day 6） | `reports/2026-11-19-day5-probe-const-lr.log` |
| **解码对照**（Day 6） | greedy **16/18**（rep-4 0.131）· sample T0.7/p0.9 15/18（0.123）· rp1.1 15/18（0.087）· rp1.2 15/18（0.057）· rp1.3 **13/18**（0.032）→ 复读非解码问题；评测协议 = greedy + rep-4/distinct-2 | `reports/2026-11-19-day6-decode.md` |
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
| Day 4（11-18 18:46 → 11-19 10:53） | **140M 主训练** + SFT 数据/脚本（D-10 = A 主 B 兜底） | ✅ 主训练收官（3B token / 16h08m / **val 2.7709** / 52,171 tok/s / 46 ckpt ≈73GB）· SFT 数据 250M + `tools/sft.py` 就绪 · **GPU 冒烟与 SFT v1 待做** |
| Day 5（11-19） | SFT v1 + 评测框架 + 门② 诊断 | ✅ 完成（SFT val 1.5515；题库 33%→89%；SFT PPL 4.60；探针 0.0051） |
| Day 6（11-19） | **门② 正式判定** + 解码对照 | ✅ 完成（不加训；复读归因数据侧；评测协议定档） |
| Day 7（**下一动作**） | **SFT v2 数据侧修正** + LoRA + GGUF/Ollama 部署 | **未开工（清单 §7）** |
| Day 7（11-24） | LoRA 对比 + GGUF/Ollama/Gradio 部署 | 未开工（超期可砍） |
| Day 8（11-25） | 深化（扫参/tokenizer 消融/DPO）+ 报告开写 | 未开工（超期可砍） |
| Day 9（11-26） | 硬缓冲日 | 未开工 |
| Day 10（11-27） | 收尾：最终对比 + repo 整理 + 报告 | 未开工 |

**关键路径与缓冲（Day 6 实测重算）**：Day 3 框架 + 门① ✅ → Day 4 主训练 3B ✅ → Day 5 SFT v1 + 评测 ✅ → Day 6 门② 判定（**不加训**）+ 解码对照 ✅ → **Day 7 SFT v2 数据侧 + LoRA + 部署** → Day 8 深化 + 报告 → Day 10 收尾。**缓冲 = 11-20 ~ 11-22 三天 + Day 9（11-26）硬缓冲**——G3/G4/G6 都有充裕时间，不需要砍项；即使 SFT v2 失败，也可直接用 SFT v1 进 LoRA/部署（G1/G2/G5 是底线）。

**剩余日程（2026-11-19 实测重排；原计划日期已不重要，按任务完成度走）**：

| 实际日期 | 任务 | 判据 / 产出 |
|---|---|---|
| 11-19 晚 ~ 11-20 | **Day 7**：SFT 数据 v2（CPU）→ SFT v2（~1.3h）→ LoRA（~1h）→ GGUF/Ollama/Gradio | 题库 ≥16/18 且 rep-4 <0.08；`refuse-unknown`/`math-mul` 至少修好一个；LoRA 可训练参数 <2%；demo 能对话 |
| 11-21 | **Day 8**：深化（lr 扫参 / tokenizer 消融 / DPO 三选一）+ 报告开写 | 报告骨架落盘（loss 曲线 + 数据决策 + 成本核算）+ 至少 1 个对照实验读数 |
| 11-22 ~ 11-25 | **机动**（原 Day 9 提前置换） | 补实验 / 修质性缺陷 / 评测扩展 / 模型卡 |
| 11-26 | **Day 9 硬缓冲** | 只在出事时用（训练发散重跑 / 数据返工） |
| 11-27 | **Day 10 收尾**：三版对比（base / SFT / LoRA）+ repo 整理 + 报告 | G5/G6 达成：对比表 + README + 模型卡 + 复现步骤 |

## 6. 惯例与红线

- **仓内 skill 优先**：跑批/排障/红线按 `SKILL.md` 执行（本件不重复；含 §3.1 数据管线标准动作、§6 收波校准清单）。
- **每晚三道概念检验题**：`notes/qa-day-N.md` 先自答；空洞回 `notes/lessons.md` 补课（追加制带出处）。
- **证据纪律**：`reports/` 只增不改（改错走勘误追加）；每次 run 证据三分 = 摘要 md + 曲线 csv + 原始 log。
- **指纹纪律**：每份数据落位即录（`SHA256SUMS` 例外入库；数据本体 gitignore）。
- **git**：develop 直提为主（信息带 `day-N` 标签）；大改走 `feature/day-N-<slug>` → `--no-ff`；模型/checkpoint/语料/日志不入库。
- **决策门预注册**：门①（Day 3 吞吐）/门②（Day 6 loss）跑前不改。
- **上游知识指针**：finetune-lab `notes/lessons.md`（四杠杆×四失败轴 + OOD 三层）· `ms-swift-finetune` skill（D-10 选 B 时）· nl2fem `notes/ref-*-concepts.md`。

## 7. Day 7 清单（SFT v2 数据侧修正 + LoRA + 部署）

> Day 6 清单已收官（门② 不加训；解码对照证伪"greedy 放大复读"），证据见 §3/§4 与 `reports/2026-11-19-day6-{gate2,decode}.md`。

| # | 事项 | 判据 |
|---|---|---|
| 1 | **SFT 数据 v2（CPU，新目录 `data/sft-mix-v2/`，不动 v1）**：①**校准/拒答**——从 404k 会话中筛含"不知道/无法/不确定/尚未/没有官方记录"的回答，目标 ≥3,000 条（≈1%），不足则手写 100~200 条补齐；②**格式硬约束**——"只回答…/一句话/不超过…/列出 3 条"类指令样本上采样 2×；③**压罗列癖**——答案含 ≥5 条编号列表的样本降采样 50%（或整条过滤），目标使列表类占比从当前水平降到 ≤15%；④其余不变（25% 预训练块、assistant-only mask、block 1024、val 2M 同口径） | **供给实测（2026-11-19 grep，会话级）**：不知道 9,438 · 不确定 23,564 · 尚未 5,786 · 没有官方 139 · 只回答 1,703 · 一句话 6,203 · 不超过 18,321 · **含"5."的列表类 258,468（28.5%）** → ①② 供给充足，③ 需砍掉约一半列表样本。其余判据：新旧数据统计对比落档；段级 mask 自检 0 违规；`SHA256SUMS` + PROVENANCE 更新；**v2 只改数据，不改 tokenizer/模板/混入比例** |
| 2 | **SFT v2（GPU，~1.3h）**：同底座 `out/main140m/last.pt`、同超参（lr 1e-4 / warmup 100 / 1 epoch over 250M） | 同题库 **≥16/18** 且 **rep-4 <0.08**（v1 0.131）；`refuse-unknown` 与 `math-mul` **至少各修好一个**；预训练 PPL 退化 ≤10%；`EXIT:0` |
| 3 | **LoRA（D-10 A 手写）**：同一底座 + 同一 SFT 数据，低秩增量（r=8/16，target = qkv/proj/gate/up/down） | 可训练参数 <2%；50 步冒烟 loss 下降；与全参 SFT 同题库对比（效果/显存/速度三读数） |
| 4 | **GGUF 量化 → Ollama → Gradio**（G4，超期可砍） | `llama.cpp` 转 Q4_K_M/ Q8_0；Ollama 能对话；Gradio 页面可访问（本地 URL） |
| 5 | 评测扩展：新指标进 `tools/eval.py` 默认输出 | distinct-2 / rep-4 已加；rubric 表（人工）落 reports/ |
| 6 | 收波：证据三分 + 笔记本 + PLAN/HANDOFF/README + commit | 同 §6 校准清单五面 |

**Day 7 决策点**：①SFT v2 的校准样本从哪来（现有数据筛选 vs 手写 100~200 条）——默认先筛选、不足再手写；②LoRA 秩 r=8 还是 16（默认 8，显存与效果折中）；③量化档位（Q4_K_M 默认，Q8_0 对照）。

**若 SFT v2 来不及**：直接用 SFT v1 进 LoRA/部署（G3/G4 优先），v2 作为 Day 8 深化项——**G1/G2/G5 是底线，G3/G4 可降级**（PLAN §4 裁法）。
