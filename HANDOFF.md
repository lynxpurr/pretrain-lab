# HANDOFF — 新会话交接（项目收官态）

> 更新：2026-11-20 晚（**项目收官 + 收官后复核**）· 本件是新会话的**唯一启动入口**：开工序 + 状态 + 复现检查 + 锚点 + 可选下一步。知识本体在 [PLAN.md](PLAN.md)（D-01~D-10 · 逐日 · 决策门 · 风险 · 纪律），操作规程在 [.zcode/skills/pretrain-lab/SKILL.md](.zcode/skills/pretrain-lab/SKILL.md)（新会话优先加载）。**当前没有"当日清单"：10 天计划已全部完成，任何新动作先立新 spec。**

## 0. 新会话开工序（按序，不跳步）

1. **加载 skill + 读本件 + PLAN 三节**：`SKILL.md` → 本件 §1/§2/§7 → PLAN §3（D-01~D-10）§4.1（门①/门② 判定）§6（纪律）。缺细节回 PLAN，不臆造。
2. **跑 §2 复现检查**（约 1 分钟）——红项先修再动；50 系环境坑已在 Day 0 解决（PLAN §5）。
3. **读前情**：`REPORT.md` 定稿（重点 §0 八版终表、§5.1 去污+残留、§5.2 holdout、§10 复现）+ `LAB_NOTEBOOK.md` Day 10~11 段 + `notes/lessons.md` Day 10~11 五条 + `reports/2026-11-20-eval-leak-recheck.md` + `reports/2026-11-20-holdout-audit.md` §7。
4. **确认项目状态**：§5 日程全 ✅、§7 可选工作未开工。用户若要继续，**先按 `specs/` 惯例立新 spec（目标/非目标/AC/任务/回滚）再执行**。
5. **收波**（任何新动作结束前）：`reports/` 证据三分 → LAB_NOTEBOOK 段 → lessons（有新教训才写）→ qa 题池 → PLAN 变更记录 → README 状态 → 指纹补 PROVENANCE → `git commit -m "day-N: …"` + push。
6. **边界**：nl2fem / finetune-lab 是知识上游非资产上游（PLAN §7）——只引用知识不改其档案；本仓数据与代码全自建。

**首次回复向用户汇报四件事**：项目/窗口状态 · 最近一次结果 · 今日可做什么 · 待拍板项（如有）。

**新会话首条消息（可直接粘贴）**：

> 读 `/home/zenz/projects/pretrain-lab/HANDOFF.md` 持卡：加载 `.zcode/skills/pretrain-lab/SKILL.md`，按 §0 五步执行——§2 复现检查（demo = pretrain-lab-sft-v2e-q8）→ 读前情（REPORT 定稿 §0/§5.1/§5.2/§10 + LAB_NOTEBOOK Day 10~11 + lessons Day 10~11 + eval-leak-recheck + holdout-audit §7）→ **项目已收官（Day 10 于 2026-11-20 提前完成；Day 11 完成去重假阴性复核）**；若要继续可选深化（见 §7），先立新 spec 再执行。

## 1. 状态一段话

**10 天计划于 2026-11-20 提前 7 天完成（实际 8 天）**：本地 5070 Ti 16GB 上从零训出 137,847,552 参数中英小模型（3B token 预训练 → 250M token SFT ×6 版 → LoRA ×2 → GGUF/Ollama demo），产出 = 经验 + 模型 + 报告 + demo。**部署 = `pretrain-lab-sft-v2e-q8`**（Q8_0 173MB；F16 326MB 可选；Q4_K_M 不保真）。**收官后复核（Day 11）修正了三处表述**：①dev 去重有 2 题残留（v2e 是"部分干净"，干净子集 15/16）；②去重检查器曾假阴性（已修 + 自带自测）；③holdout 初版 3 题近重复（换题重跑 v2）。**最终诚实结论：dev 集 v2e 最优；holdout 30 题上 v2e 与 v2 同为 23/30；数学/翻译的修复不泛化，calibration 是唯一稳定泛化项。**

