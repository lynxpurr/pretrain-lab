# HANDOFF — 新会话交接

> 更新：2026-11-20 晚（**项目收官：Day 10 终检完成（提前 7 天）**；部署 = v2e-q8；spec 全部 COMPLETED）· 本件是新会话的**唯一启动入口**：开工序 + 状态 + 复现检查 + 当日清单 + 锚点。知识本体在 [PLAN.md](PLAN.md)（D-01~D-10 · 逐日方案 · 决策门 · 风险 · 纪律 · 边界），本件只指路不复述；**仓内操作规程（跑批/故障速查/红线）= [.zcode/skills/pretrain-lab/SKILL.md](.zcode/skills/pretrain-lab/SKILL.md)，新会话优先加载**。

## 0. 新会话开工序（按序执行，不跳步）

1. **加载 skill + 读本件 + PLAN 三节**：`.zcode/skills/pretrain-lab/SKILL.md` → 本件 §1（状态）§5（日程）§7（当日清单）→ PLAN §3（D-01~D-10）§4（逐日 + 决策门①②原文）§4.1（门①／门② 判定）§6（纪律）。缺细节回 PLAN，不臆造。
2. **跑 §2 复现检查**（约 1 分钟）——红项先修再开工，不盲目重装（50 系环境坑已全部压到 Day 0 解决，PLAN §5 风险表）。
3. **读前情**：`LAB_NOTEBOOK.md` 最后两段（v2e / 最终阶段）+ `notes/lessons.md` 最终阶段三条（量化保真/对拍三同/spec 惯例）+ `reports/2026-11-20-v2e.md` + `reports/2026-11-20-deploy-v2e.md` + **`specs/2026-11-20-final-phase.md`（当前执行规范）** + `notes/qa-day-8.md`（题池）。
4. **执行当日清单**：按 §5 日程当日行 + §7 当日清单；决策门判定**跑前不改**（PLAN §4 预注册）。若用户要求提前/延后开工，先改 §5 实际日期再执行。**当前 §5/§7 已全部 ✅（项目 2026-11-20 收官）**——后续任何新动作先立新 spec（可选深化见 §7 末段 + REPORT §11），不直接复用旧清单。
5. **收波**（当日结束前）：`reports/` 证据三分 → LAB_NOTEBOOK 当日段 → lessons（有新教训才写）→ qa 题目池 → PLAN 变更记录 → README 状态 → 指纹补 PROVENANCE → `git commit -m "day-N: …"` + push。
6. **边界提醒**：nl2fem / finetune-lab 是**知识上游非资产上游**（PLAN §7）——只引用知识不改其档案；本仓数据与代码全自建。

**首次回复向用户汇报四件事**：窗口剩余天数 · 上一日结果 · 今日计划 · 待拍板项（如有）。

**新会话首条消息（可直接粘贴）**：

> 读 `/home/zenz/projects/pretrain-lab/HANDOFF.md` 持卡：加载 `.zcode/skills/pretrain-lab/SKILL.md`，按 §0 六步执行——§2 复现检查（demo 模型 = pretrain-lab-sft-v2e-q8）→ 读前情（REPORT.md 定稿 + LAB_NOTEBOOK Day 10 段 + lessons 最终阶段/Day 10 + `reports/2026-11-20-day10-repro-check.md`）→ **项目已收官（Day 10 于 2026-11-20 提前完成）**；如需继续可选深化（LoRA 2 epochs / DPO / 分语言 val / 评测集扩容），先立新 spec 再执行。

## 1. 状态一段话

**Day 0~8 + 机动窗口 v2d/v2e + 最终阶段 spec + Day 10 终检全部收官（2026-11-20，提前 7 天）**；部署 = `pretrain-lab-sft-v2e-q8`（五项判据全过、去污后干净读数）；八版终表/复现走查/REPORT 定稿/spec COMPLETED 全落档。项目 = 本地 5070 Ti 16GB 上 10 天从零训一个 ~140M 中英小模型（预训练 → SFT → LoRA 对比 → 部署 demo），**学习导向**；底稿 = NoteFlow `WorkingDeck/2026-09/2026-09-22/small-llm-10day-plan.md`。

