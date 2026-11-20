# HANDOFF — 新会话交接

> 更新：2026-11-20 晨（Day 8 收官）· 本件是新会话的**唯一启动入口**：开工序 + 状态 + 复现检查 + 当日清单 + 锚点。知识本体在 [PLAN.md](PLAN.md)（D-01~D-10 · 逐日方案 · 决策门 · 风险 · 纪律 · 边界），本件只指路不复述；**仓内操作规程（跑批/故障速查/红线）= [.zcode/skills/pretrain-lab/SKILL.md](.zcode/skills/pretrain-lab/SKILL.md)，新会话优先加载**。

## 0. 新会话开工序（按序执行，不跳步）

1. **加载 skill + 读本件 + PLAN 三节**：`.zcode/skills/pretrain-lab/SKILL.md` → 本件 §1（状态）§5（日程）§7（当日清单）→ PLAN §3（D-01~D-10）§4（逐日 + 决策门①②原文）§4.1（门①／门② 判定）§6（纪律）。缺细节回 PLAN，不臆造。
2. **跑 §2 复现检查**（约 1 分钟）——红项先修再开工，不盲目重装（50 系环境坑已全部压到 Day 0 解决，PLAN §5 风险表）。
3. **读前情**：`LAB_NOTEBOOK.md` 最近一日段 + `notes/qa-day-8.md`（前日题仍空着的话顺手回填：自答暴露的疑问 = 今日选题池）+ `notes/lessons.md` 顶部「跨日回顾 13 条」+ Day 8 段 + `reports/2026-11-20-day8-review.md` 盘点。
4. **执行当日清单**：按 §5 日程当日行 + §7 当日清单；决策门判定**跑前不改**（PLAN §4 预注册）。若用户要求提前/延后开工，先改 §5 实际日期再执行。
5. **收波**（当日结束前）：`reports/` 证据三分 → LAB_NOTEBOOK 当日段 → lessons（有新教训才写）→ qa 题目池 → PLAN 变更记录 → README 状态 → 指纹补 PROVENANCE → `git commit -m "day-N: …"` + push。
6. **边界提醒**：nl2fem / finetune-lab 是**知识上游非资产上游**（PLAN §7）——只引用知识不改其档案；本仓数据与代码全自建。

**首次回复向用户汇报四件事**：窗口剩余天数 · 上一日结果 · 今日计划 · 待拍板项（如有）。

**新会话首条消息（可直接粘贴）**：

> 读 `/home/zenz/projects/pretrain-lab/HANDOFF.md` 持卡开工：加载 `.zcode/skills/pretrain-lab/SKILL.md`，按 §0 六步开工序执行——§2 复现检查 → 读前情（`LAB_NOTEBOOK.md` 机动窗口 v2d 段 + lessons 机动窗口四条 + `reports/2026-11-20-v2d.md` + `notes/qa-day-8.md`）→ 执行 §7 机动窗口清单（**v2e 第 2 轮 vs 锁定 v2 二选一**，默认 v2e），全程按 §6 惯例与 skill §3.2/§6 执行与收波。

## 1. 状态一段话

**Day 0~8 + 机动窗口 v2d/v2e 已全部收官；v2e 五项判据全过（去污后 rep-4 0.055 / 题库 17-18 / translate 真译文 / math 8-42）→ 待拍板：部署是否切 v2e；不切则 v2 保持**。项目 = 本地 5070 Ti 16GB 上 10 天从零训一个 ~140M 中英小模型（预训练 → SFT → LoRA 对比 → 部署 demo），**学习导向**；底稿 = NoteFlow `WorkingDeck/2026-09/2026-09-22/small-llm-10day-plan.md`。