**当前手里有什么（都能直接跑）**：
- **底座**：`out/main140m/last.pt`（137,847,552 参数 · 3B token · **val 2.7709** · sha `0c0096cc172e8a58`）+ 46 个等间隔 ckpt 谱系（≈73GB）
- **SFT v1（完全干净基线）**：`out/sft-v1/last.pt`（val 1.5515 · sha `853322df4583bfa2`）——无 extras，16/18 全干净
- **SFT v2（原部署至 11-20）**：`out/sft-v2/last.pt`（val 1.6038 · sha `a81c3480f4b63366`）——rep-4 0.066；含记忆；数学弱
- **SFT v2b（消融）**：数学保护修回但 rep-4 0.117、translate 回归
- **SFT v2c（消融）**：题库 17/18、en-fluency 首修；rep-4 0.135
- **SFT v2d（消融）**：rep-4 0.084 + rubric 6/8；math-mul 回退 72
- **SFT v2e（部署，2026-11-20 起）**：`out/sft-v2e/last.pt`（val 1.6065 · sha `984a25c4d59e36a4`）——rep-4 **0.055**、题库 17/18（**2 题残留**）、rubric 6/8；干净子集 **15/16**
- **LoRA**：r=8 `out/sft-lora-r8-5e4/last.pt`（1.20% · val 1.8253 · rep-4 0.260）；r=12 `out/sft-lora-r12-5e4/last.pt`（1.79% · val 1.8054 · rubric 5-8 · rep-4 0.249）——均 1 epoch 欠拟合，不部署
- **数据**：`data/shards/`（3B）· `data/sft-mix/`（v1）· `data/sft-mix-v2/v2b/v2c/v2d/v2e/` · `data/sft-extra-v2/`（5 类补充样本）· `data/eval/tests.json`（dev 18）+ `tests-holdout.json`（holdout 30）
- **部署**：Ollama 用户级 11435 默认 `pretrain-lab-sft-v2e-q8`（F16/Q8/Q4 三 tag；旧 v2 全 tag 保留，回滚 <1min）· `tools/app_stdlib.py` 7860（**默认 T0.3**）· 证据 `reports/2026-11-20-deploy-v2e.md`
- **报告**：**[REPORT.md](REPORT.md)** 定稿（八版终表 + §5.1 去污/残留 + §5.2 holdout + §6 LoRA + §10 复现）
- **脚本**：`tools/{model,train,sft,eval,check_eval_leak,build_sft,build_sft_v2,gen_sft_v2_extra,lora,export_gguf,export_hf,eval_format,app_stdlib,app,plot_loss}.py`
- **决策门**：① **PASS**（140M 52,250 tok/s ≥ 35k）；② **不触发**（0.0134 / 0.0051 双证据）

**阶段结论（简版）**：Day 7 v2 = 校准/翻译/格式修好但数学回归；Day 8 v2c = 选择性保护 + en-fluency 首修；机动 v2d = 复读修复最有效（rep-4 0.084）；v2e = 去污 + 精确指令对 + math×2 → dev 判据字面全过、rep-4 0.055；最终阶段 = Q4 量化吃掉弱记忆 → 部署 Q8；Day 10 = 八版终表 + bit-for-bit 复现 + LoRA r12 + demo T0.3；**Day 11 = 去重假阴性修复 + holdout v2（v2e 与 v2 同 23/30）**。

## 2. 复现检查（约 1 分钟，按序）

```bash
cd /home/zenz/projects/pretrain-lab
git branch --show-current && git fetch -q && git status -sb   # develop；干净、与 origin 同步
nvidia-smi --query-gpu=memory.free --format=csv,noheader       # ~14GB 空闲（laya-triage ~1.8G）
df -h /home | tail -1                                          # 余量 ≥100GB
which tmux || echo tmux-missing
.venv-pre/bin/python -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
ls data/raw/SHA256SUMS data/tokenizer-32k/tokenizer.json data/shards/meta.json
(cd data/shards && sha256sum -c SHA256SUMS | tail -1)           # 全 OK
ls data/sft-mix/{meta.json,SHA256SUMS} data/sft-mix-v2e/{meta.json,SHA256SUMS}
ls data/eval/tests.json data/eval/tests-holdout.json data/eval/SHA256SUMS
ls out/main140m/last.pt out/sft-v1/last.pt out/sft-v2/last.pt out/sft-v2e/last.pt \
   out/sft-lora-r8-5e4/last.pt out/sft-lora-r12-5e4/last.pt
tmux ls | grep -E "sft|train|lora|demo" || echo no-running-training
curl -s --max-time 3 http://127.0.0.1:11435/api/tags >/dev/null && echo ollama-user-ok || echo ollama-user-missing
OLLAMA_HOST=127.0.0.1:11435 ollama list | grep -c v2e      # 应 ≥3（v2e / v2e-q8 / v2e-q4）
curl -s --max-time 3 http://127.0.0.1:7860/health && echo demo-ok   # demo 指向 v2e-q8
.venv-pre/bin/python -I tools/check_eval_leak.py --eval data/eval/tests-holdout.json \
  --extra-dir data/sft-extra-v2 --skip-sft-source             # 应 EXIT 0（holdout 0 撞车）
ls reports/2026-11-20-{day10-repro-check,holdout-audit,holdout-eval-v2,eval-leak-recheck}.md
```