**当前手里有什么（都能直接跑）**：
- **底座**：`out/main140m/last.pt`（137,847,552 参数 · 3B token · **val 2.7709** · sha `0c0096cc172e8a58`）+ 46 个等间隔 ckpt 谱系（≈73GB）
- **SFT v1**：`out/sft-v1/last.pt`（**SFT val 1.5515** · sha `853322df4583bfa2`）——基线对照
- **SFT v2（原部署，至 11-20）**：`out/sft-v2/last.pt`（**SFT val 1.6038** · sha `a81c3480f4b63366`）——**rep-4 0.066**、校准/翻译/格式修好；数学弱（math-add 15、math-mul 72）；题库读数含评测记忆成分
- **SFT v2b（消融，不部署）**：`out/sft-v2b/last.pt`（val 1.5981 · sha `44856617008a1e10`）——数学保护修回 8/42，但 rep-4 0.117、translate/capability 回归
- **SFT v2c（消融，不部署）**：`out/sft-v2c/last.pt`（val 1.6018 · sha `6c12947bb3a56dd5`）——**关键词题库 17/18 最高**、math 修回、**en-fluency 首次修复**；rep-4 0.135 + translate-en2zh 回归
- **SFT v2e（部署，2026-11-20 起）**：`out/sft-v2e/last.pt`（val 1.6065 · sha `984a25c4d59e36a4`）——**rep-4 0.055（全系最低）+ 题库 17/18（去污后）+ rubric 6/8 + translate 真译文 + math 8/42**；**extras 评测去污**（12 处 + 断言）后为干净读数
- **SFT v2d（消融，不部署，机动窗口）**：`out/sft-v2d/last.pt`（val 1.6059 · sha `fe972eed11aa599b`）——**rep-4 0.084（SFT 最低档）+ rubric 6/8（最高）**、reason 0.728→**0.088** / en-fluency 0.708→0.371 / zh-fluency 0.516→0.303、math-add 纯数字"8"；未达 = rep-4 差 0.004 / math-mul 回退 72 / translate 字词解释 / 关键词题库 15/18（语义 17/18）
- **LoRA r=8 5e-4**：`out/sft-lora-r8-5e4/last.pt`（merged；1.20% 可训练；peak 9.74GB；**val 1.8253 / 题库 15-18 / rep-4 0.260**；1 epoch 欠拟合，不部署）
- **LoRA r=12 5e-4（Day 10 容量对照）**：`out/sft-lora-r12-5e4/last.pt`（merged；**1.79% 可训练 / peak 9.76GB / val 1.8054 / 题库 15-18 / rubric 5-8 / rep-4 0.249**；rank↑ 只补 0.02 val，仍不部署——REPORT §6）
- **数据**：`data/shards/`（3B 预训练）· `data/sft-mix/`（v1）· `data/sft-mix-v2/`（原部署）· `data/sft-mix-v2b/v2c/v2d/`（消融）· **`data/sft-mix-v2e/`（部署，去污）** · `data/sft-extra-v2/`（校准/格式/正例/**concise**/**translate**）· `data/eval/tests.json`（18 题 / 9 tag）
- **部署（2026-11-20 已切 v2e）**：Ollama 用户级 11435 默认 **`pretrain-lab-sft-v2e-q8`**（GGUF F16 326MB / Q8_0 173MB / Q4_K_M 103MB 保留但不保真）· `tools/app_stdlib.py`（7860）· 旧 v2 tag 全保留（回滚 <1min）· 证据 `reports/2026-11-20-deploy-v2e.md`
- **报告（G6）**：**[REPORT.md](REPORT.md)**（**定稿**：八版终表 + §4.7 裁决 + §5.1 评测污染章 + §6 LoRA r12 + §10 复现）· 图 = `tools/plot_loss.py`（`reports/figs/loss-curves-day8-v2e.png`）
- **脚本**：`tools/{model,train,sft,eval,build_sft,build_sft_v2,gen_sft_v2_extra,lora,export_gguf,export_hf,eval_format,app_stdlib,app,plot_loss}.py`
- **决策门**：① **PASS**（140M 52,250 tok/s ≥ 35k）；② **不触发**（不加训 15 亿，双证据 0.0134 / 0.0051）