**当前手里有什么（都能直接跑）**：
- **底座**：`out/main140m/last.pt`（137,847,552 参数 · 3B token · **val 2.7709** · sha `0c0096cc172e8a58`）+ 46 个等间隔 ckpt 谱系（≈73GB）
- **SFT v1**：`out/sft-v1/last.pt`（**SFT val 1.5515** · sha `853322df4583bfa2`）——基线对照
- **SFT v2（部署）**：`out/sft-v2/last.pt`（**SFT val 1.6038** · sha `a81c3480f4b63366`）——**rep-4 0.066（七版最低）**、校准/翻译/格式修好；数学弱（math-add 15、math-mul 72）
- **SFT v2b（消融，不部署）**：`out/sft-v2b/last.pt`（val 1.5981 · sha `44856617008a1e10`）——数学保护修回 8/42，但 rep-4 0.117、translate/capability 回归
- **SFT v2c（消融，不部署）**：`out/sft-v2c/last.pt`（val 1.6018 · sha `6c12947bb3a56dd5`）——**关键词题库 17/18 最高**、math 修回、**en-fluency 首次修复**；rep-4 0.135 + translate-en2zh 回归
- **SFT v2e（消融，机动窗口第 2 轮，五项判据全过）**：`out/sft-v2e/last.pt`（val 1.6065 · sha `984a25c4d59e36a4`）——**rep-4 0.055（全系最低）+ 题库 17/18（去污后）+ rubric 6/8 + translate 真译文 + math 8/42**；**extras 评测去污**（12 处 + 断言）后为干净读数
- **SFT v2d（消融，不部署，机动窗口）**：`out/sft-v2d/last.pt`（val 1.6059 · sha `fe972eed11aa599b`）——**rep-4 0.084（SFT 最低档）+ rubric 6/8（最高）**、reason 0.728→**0.088** / en-fluency 0.708→0.371 / zh-fluency 0.516→0.303、math-add 纯数字"8"；未达 = rep-4 差 0.004 / math-mul 回退 72 / translate 字词解释 / 关键词题库 15/18（语义 17/18）
- **LoRA r=8 5e-4**：`out/sft-lora-r8-5e4/last.pt`（merged；1.20% 可训练；peak 9.74GB；**val 1.8253 / 题库 15-18 / rep-4 0.260**；1 epoch 欠拟合，不部署）
- **数据**：`data/shards/`（3B 预训练）· `data/sft-mix/`（v1）· `data/sft-mix-v2/`（部署）· `data/sft-mix-v2b/v2c/v2d/`（消融）· `data/sft-extra-v2/`（校准/格式/正例/**concise**）· `data/eval/tests.json`（18 题 / 9 tag）
- **部署（2026-11-20 已切 v2e）**：Ollama 用户级 11435 默认 **`pretrain-lab-sft-v2e-q8`**（GGUF F16 326MB / Q8_0 173MB / Q4_K_M 103MB 保留但不保真）· `tools/app_stdlib.py`（7860）· 旧 v2 tag 全保留（回滚 <1min）· 证据 `reports/2026-11-20-deploy-v2e.md`
- **报告（G6）**：**[REPORT.md](REPORT.md)**（七版素材 + loss 图 + §4.5 v2d；Day 10 定稿）· 图 = `tools/plot_loss.py`（`reports/figs/loss-curves-day8-v2d.png`）
- **脚本**：`tools/{model,train,sft,eval,build_sft,build_sft_v2,gen_sft_v2_extra,lora,export_gguf,export_hf,eval_format,app_stdlib,app,plot_loss}.py`
- **决策门**：① **PASS**（140M 52,250 tok/s ≥ 35k）；② **不触发**（不加训 15 亿，双证据 0.0134 / 0.0051）

**Day 8 关键结论**：v2c（选择性数学保护 + 英文再平衡）= **关键词题库 17/18 + rubric 5/8 双历史最高**，math-add/math-mul 修回（8/42）、**en-fluency 四版全挂题首次修复**、refuse-unknown 双过；rep-4 0.135 未达 <0.08 判据 + translate-en2zh 回归 → **按预注册保持 v2 部署**。证据 = [reports/2026-11-20-day8-v2c.md](reports/2026-11-20-day8-v2c.md)。

**机动窗口 v2d 关键结论**（2026-11-20，用户拍板 v2d + 部署保持 v2）：长答案压制 + translate 方向 + concise 正例 + format 3× → **rep-4 0.135→0.084（砍 38%）+ rubric 5/8→6/8**、三题复读全面下降（reason 砍 88%）；未达判据 = rep-4（差 0.004）/ math-mul（回退 72=组合记忆脆弱）/ translate（英答中但字词解释）/ 关键词题库 15/18（两题假阴，语义 17/18）→ **不部署**。三条新教训：组合记忆小扰动翻转 / 方向池上采样 ≠ 指令行为 / 英文长答案缺席只能加正例。证据 = [reports/2026-11-20-v2d.md](reports/2026-11-20-v2d.md)。

**机动窗口 v2e 关键结论**（2026-11-20 第 2 轮，用户"继续推进下一步"）：**开工发现评测污染**——v2 起 extras 与 18 题原句系统性撞车（2027 世界杯 / 7×6 / 水的化学式 / 学习编程列表 / ocean&北京，详见 v2e 报告 §1），v2~v2d 题库分含记忆成分、v1 的 16/18 反而是干净读数。v2e = 去污（12 处 + `assert_no_eval_leak` 硬断言）+ translate 精确对 180 条 + 数学豁免 ×2 + en_flu 降采样 → **五项判据全过**：rep-4 **0.055**（全系最低）/ 题库 **17/18（去污后）** / translate **"我热爱机器学习。"** / math **8+42（真泛化）** / PPL +5.5%；**全面优于 v2**（rep-4 0.066→0.055、题库 15→17、math 15/72→8/42、en-fluency 拒答→英文正文、PPL 持平）。**待拍板：部署是否切 v2e**。三条新教训：按评测缺陷造数据必须配评测集去重 / 去污后五项全过说明 v2 时代部分"能力不足"是记忆假象 / 精确指令对 ≠ 方向池（行为 vs 分布）。证据 = [reports/2026-11-20-v2e.md](reports/2026-11-20-v2e.md)。

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
ls out/sft-v2/last.pt out/sft-lora-r8-5e4/last.pt out/sft-v2c/last.pt out/sft-v2d/last.pt  # 部署 / LoRA / 消融
ls tools/{build_sft_v2,gen_sft_v2_extra,lora,export_gguf,eval_format,app_stdlib}.py  # Day 7 脚本
tmux ls | grep -E "sft|main140m|train|lora|demo" || echo no-running-training
curl -s --max-time 3 http://127.0.0.1:11435/api/tags >/dev/null && echo ollama-user-ok || echo ollama-user-missing
curl -s --max-time 3 http://127.0.0.1:7860/health && echo demo-ok || echo demo-missing
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
| **SFT v2** | val **1.6038** / 3,815 步 / 1h19m46s / 52,825 tok/s / peak 12.05GB / **rep-4 0.066** / 预训练 PPL 16.185（+5.4%）/ 题库 15-18（语义 16-18） |
| **SFT v2b（消融）** | val 1.5981 / 1h19m23s / 53,073 tok/s / 数学修回（3+5=8、7×6=42）但 rep-4 0.117 / translate+capability 回归 / 不部署 |
| **SFT v2c（消融）** | 数据 250,001,408 token（列表 10.55% / 会话 587,344 / 监督 76.16%）/ val **1.6018** / 1h19m40s / 52,925 tok/s / peak 12.05GB / **题库 17-18 + rubric 5-8 双最高** / math 修回 8/42 / **en-fluency 首修** / rep-4 0.135（判据未达）+ translate-en2zh 回归 / 不部署（预注册裁决） |
| **LoRA r8** | 1.20% 可训练 / peak **9.74GB（-2.3GB）** / **54,124 tok/s** / ckpt **526MB + adapter 6.5MB** / val **1.8253** / 题库 15-18 / **rep-4 0.260** / 1 epoch 欠拟合（不部署；Day 8 试 r=12/2 epochs） |
| **SFT v2e（消融，机动窗口第 2 轮，五项全过）** | 数据 250,001,408 token（列表 11.47% / 会话 595,348 / 监督 75.99% / 去污 12 处 + translate 精确对 180 + math 豁免 ×2 12,500 + en_flu 1× 770）· 训练 **1h19m19s / 3,815 步 / 53,098 tok/s / val 1.6065 / peak 12.05GB** · 八版评测 **rep-4 0.055（全系最低）+ 题库 17/18（去污后）+ rubric 6/8 + distinct-2 0.860**、translate "我热爱机器学习。"、math 8/42（真泛化）、en-fluency 0.208 / zh-flu 0.224 / reason 0.095 → **五项判据全过，待拍板部署切换** |
| **SFT v2d（消融，机动窗口）** | 数据 250,001,408 token（列表 10.15% / 会话 613,180 / 监督 75.65% / 长答案砍 6,507 留 6,296 + translate 写入 2,106 + concise 150 + fmt 3×）· 训练 **1h19m44s / 3,815 步 / 52,851 tok/s / val 1.6059 / peak 12.05GB** · 七版评测 **rep-4 0.084（SFT 最低档）+ rubric 6/8（最高）**、reason 0.728→0.088 / en-flu 0.708→0.371 / zh-flu 0.516→0.303 / math-add 纯数字「8」；未达 = rep-4 差 0.004 / math-mul 72 / translate 字词解释 / 关键词 15-18（语义 17-18）→ 不部署 |
| **GGUF/Ollama** | **部署 = v2e-q8**；F16 对拍 5/5 逐字一致；Q8_0 保住新学能力（42/中文翻译）；**Q4_K_M 在 v2e 上不保真**（42→72）；demo 7860（系统提示 + T0.7） |

**指纹与待办**

| 项 | 值 |
|---|---|
| 数据指纹 | raw 17 · 字符级 3 · tokenizer 3 · 分片 7 · SFT v1/v2/v2b/v2c 各 4 · 补充样本 3 · 评测 1（全部入库，见 `data/PROVENANCE.md` 与各层 `SHA256SUMS`） |
| ckpt 指纹 | char20m `5d97b5f73852a2e9` · 50M `71fc274be289c3c2` · 140M 探针 `df8fc7ac351415db` · **main140m `0c0096cc172e8a58`** · **sft-v1 `853322df4583bfa2`** · **sft-v2 `a81c3480f4b63366`** · **sft-v2b `44856617008a1e10`** · **sft-v2c `6c12947bb3a56dd5`** · **sft-v2d `fe972eed11aa599b`** · **sft-v2e `984a25c4d59e36a4`** |
| 待回填 | Day 10 最终对比表（六版）· REPORT.md §8 GPU 累计精确化 · v2d/LoRA 深化/DPO（机动窗口选） |
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
| Day 7（11-19） | **SFT 数据 v2/v2b → SFT v2 → LoRA → GGUF/Ollama** | ✅ 完成（v2 val 1.6038 / rep-4 0.066；v2b 消融；LoRA r8 1.20%；Q4 demo 7860） |
| **Day 8（11-19 晚 → 11-20 晨，提前开工）** | 深化（v2c 数据）+ 六版评测 + 报告开写 | ✅ 完成（v2c 题库 17-18 双最高但 rep-4 未达 → 保持 v2 部署；REPORT.md 起稿） |
| 机动（11-20） | **v2d 数据迭代（长答案压制 + translate 方向 + concise 正例 + format 3×）+ 七版评测 + 报告图** | ✅ 完成（rep-4 **0.084** + rubric **6/8** 双项最佳；rep-4 差 0.004 / math-mul 回退 / translate 字词解释 → 不部署；证据 `reports/2026-11-20-v2d*`） |
| 机动（11-20 第 2 轮） | **v2e（去污 + translate 精确对 + math ×2 + en_flu 降采样）+ 八版评测** | ✅ 完成（五项判据全过；rep-4 0.055 / 题库 17-18 去污后；待拍板部署切换） |
| 机动（11-22 ~ 11-25） | **部署切换 v2e（待拍板）或保持 v2** + 报告定稿准备 + LoRA 深化/DPO 视余力 | 未开工（下一动作） |
| Day 9（11-26） | 硬缓冲（只在出事时用） | 未开工 |
| Day 10（11-27） | 六版最终对比 + repo 整理 + 报告定稿 | 未开工 |

**关键路径与缓冲（v2d 实测重算）**：Day 3 框架 + 门① ✅ → Day 4 主训练 3B ✅ → Day 5 SFT v1 + 评测 ✅ → Day 6 门② 判定 + 解码对照 ✅ → Day 7 **SFT v2/v2b + LoRA + GGUF/Ollama** ✅ → Day 8 **v2c + 六版评测 + 报告开写** ✅ → 机动窗口 **v2d（rep-4 0.084 + rubric 6/8 双项最佳，不部署）** ✅ → 11-22~25 v2e 或锁定 v2 → Day 10 收尾。**缓冲 = 11-22 ~ 25 机动 + Day 9（11-26）硬缓冲**——G1~G5 全闭环，剩余全是改进项；v2 部署可用（数学弱/英文拒答是已知限制，v2c/v2d 已证可修但代价未收敛）。

## 6. 惯例与红线

- **仓内 skill 优先**：跑批/排障/红线按 `SKILL.md` 执行（含 §3 预训练、§3.2 SFT+评测、§6 收波校准清单）。
- **每晚三道概念检验题**：`notes/qa-day-N.md` 先自答；空洞回 `notes/lessons.md` 补课（追加制带出处）。当前待自答：qa-day-2 ~ qa-day-5、qa-day-7；qa-day-8 已有 agent 预答卡（本会话回填，可复核/改写）。
- **证据纪律**：`reports/` 只增不改（改错走勘误追加）；每次 run 证据三分 = 摘要 md + 曲线 csv + 原始 log。
- **指纹纪律**：每份数据/ckpt 落位即录（`SHA256SUMS` 例外入库；数据本体 gitignore）。
- **git**：develop 直提为主（信息带 `day-N` 标签）；大改走 `feature/day-N-<slug>` → `--no-ff`；模型/checkpoint/语料/日志不入库。
- **决策门**：①/② 均已判定且口径跑前未改（PLAN §4.1）——重开条件见同节，**不得事后改口径**。
- **评测协议**：统一 greedy + 关键词 + distinct-2/rep-4 + 人工 rubric；**不许用解码调参替代数据修复**。
- **上游知识指针**：finetune-lab `notes/lessons.md` · `ms-swift-finetune` skill（D-10 选 B 时）· nl2fem `notes/ref-*-concepts.md`。

## 7. 机动窗口清单（v2d/v2e 均已收官；剩余 = 部署切换拍板 + Day 10 收尾）

> **v2e 已收官（2026-11-20 第 2 轮，两轮为限的最后一轮）**：**五项判据全过**——rep-4 **0.055**（全系最低）/ 题库 **17/18（去污后）** / translate **"我热爱机器学习。"** / math **8+42（真泛化）** / PPL +5.5%；**全面优于 v2**（rep-4 0.066→0.055、题库 15→17、math 15/72→8/42、en-fluency 拒答→英文正文）。**开工发现评测污染**：v2 起 extras 与 18 题原句系统性撞车（2027 世界杯 / 7×6 / 水的化学式 / 学习编程 / ocean&北京）→ v2~v2d 题库分含记忆成分、**v1 的 16/18 反而是干净读数**；v2e 已去污（12 处变体 + `assert_no_eval_leak` 断言，复扫 0 撞车）。证据 = [reports/2026-11-20-v2e.md](reports/2026-11-20-v2e.md)。

| # | 事项 | 判据/状态 |
|---|---|---|
| 1 | ~~部署切换 v2e~~ | ✅ **完成（2026-11-20）**：默认 `pretrain-lab-sft-v2e-q8`，demo 已切；Q4 不保真（量化吃掉新学能力）→ 证据 `reports/2026-11-20-deploy-v2e.md` |
| 2 | **不切换（备选）**：v2 保持部署，v2e 入档"能力全面最优"消融 | 预注册五项已全过，此路径仅因"不动部署"而选 |
| 3 | 报告定稿准备：八版对比表 + §4.6 v2e + 评测污染方法学章节（§5 或新增）+ loss 图（day8-v2e） | Day 10 素材齐 |
| 4 | LoRA 深化（r=12 / 2 epochs）/ DPO（视余力） | 题库差 ≤2 题 + 三读数 / refuse 保持 + 判据不降 |
| 5 | Day 10（11-27）：最终对比表 + repo 整理 + REPORT 定稿 + 复现步骤核对 | — |

**待拍板项**：**部署是否从 v2 切到 v2e**——v2e 五项判据全过且全面优于 v2（唯一的"退"是 math-add 格式从纯数字变回算式，因为去污把 ARITH 的 (3,5) 组合排除了；格式瑕疵 list-3/math-mul 与历史同款）。切换是**对外可见动作**（GGUF/Ollama/demo/模型卡），需显式确认后执行。