- **注意**：全量去重（含 dev）会 EXIT 1（dev 仍有 2 题残留，已知；见 §4）——这是**预期**，不是环境坏。
- `bad interpreter` = venv 断链（D-07 uv 托管解释器免疫）。
- `ollama-user-missing` / `demo-missing`：Ollama 用户级 `OLLAMA_MODELS=$HOME/.ollama/models OLLAMA_HOST=127.0.0.1:11435 ollama serve`；demo `.venv-pre/bin/python -I tools/app_stdlib.py --model pretrain-lab-sft-v2e-q8 --port 7860`（默认 T0.3）。
- 分片 `sha256sum -c` 失败 = 数据被动过——**先查再训**（PROVENANCE 纪律）。
- 检查不过 → PLAN §8 / §5；重建命令见 `reports/2026-11-18-day0-env-snapshot.md`。

## 3. 已完成摘要（Day 0~11，细节在证据与笔记）

| Day | 内容 | 结果 |
|---|---|---|
| 0（11-18 早） | 环境预铺 + 数据下载 + D-10 拍板 | `.venv-pre`（uv 3.12.13 + torch 2.11.0+cu128）· 数据 37.9GB / 17 条指纹 |
| 1（11-18） | 手写 `model.py` + 字符级 20M 闭环 | 22,220,544 参数 · val 1.5599 · 187,480 字符/s |
| 2（11-18 续跑） | 32k BPE + 3B memmap | zh 1.841 / en 4.226 chars/token · 3,000,000,000 token |
| 3（11-18 续跑） | 训练框架 + 50M/探针 + 门① | 50M 120,517 tok/s · 140M **52,250 → PASS** |
| 4（11-18 → 11-19） | 140M × 3B 主训练 | 16h07m41s · **val 2.7709** · 46 ckpt ≈73GB |
| 5（11-19） | SFT v1 + 评测框架 | val 1.5515 · 题库 6/18→16/18 · PPL 9.82→4.60 |
| 6（11-19） | 门② 判定 + 解码对照 | **不加训**（0.0134 / 0.0051）· 复读归因数据侧 |
| 7（11-19） | v2/v2b + LoRA r8 + GGUF/Ollama | v2 val 1.6038 / rep-4 0.066；LoRA 1.20%；demo 7860 |
| 8（11-19→20） | v2c + 六版评测 + 报告开写 | 题库 17/18 + en-fluency 首修；rep-4 0.135 → 不部署 |
| 机动（11-20） | v2d 复读压制 | rep-4 0.084 + rubric 6/8；差 0.004 → 不部署 |
| 机动（11-20） | v2e 去污轮 + 八版评测 | rep-4 0.055 / 题库 17/18（2 残留）/ dev 五项字面全过 |
| 最终阶段（11-20） | 部署切 v2e-q8 + 报告扩写 | Q4 不保真 → Q8；§5.1 评测污染章 |
| **Day 10（11-20 提前）** | 八版终表 + repo 整理 + 复现走查 + LoRA r12 | bit-for-bit 4/4 · eval 18/18 逐字 · F16 5/5 · r12 val 1.8054 · demo T0.3 |
| **Day 11（11-20 收官后）** | **去重假阴性修复 + holdout 双向复检** | 断言/工具修复 · dev 残留 2 题披露（干净子集 v2e 15/16）· holdout v2：v2e=v2=23/30 |

## 4. 锚点速查（对账用已知答案）

**环境与数据**