**Day 8 关键结论**：v2c（选择性数学保护 + 英文再平衡）= **关键词题库 17/18 + rubric 5/8 双历史最高**，math-add/math-mul 修回（8/42）、**en-fluency 四版全挂题首次修复**、refuse-unknown 双过；rep-4 0.135 未达 <0.08 判据 + translate-en2zh 回归 → **按预注册保持 v2 部署**。证据 = [reports/2026-11-20-day8-v2c.md](reports/2026-11-20-day8-v2c.md)。

**机动窗口 v2d 关键结论**（2026-11-20，用户拍板 v2d + 部署保持 v2）：长答案压制 + translate 方向 + concise 正例 + format 3× → **rep-4 0.135→0.084（砍 38%）+ rubric 5/8→6/8**、三题复读全面下降（reason 砍 88%）；未达判据 = rep-4（差 0.004）/ math-mul（回退 72=组合记忆脆弱）/ translate（英答中但字词解释）/ 关键词题库 15/18（两题假阴，语义 17/18）→ **不部署**。三条新教训：组合记忆小扰动翻转 / 方向池上采样 ≠ 指令行为 / 英文长答案缺席只能加正例。证据 = [reports/2026-11-20-v2d.md](reports/2026-11-20-v2d.md)。

**机动窗口 v2e 关键结论**（2026-11-20 第 2 轮，用户"继续推进下一步"）：**开工发现评测污染**——v2 起 extras 与 18 题原句系统性撞车（2027 世界杯 / 7×6 / 水的化学式 / 学习编程列表 / ocean&北京，详见 v2e 报告 §1），v2~v2d 题库分含记忆成分、v1 的 16/18 反而是干净读数。v2e = 去污（12 处 + `assert_no_eval_leak` 硬断言）+ translate 精确对 180 条 + 数学豁免 ×2 + en_flu 降采样 → **五项判据全过**：rep-4 **0.055**（全系最低）/ 题库 **17/18（去污后）** / translate **"我热爱机器学习。"** / math **8+42（真泛化）** / PPL +5.5%；**全面优于 v2**（rep-4 0.066→0.055、题库 15→17、math 15/72→8/42、en-fluency 拒答→英文正文、PPL 持平）。**→ 随即在最终阶段拍板切部署（v2e-q8）**。三条新教训：按评测缺陷造数据必须配评测集去重 / 去污后五项全过说明 v2 时代部分"能力不足"是记忆假象 / 精确指令对 ≠ 方向池（行为 vs 分布）。证据 = [reports/2026-11-20-v2e.md](reports/2026-11-20-v2e.md)。

**最终阶段（2026-11-20 晚，spec 推进）**：`specs/2026-11-20-final-phase.md`（AC1~AC11 + T1~T4）——**T1 部署切 v2e-q8**（demo 7860 已切，旧 v2 tag 全保留回滚 <1min）；对拍发现 **Q4_K_M 量化吃掉新学能力**（math 42→72、translate 退回英文原句）→ 部署默认 **Q8_0** + 新增"量化保真度抽检"验收红线（skill §5）；**T2 报告扩写**（§5.1 评测污染独立章 + §10 复现→v2e + §0 成绩单 v2e 口径 + 五轮迭代）；AC2~AC8 命令级验收通过。证据 = [reports/2026-11-20-deploy-v2e.md](reports/2026-11-20-deploy-v2e.md) · commit `d0c973d`/`5fc4d2c`。