| 锚 | 值 |
|---|---|
| 机器 | .118 · RTX 5070 Ti 16GB · 96GB RAM · 磁盘余 ~2.1T |
| `.venv-pre` | torch 2.11.0+cu128 · CUDA True · sm_120 · uv CPython 3.12.13 |
| 32k BPE | 词表 32,000 · specials 0/1/2 · zh 1.841 / en 4.226 chars/token · sha `05e9ef17…` |
| 3B 训练集 | 3,000,000,000 token · en 60%/zh 40% · 6×1GB + val 4M · max_id 31999 |
| SFT 集 | 250,001,408 token · 244,142 块 · 25% 预训练混入 · val 2,001,920 token |
| 评测集 | **dev 18 题 / 13 tag**（sha `6c5bd1e9`）+ **holdout 30 题 / 13 tag**（sha `e6e31aaa`）· 双向三层去重 |
| **dev 去重残留** | **2 题**：`fact-months`「一年有几个月」/ `math-add`「3 加 5」= format brevity extras（各 2 条）；旧断言 `len>=8` 守卫假阴性；干净子集 = 16 题：v1 14 / v2 14 / v2c 15 / **v2e 15** / v2b/v2d/LoRA 13 |

**训练与评测**

| 锚 | 值 |
|---|---|
| 主模型配置 | 140M = d768/L16/H12 **137,847,552** · 50M = d576/L8/H9 50,292,288 |
| 门① / 门② | **PASS 52,250 tok/s**（≥35k）· **不触发**（0.0134 / 0.0051） |
| micro-bs 边界 | 50M=16 · 140M=8（bs10 需 expandable_segments；bs12 OOM）；compile 4,077 弃用 |
| 主训练 | bs8×accum8×T1024 · 45,777 步 · lr 6e-4 · 16h07m41s · peak 10.51GB · **val 2.7709** |
| SFT v1 | 3,815 步 / 1h19m26s / val 1.5515 / peak 12.09GB |
| SFT v2 | val 1.6038 / rep-4 0.066 / 1h19m46s / 52,825 tok/s |
| SFT v2b | val 1.5981 / rep-4 0.117 / math 8-42 / 不部署 |
| SFT v2c | val 1.6018 / 题库 17-18 / rep-4 0.135 / en-fluency 首修 / 不部署 |
| SFT v2d | val 1.6059 / rep-4 0.084 / rubric 6-8 / math-mul 72 / 不部署 |
| **SFT v2e（部署）** | val 1.6065 / **rep-4 0.055** / **题库 17/18（2 残留；干净 15/16）** / rubric 6/8 / translate 精确句式 / math 8-42（字面） / 1h19m19s / 53,098 tok/s |
| LoRA r8 / r12 | 1.20% / val 1.8253 / rep-4 0.260；1.79% / val 1.8054 / rubric 5-8 / rep-4 0.249；均不部署 |
| 评测协议 | greedy + 关键词 + distinct-2/rep-4 + 人工 rubric；**holdout 另表 + 人工复核**；demo 端 **T0.3**/top-p0.9 单独声明 |
| **holdout v2（人工复核）** | base 12 / v1 21 / v2 **23** / v2b 21 / v2c 21 / v2d 22 / v2e **23** / lora8 19 / lora12 19（30 题）；**dev 排名不复现**；13×5/17+6/100−37 全错；translate 只认句式；calibration 稳定 |
| GGUF/Ollama | 部署 **v2e-q8**（173MB）；F16 326MB（对拍 5/5）；**Q4_K_M 不保真**（42→72 / translate 回英文）；demo 7860（T0.3）；回滚 tag v2-q4 保留 |

**指纹与待办**

| 项 | 值 |
|---|---|
| 数据指纹 | raw 17 · 字符级 3 · tokenizer 3 · 分片 7 · SFT v1/v2/v2b/v2c/v2d/v2e 各 4 · 补充样本 5 · 评测 2（`data/eval/SHA256SUMS`） |
| ckpt 指纹 | main140m `0c0096cc172e8a58` · sft-v1 `853322df4583bfa2` · sft-v2 `a81c3480f4b63366` · v2b `44856617008a1e10` · v2c `6c12947bb3a56dd5` · v2d `fe972eed11aa599b` · **v2e `984a25c4d59e36a4`** · lora-r8 `81fbbf0840ed56c1` · lora-r12 `4d57b10cb7bcf169` |
| 待回填 | **无**（10 天计划 + 收官复核完成）；可选深化见 §7（需新 spec） |

## 5. 波次队列与日程（**实际执行 = 11-18 ~ 11-20**）

| 波次 | 状态 |
|---|---|
| Day 0 ~ Day 8（环境 → 主训练 → SFT v1 → 门② → v2/v2b/LoRA/部署 → v2c） | ✅ 完成 |
| 机动 v2d / v2e（复读压制 / 去污轮） | ✅ 完成 |
| 最终阶段（部署切 v2e-q8 + 报告扩写） | ✅ 完成 |
| **Day 9（11-26 硬缓冲）** | 未用（提前收官） |
| **Day 10（实际 11-20）** | ✅ 完成（终检 T4 五项） |
| **Day 11（11-20 收官后复核）** | ✅ 完成（去重假阴性 + holdout v2） |

**关键路径（终版）**：Day 3 框架+门① ✅ → Day 4 主训练 3B ✅ → Day 5 SFT v1 + 评测 ✅ → Day 6 门② ✅ → Day 7 v2/v2b + LoRA + 部署 ✅ → Day 8 v2c + 六版评测 ✅ → 机动 v2d/v2e ✅ → 最终阶段 v2e-q8 ✅ → **Day 10 终检 ✅ → Day 11 复核 ✅**。原缓冲（11-22~25 + Day 9）全部未用——8 天完成 10 天计划。

## 6. 惯例与红线

- **仓内 skill 优先**：跑批/排障/红线按 `SKILL.md`（§3 预训练、§3.2 SFT+评测、**§3.4 评测集/holdout**、§6 收波）。
- **qa**：qa-day-2~5/7/10 已 agent 预答（23 题，qa-day-8 模式），**待用户复核/改写**；评分要点 [notes/qa-rubric.md](notes/qa-rubric.md)。
- **证据纪律**：`reports/` 只增不改（改错走勘误追加）；每次 run 三分 = md + csv + log。
- **指纹纪律**：每份数据/ckpt 落位即录（`SHA256SUMS` 入库；数据本体 gitignore）。
- **git**：develop 直提（`day-N` 标签）；模型/checkpoint/语料/原始 logs 不入库。
- **决策门**：①/② 已判定且口径跑前未改（PLAN §4.1），不得事后改口径。
- **评测红线（Day 10~11 加严）**：① dev 只用于迭代，验收必须有 holdout（≥30 题，**双向**三层去重 0 撞车）；② 关键词分必须配人工复核；③ 版本读数标 **完全干净/部分干净/含记忆** + 干净子集；④ **去重检查器先自测**（已知撞车必须被抓）；⑤ 报告 `check_eval_leak.py` 的 EXIT 码。
- **上游知识指针**：finetune-lab `notes/lessons.md` · `ms-swift-finetune` skill · nl2fem `notes/ref-*-concepts.md`。

## 7. 收官后可选工作（**均需新 spec；不阻塞交付**）

| 优先级 | 事项 | 成本 | 收益/判据 |
|---|---|---|---|
| 1 | **holdout 扩到 60~100 题 + 能力型测试**（数学多 operand、翻译多句式） | ~2h | 把 30 题噪声压下去；直接检验"单题修复"假设；预注册判据（如数学 ≥70%、翻译 ≥70%） |
| 2 | **LoRA 2 epochs**（r=12） | ~2.6h GPU | 验证"epochs vs rank"谁是主因；判据 = val 是否进 1.70 档 |
| 3 | **分语言 val**（中/英 PPL 分项） | ~45min | 收口"英文上采样稀释中文"的疑问 |
| 4 | **v2f：去 brevity 残留重建 + 重训** | ~1h20m + 重跑八版 | 换取完全干净的 dev 读数；代价 = 打乱八版可比、两轮为限精神；**仅在对外发布需要"完全干净"时做** |
| 5 | qa 复核（学习项） | 自定 | 先自答再对照 `qa-rubric.md` |
| — | DPO | — | **不建议**（新方向 + 翻新伤口风险） |

**建议顺序**：1 → 2 → 3；4 只在有对外发布需求时做；5 随时。

## 8. 参考实现与出处

- minimind @ `233d00f` · nanoGPT @ `3adf61e`（`~/projects/`，只读借鉴）
- 底稿：NoteFlow `WorkingDeck/2026-09/2026-09-22/small-llm-10day-plan.md`
- 全部证据：`reports/2026-11-18-day*` ~ `reports/2026-11-20-*`（含 holdout / eval-leak-recheck / lora-r12 / deploy-v2e-recheck）
- 当前 commit 链：`d0c973d`（spec）→ `5fc4d2c`（部署+报告）→ `d00ffad`（Day 10）→ `f7bc170`/`36e96b6`（qa）→ `7352e74`（holdout）→ Day 11 复核提交