**Day 10 终检（2026-11-20 提前 7 天，T4）**：①**八版终表**（§0 8 行 × 7 列 + **"读数性质（含记忆/干净）"列** + §4.7 裁决表；与 v2e-eval 逐题对账）；②repo 整理（README 收官态 / MODEL_CARD 全面转 v2e / 54 份 md / 152 链接 **0 断链** / 证据 md-csv-log 三分核对）；③**§10 复现走查**：v2e build **bit-for-bit**（4/4 sha256 + meta 全字段）、eval **18/18 行逐字**、deploy **F16 5/5**、Q8 保住新学能力；④**LoRA r=12 容量对照**（1.79% / val 1.8054 / 题库 15-18 / rubric 5-8 / rep-4 0.249——rank↑ 只补 0.02 val，仍不部署）；⑤终检修正 **demo 温度 T0.7→T0.3**（translate 方向 16/20→20/20）；⑥REPORT 置 **FINAL**、spec 置 **COMPLETED**。证据 = [reports/2026-11-20-day10-repro-check.md](reports/2026-11-20-day10-repro-check.md) · `...-deploy-v2e-recheck.log` · `...-lora-r12-eval{,-rubric}.md` · `...-lora-r12-sft.{log,csv}`。

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
ls data/sft-mix-v2/{meta.json,SHA256SUMS} data/sft-extra-v2/{meta.json,SHA256SUMS}  # v2 数据
ls data/sft-mix-v2c/{meta.json,SHA256SUMS} data/sft-mix-v2b/{meta.json,SHA256SUMS}  # v2b/v2c 数据
ls data/sft-mix-v2d/{meta.json,SHA256SUMS} data/sft-extra-v2/concise.jsonl          # v2d 数据 + concise
ls out/sft-v2/last.pt out/sft-lora-r8-5e4/last.pt out/sft-v2c/last.pt out/sft-v2d/last.pt out/sft-v2e/last.pt out/sft-lora-r12-5e4/last.pt  # 原部署 / LoRA r8 / 消融 / 部署 v2e / LoRA r12
ls tools/{build_sft_v2,gen_sft_v2_extra,lora,export_gguf,eval_format,app_stdlib}.py  # Day 7 脚本
tmux ls | grep -E "sft|main140m|train|lora|demo" || echo no-running-training
curl -s --max-time 3 http://127.0.0.1:11435/api/tags >/dev/null && echo ollama-user-ok || echo ollama-user-missing
OLLAMA_HOST=127.0.0.1:11435 ollama list | grep -c v2e                     # 应 ≥3（v2e / v2e-q8 / v2e-q4）
curl -s --max-time 3 http://127.0.0.1:7860/health && echo demo-ok || echo demo-missing   # demo 应指向 v2e-q8
ls specs/2026-11-20-final-phase.md reports/2026-11-20-deploy-v2e.md out/gguf/pretrain-lab-140m-sft-v2e-f16.gguf
```

- `bad interpreter` = venv 断链（D-07 uv 托管解释器免疫此坑）。
- `ollama-user-missing` / `demo-missing`：启动命令见 [reports/2026-11-19-day7-deploy.md](reports/2026-11-19-day7-deploy.md) §2/§4——Ollama 用户级 `OLLAMA_MODELS=$HOME/.ollama/models OLLAMA_HOST=127.0.0.1:11435 ollama serve`；demo `.venv-pre/bin/python -I tools/app_stdlib.py --model pretrain-lab-sft-v2e-q8 --port 7860`（2026-11-20 已切 v2e-q8）。
- 分片 `sha256sum -c` 失败 = 数据被动过——**先查再训**（PROVENANCE 纪律）。
- 检查不过 → PLAN §8 环境快照 / §5 风险表；重建命令见 `reports/2026-11-18-day0-env-snapshot.md`。

## 3. 已完成摘要（Day 0~7，细节在证据与笔记，勿重复劳动）

| Day | 内容 | 结果 |
|---|---|---|
| 0（11-18 早） | 环境预铺 + 数据下载 + D-10 拍板 | `.venv-pre`（uv 3.12.13 + torch 2.11.0+cu128）· 数据 37.9GB / 17 条指纹 · 证据 `reports/2026-11-18-day0-env-snapshot.md` |
| 1（11-18） | 手写 `model.py` + 字符级 20M 闭环 | 22,220,544 参数 · val **1.5599** · **187,480 字符/s** · 96.1 min · 证据 `reports/2026-11-18-day1-char20m.*` |
| 2（11-18 续跑） | 32k BPE + 3B memmap 流水线 | zh 1.841 / en 4.226 chars/token · **3,000,000,000 token**（en60/zh40，6×1GB + val 4M）· 构建 20.7min · 冒烟 10.4542 |
| 3（11-18 续跑） | `tools/train.py` + 50M 冒烟/30min + 140M 探针 + **门①** | 50M **120,517 tok/s**（val 3.6377）· 140M **52,250 tok/s → 门① PASS** · 3B 单程 15.9h · 续训 kill→restore val 一字不差 |
| 4（11-18 18:46 → 11-19 10:53） | **140M × 3B 主训练** + SFT 数据 + `sft.py` | **16h07m41s / 52,171 tok/s / val 2.7709 / 0 尖峰 / 46 ckpt ≈73GB** · SFT 数据 250,001,408 token · 证据 `reports/2026-11-19-day4-main140m.md` |
| 5（11-19） | **SFT v1 + 对比评测** | SFT val **1.5515**（3,815 步 / 1h19m）· base→sft：题库 **6/18→16/18**、SFT PPL **9.818→4.596**、预训练 PPL 15.350→16.307（遗忘 +6.2%）· 证据 `reports/2026-11-19-day5-{eval,sft-v1}.*` |
| 6（11-19） | **门② 判定 + 解码对照** | **不加训**（0.0134 / 0.0051 双证据，`reports/2026-11-19-day6-gate2.md`）· 复读归因数据侧（`...-day6-decode.md`）· 评测协议定档 |
| 7（11-19） | **SFT 数据 v2/v2b + LoRA + GGUF/Ollama** | v2 **val 1.6038 / rep-4 0.066 / 15-18（语义 16-18）** · v2b 数学修回但 rep-4 0.117 · LoRA r8 **1.20% / peak 9.74GB** · GGUF Q4 103MB + demo 7860 · 证据 `reports/2026-11-19-day7-*` |
| 8（11-19 晚 → 11-20 晨，提前开工） | **v2c（选择性数学保护 + 英文再平衡）+ 六版评测 + 报告开写** | v2c **val 1.6018 / 题库 17-18 历史最高 / rubric 5-8 / math 修回 / en-fluency 首修**；rep-4 0.135 未达判据 → 按预注册**保持 v2 部署**；**REPORT.md 11 章起稿** · 证据 `reports/2026-11-20-day8-*` | |
| 9（11-20 机动 + 最终阶段） | **v2d/v2e 两轮数据迭代 + 八版评测 + 部署切 v2e-q8 + 报告扩写** | v2e 五项判据全过（rep-4 0.055 / 题库 17-18 去污后）；Q4 不保真 → Q8 部署；REPORT §5.1 评测污染章 | |
| **10（11-20 提前收官）** | **八版终表 + repo 整理 + §10 复现走查 + LoRA r12 + REPORT/spec 定稿** | 4/4 sha bit-for-bit · 18/18 行评测逐字 · F16 5/5 · r12 val 1.8054 · demo T0.3；证据 `reports/2026-11-20-day10-repro-check.md` | |

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
| 评测协议 | **greedy + 关键词判分 + distinct-2/rep-4 + 人工 rubric**；demo 端 **T0.3**/top-p0.9 单独声明（Day 10 终检下调：T0.7 下 translate 方向 4/20 漂移，T0.3 20/20） |
| **SFT v2** | val **1.6038** / 3,815 步 / 1h19m46s / 52,825 tok/s / peak 12.05GB / **rep-4 0.066** / 预训练 PPL 16.185（+5.4%）/ 题库 15-18（语义 16-18） |
| **SFT v2b（消融）** | val 1.5981 / 1h19m23s / 53,073 tok/s / 数学修回（3+5=8、7×6=42）但 rep-4 0.117 / translate+capability 回归 / 不部署 |
| **SFT v2c（消融）** | 数据 250,001,408 token（列表 10.55% / 会话 587,344 / 监督 76.16%）/ val **1.6018** / 1h19m40s / 52,925 tok/s / peak 12.05GB / **题库 17-18 + rubric 5-8 双最高** / math 修回 8/42 / **en-fluency 首修** / rep-4 0.135（判据未达）+ translate-en2zh 回归 / 不部署（预注册裁决） |
| **LoRA r8** | 1.20% 可训练 / peak **9.74GB（-2.3GB）** / **54,124 tok/s** / ckpt **526MB + adapter 6.5MB** / val **1.8253** / 题库 15-18 / **rep-4 0.260** / 1 epoch 欠拟合（不部署） |
| **LoRA r12（Day 10 容量对照）** | **1.79% 可训练（2,506,752）/ peak 9.76GB / 53,472 tok/s / ckpt 551MB + adapter 10MB / val 1.8054 / 题库 15-18 / rubric 5-8 / rep-4 0.249** / 预训练 PPL 15.730 · 1 epoch 仍欠拟合（不部署；rank↑ 只补 0.02 val） |
| **SFT v2e（部署，2026-11-20 起；五项全过）** | 数据 250,001,408 token（列表 11.47% / 会话 595,348 / 监督 75.99% / 去污 12 处 + translate 精确对 180 + math 豁免 ×2 12,500 + en_flu 1× 770）· 训练 **1h19m19s / 3,815 步 / 53,098 tok/s / val 1.6065 / peak 12.05GB** · 八版评测 **rep-4 0.055（全系最低）+ 题库 17/18（去污后）+ rubric 6/8 + distinct-2 0.860**、translate "我热爱机器学习。"、math 8/42（真泛化）、en-fluency 0.208 / zh-flu 0.224 / reason 0.095 → **部署已切 v2e-q8** |
| **SFT v2d（消融，机动窗口）** | 数据 250,001,408 token（列表 10.15% / 会话 613,180 / 监督 75.65% / 长答案砍 6,507 留 6,296 + translate 写入 2,106 + concise 150 + fmt 3×）· 训练 **1h19m44s / 3,815 步 / 52,851 tok/s / val 1.6059 / peak 12.05GB** · 七版评测 **rep-4 0.084（SFT 最低档）+ rubric 6/8（最高）**、reason 0.728→0.088 / en-flu 0.708→0.371 / zh-flu 0.516→0.303 / math-add 纯数字「8」；未达 = rep-4 差 0.004 / math-mul 72 / translate 字词解释 / 关键词 15-18（语义 17-18）→ 不部署 |
| **GGUF/Ollama** | **部署 = v2e-q8（173MB）**；F16 对拍 5/5 逐字一致（sha `eee10822`）；Q8_0 保住新学能力（42/中文翻译）；**Q4_K_M 在 v2e 上不保真**（42→72 / translate 回英文）；demo 7860 → v2e-q8（系统提示 + **T0.3**）；回滚 tag v2-q4 保留 |

**指纹与待办**

| 项 | 值 |
|---|---|
| 数据指纹 | raw 17 · 字符级 3 · tokenizer 3 · 分片 7 · SFT v1/v2/v2b/v2c/v2d/v2e 各 4 · 补充样本 5 · 评测 1（全部入库，见 `data/PROVENANCE.md` 与各层 `SHA256SUMS`） |
| ckpt 指纹 | char20m `5d97b5f73852a2e9` · 50M `71fc274be289c3c2` · 140M 探针 `df8fc7ac351415db` · **main140m `0c0096cc172e8a58`** · **sft-v1 `853322df4583bfa2`** · **sft-v2 `a81c3480f4b63366`** · **sft-v2b `44856617008a1e10`** · **sft-v2c `6c12947bb3a56dd5`** · **sft-v2d `fe972eed11aa599b`** · **sft-v2e `984a25c4d59e36a4`** · lora-r8 `81fbbf0840ed56c1` · **lora-r12 `4d57b10cb7bcf169`** |
| 待回填 | **无（Day 10 终检已收官）**；可选深化 = LoRA 2 epochs / DPO / 分语言 val（均不属于 10 天计划） |
| 参考实现 | minimind @ `233d00f` · nanoGPT @ `3adf61e`（`~/projects/`） |

## 5. 波次队列与日程（**实际执行 = 11-18 ~ 11-20；10 天计划 8 天完成**）

| 波次 | 内容 | 状态 |
|---|---|---|
| Day 0（11-18 早） | 环境预铺 | ✅ 完成 |
| Day 1（11-18） | 手写 model.py + 字符级 20M 闭环 | ✅ 完成 |
| Day 2（11-18 续跑） | 32k BPE + 3B memmap 数据流水线 | ✅ 完成 |
| Day 3（11-18 续跑） | 训练框架 + 50M 冒烟/30min + 140M 探针 + **门①** | ✅ 完成（门① PASS 52,250） |
| Day 4（11-18 晚 → 11-19 晨） | **140M × 3B 主训练** + SFT 数据/脚本 | ✅ 完成（val 2.7709 / 16h08m / 46 ckpt） |
| Day 5（11-19） | SFT v1 + 评测框架 + 门② 双证据 | ✅ 完成（SFT val 1.5515；题库 33%→89%） |
| Day 6（11-19） | **门② 正式判定** + 解码对照 | ✅ 完成（不加训；复读归因数据侧） |
| Day 7（11-19） | **SFT 数据 v2/v2b → SFT v2 → LoRA → GGUF/Ollama** | ✅ 完成（v2 val 1.6038 / rep-4 0.066；v2b 消融；LoRA r8 1.20%；Q4 demo 7860） |
| **Day 8（11-19 晚 → 11-20 晨，提前开工）** | 深化（v2c 数据）+ 六版评测 + 报告开写 | ✅ 完成（v2c 题库 17-18 双最高但 rep-4 未达 → 保持 v2 部署；REPORT.md 起稿） |
| 机动（11-20） | **v2d 数据迭代（长答案压制 + translate 方向 + concise 正例 + format 3×）+ 七版评测 + 报告图** | ✅ 完成（rep-4 **0.084** + rubric **6/8** 双项最佳；rep-4 差 0.004 / math-mul 回退 / translate 字词解释 → 不部署；证据 `reports/2026-11-20-v2d*`） |
| 机动（11-20 第 2 轮） | **v2e（去污 + translate 精确对 + math ×2 + en_flu 降采样）+ 八版评测** | ✅ 完成（五项判据全过；rep-4 0.055 / 题库 17-18 去污后；部署已切 v2e-q8） |
| 机动（11-20 第 3 轮，最终阶段） | **部署切换 v2e-q8 + 报告扩写（评测污染章）** | ✅ 完成（spec T1/T2；AC2~AC8 命令级验收） |
| Day 9（11-26） | 硬缓冲（只在出事时用） | 未用（提前收官） |
| **Day 10（实际 11-20，提前 7 天）** | **八版终表 + repo 整理 + REPORT/spec 置 COMPLETED + LoRA r=12** | ✅ 完成（4/4 sha bit-for-bit / eval 18-18 行逐字 / F16 5/5 / r12 val 1.8054 / demo T0.3） |

**关键路径（终版）**：Day 3 框架 + 门① ✅ → Day 4 主训练 3B ✅ → Day 5 SFT v1 + 评测 ✅ → Day 6 门② 判定 + 解码对照 ✅ → Day 7 SFT v2/v2b + LoRA + GGUF/Ollama ✅ → Day 8 v2c + 六版评测 + 报告开写 ✅ → 机动 v2d（rep-4 0.084）/ v2e（五项全过，去污）✅ → 最终阶段部署切 v2e-q8 + 报告扩写 ✅ → **Day 10 终检（11-20 提前）✅ 项目收官**。原缓冲（11-22~25 机动 + Day 9）全部未用——实际 8 天完成 10 天计划。

## 6. 惯例与红线

- **仓内 skill 优先**：跑批/排障/红线按 `SKILL.md` 执行（含 §3 预训练、§3.2 SFT+评测、§6 收波校准清单）。
- **每晚三道概念检验题**：`notes/qa-day-N.md` 先自答；空洞回 `notes/lessons.md` 补课（追加制带出处）。当前待自答：qa-day-2 ~ qa-day-5、qa-day-7、**qa-day-10**（Day 10 题池：bit-for-bit 复现 / 量化抽检 / 读数标注）；qa-day-8 已有 agent 预答卡（可复核/改写）。**评分要点 = [notes/qa-rubric.md](notes/qa-rubric.md)**（18 题判分要点 + 常见错误 + 出处；先自答再对照）；若只想快速收口，可授权 agent 按 qa-day-8 模式代写预答卡。
- **证据纪律**：`reports/` 只增不改（改错走勘误追加）；每次 run 证据三分 = 摘要 md + 曲线 csv + 原始 log。
- **指纹纪律**：每份数据/ckpt 落位即录（`SHA256SUMS` 例外入库；数据本体 gitignore）。
- **git**：develop 直提为主（信息带 `day-N` 标签）；大改走 `feature/day-N-<slug>` → `--no-ff`；模型/checkpoint/语料/日志不入库。
- **决策门**：①/② 均已判定且口径跑前未改（PLAN §4.1）——重开条件见同节，**不得事后改口径**。
- **评测协议**：统一 greedy + 关键词 + distinct-2/rep-4 + 人工 rubric；**不许用解码调参替代数据修复**。
- **上游知识指针**：finetune-lab `notes/lessons.md` · `ms-swift-finetune` skill（D-10 选 B 时）· nl2fem `notes/ref-*-concepts.md`。

## 7. Day 10 终检清单（T4）— ✅ 全部完成（2026-11-20 提前 7 天）

> **项目已收官**：spec T1/T2/T3/T4 全部完成，spec 置 COMPLETED。部署 = `pretrain-lab-sft-v2e-q8`（rep-4 0.055 / 题库 17-18 去污后 / math 8-42 / translate 真译文）；Q4 量化不保真入验收红线；REPORT 定稿；LoRA r=12 容量对照入 §6。**不再迭代数据版本。**

| # | 事项 | 结果 |
|---|---|---|
| 1 | 八版最终对比表定稿（§0 + §4.7 终表；含"读数性质（含记忆/干净）"标注列） | ✅ 8 行 × 7 列 + 标注列；与 `reports/2026-11-20-v2e-eval{,-rubric}.md` 逐项对账一致 |
| 2 | repo 整理（README 首屏 / MODEL_CARD v2e 口径 / `git add -n` 三件 / 断链） | ✅ 54 份 md / 152 链接 **0 断链**；证据 md-csv-log 俱全 |
| 3 | REPORT 置 FINAL；spec 置 COMPLETED | ✅ REPORT 头 "FINAL / 定稿"；spec Status = COMPLETED（§9 终检记录） |
| 4 | §10 复现走查（v2e build/sft/eval/deploy 四段） | ✅ build **bit-for-bit**（4/4 sha256 + meta 全同）/ eval **18/18 行逐字** / deploy **F16 5/5**——`reports/2026-11-20-day10-repro-check.md` |
| 5 | 收波：commit + push；LAB_NOTEBOOK Day 10 段 | ✅ `git log` 有 `day-10:` 提交 |

**终检额外产出**：LoRA r=12（1.79% / val 1.8054 / rubric 5-8 / rep-4 0.249，仍不部署）；demo 温度 T0.7→T0.3（方向 16/20→20/20）；qa-day-10 题池。

**已拍板/执行**：①LoRA r=12 跑完（HANDOFF 默认路径）；②八版终表保留"含记忆/干净"标注（对外版保留——诚实读数解释优于"高分"）。
**未做（超出 10 天计划）**：LoRA 2 epochs、DPO、分语言 val、评测集扩容——见 REPORT §11 后续方向。
