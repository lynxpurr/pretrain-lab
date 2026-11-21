# pretrain-lab — 操作路由（仓内 skill）

> 只路由不双写：本件告诉 agent（和我自己）在这个仓里标准动作走哪、红线在哪；细节事实源见指针。范围 = 本仓从零训练行动（2026-11-18 ~ 11-21，**已收官**；常青规程保留）。

## §1 开工序（每次新会话/每日开工）

1. 读 [HANDOFF.md](../../../HANDOFF.md) §0（开工序）+ §1（状态一段话）+ §3（已完成摘要）+ §5（波次状态）+ **§7 当日清单**（后续日同法追加）。
2. 跑 HANDOFF §2 复现检查（约 1 分钟，红项先修不盲目重装）。
3. 读 [LAB_NOTEBOOK.md](../../../LAB_NOTEBOOK.md) 最近一日段 + `notes/qa-day-(N-1).md`（昨晚三题暴露的疑问 = 今日选题池）。
4. 当日事项按 PLAN §4 逐日方案 + HANDOFF 波次队列执行；决策门判定跑前不改（PLAN §4/§4.1 预注册；门①口径 = **140M 等效 ≥35k tok/s**，50M 读数需按 FLOPs 比 2.74× 折算或跑 140M 探针）。

## §2 资产坐标

| 件 | 位置 |
|---|---|
| 计划/决策/逐日/风险 | [PLAN.md](../../../PLAN.md)（D-01~D-10 · §4 决策门 · §6 纪律） |
| 会话交接 + 当日清单 | [HANDOFF.md](../../../HANDOFF.md)（§0 开工序 · §2 复现检查 · §7 机动窗口清单） |
| 逐日记账 | [LAB_NOTEBOOK.md](../../../LAB_NOTEBOOK.md)（决策/现象/读数/疑问，按日追加） |
| 可复用教训（补课用） | [notes/lessons.md](../../../notes/lessons.md)（追加制带出处） |
| 概念检验题（先自答） | `notes/qa-day-N.md` |
| 脚本 | `tools/`（model.py 模型 · prepare_* 数据 · **train.py 预训练框架（多分片/累积/续训/采样/`--init-from` 探针）** · **sft.py 全参 SFT + LoRA（配对 labels + ignore_index + `--lora-*`）** · **eval.py 评测（双口径 PPL + 题库 + distinct-2/rep-4；`--tests` 可换 holdout）** · **eval_lang.py 分语言 val（zh/en 分块 + all/sup 双口径 CE）** · **check_eval_leak.py 评测去重检查器（双向三层）** · eval_format.py 格式/方向/拒答 rubric · build_sft.py v1 数据 · **build_sft_v2.py v2/v2b/v2c/v2d/v2e 数据（列表降采样 + `--protect-math` / `--protect-math-short` + `--en-refusal-keep-den` + `--en-helpful-upsample`）** · gen_sft_v2_extra.py 校准/格式/正例/concise · **lora.py LoRA A/B + apply/merge** · plot_loss.py 报告 loss 图 · **export_gguf.py GGUF（q/k permute）** · export_hf.py HF Llama 格式 · app_stdlib.py 零依赖 demo · app.py Gradio 备用 · train_char20m.py 字符级闭环 · train_tokenizer.py 训 BPE · build_shards.py 建 memmap 分片；都在仓根跑，勿从子目录启动） |
| run 证据（只增不改） | `reports/<日期>-<主题>.{md,csv,log}` 三分 |
| Tokenizer | `data/tokenizer-32k/`（32k ByteLevel BPE，specials endoftext/im_start/im_end；sha 见其 `SHA256SUMS`；重训 `tools/train_tokenizer.py` ~4.5min） |
| 训练数据 | `data/shards/`（3,000,000,000 token · en 60%/zh 40% · 6×1GB 片 + val 4M · uint16；指纹 `data/shards/SHA256SUMS`；重建 `tools/build_shards.py` ~21min） |
| SFT 数据 / 评测集 | `data/sft-mix/`（v1 · 250,001,408 token · 404,210 会话 + 25% 预训练块 · assistant-only mask）· **`data/sft-mix-v2/`（当前 SFT · 同 token/块 · 校准/格式补充 + 列表 1/5 · val 复用 v1）** · **`data/sft-mix-v2b/`（数学保护消融 · 列表 13.53%）** · **`data/sft-mix-v2c/`（选择性数学保护 + 英文再平衡消融 · 列表 10.55%）** · **`data/sft-mix-v2d/`（复读压制 + translate 方向 + concise 正例消融 · 列表 10.15%）** · **`data/sft-mix-v2e/`（去污 + translate 精确对 + math ×2 消融 · 列表 11.47%）** · **`data/sft-extra-v2/`（calibration/format/helpful/concise/**translate** 五类补充样本，**v2e 起已评测去污**）** · **`data/eval/tests.json`（dev 18 题 / 13 tag）+ `data/eval/tests-holdout.json`（holdout 30 题；双向去重 0 撞车）+ `data/eval/tests-holdout-v3.json`（**holdout 90 题** = 30 旧 + 60 新；math 14 / translate 14 / calibration 6 能力块；sha `2539aa2b`；Day 12）**；去重检查器 `tools/check_eval_leak.py` |
| 模型产物 | `out/main140m/last.pt`（底座 · val 2.7709）· `out/sft-v1/last.pt`（v1 · 1.5515）· **`out/sft-v2/last.pt`（原部署至 11-20 · 1.6038 · rep-4 0.066 · 含记忆读数）** · **`out/sft-v2b/last.pt`（消融 · 1.5981 · rep-4 0.117）** · **`out/sft-v2c/last.pt`（消融 · 1.6018 · 题库 17/18 · rep-4 0.135，不部署）** · **`out/sft-v2d/last.pt`（消融 · 1.6059 · rep-4 0.084 + rubric 6/8 双项最佳，不部署）** · **`out/sft-v2e/last.pt`（部署 · 1.6065 · rep-4 0.055 全系最低 + 题库 17-18 去污后，五项判据全过）** · **`out/sft-lora-r8-5e4/last.pt`（LoRA merged · 1.8253 · rep-4 0.260，不部署）** · **`out/sft-lora-r12-5e4/last.pt`（LoRA merged · 1.79% · val 1.8054 · rubric 5-8 · rep-4 0.249，不部署）** · **`out/sft-lora-r12-5e4-2ep/last.pt`（LoRA 2 epochs（Day 12）· val 1.7921 · rep-4 0.176 · holdout v3 人工 48，不部署）** · 底座谱系 46 ckpt ≈73GB |
| 部署（**2026-11-20 已切 v2e**） | **默认 `pretrain-lab-sft-v2e-q8`**（Q8_0 173MB；F16 326MB 可选；**Q4_K_M 在 v2e 上不保真**——吃掉 math 42/translate 新能力）· GGUF `out/gguf/pretrain-lab-140m-sft-v2e-f16.gguf` · Ollama 用户级 `127.0.0.1:11435`（v2 全 tag 保留回滚）· **demo `tools/app_stdlib.py` → `http://127.0.0.1:7860`（默认 T0.3：T0.7 下 translate 方向 16/20，T0.3 20/20）** · 模型卡 [MODEL_CARD.md](../../../MODEL_CARD.md) · 证据 `reports/2026-11-20-deploy-v2e.md` · 复验 `...-deploy-v2e-recheck.log` |
| 数据与指纹 | `data/raw/`（gitignore）+ `data/PROVENANCE.md` + 各层 `SHA256SUMS`（含 v2/v2b/v2c/extra） |
| 产物 | `out/<run>/last.pt`（gitignore）· `out/gguf/` · `logs/`（gitignore，证据快照拷 reports/） |
| 执行规范（spec） | **`specs/`（spec coding：目标/非目标/可验证 AC1~ACn/任务勾选/回滚）**——收尾/多步任务先立 spec 再执行（范例 `specs/2026-11-20-final-phase.md`）；spec=要做什么+怎么验，reports=做成了什么（只增不改） |
| 环境 | `.venv-pre/`（D-07 uv 托管 3.12.13 + torch 2.11.0+cu128；重建命令见 reports/2026-11-18-day0-env-snapshot.md） |

## §3 训练跑批标准动作（Day 1 最小闭环 → **Day 3 正式框架 `tools/train.py`**）

**启动前**（缺一不跑）：
1. 数据现值域自检：`python -c "…memmap.max() < vocab_size…"`（lesson：值域断言前置数据侧）。
2. 锚定预判：首步 loss 应 ≈ ln(vocab_size)（字符级 11765 → 9.37；BPE 32k → 10.37）。**容差随模型规模放宽**：22M +0.06 / 30M +0.08 / **140M +0.17** → 判据 = 落在 `ln(V) + 0~0.25` 且不接近 0；>0.5 或 <0 停线查（数据/词表/取批）。
3. 冒烟：小配置 60 步内 loss 明显下降（50M 参考形态：100 步 10.48→6.93），再上正式跑。
4. 参数检查：`--max-minutes`（兜底，正常时长 2×）> 预估；`--ckpt-every` ≤ 2000 步；`--eval-every`/`--sample-every` 已设；`--target-tokens` 决定 total_steps（LR 调度）。

**启动**：`tmux new-session -d -s <run>"cd <仓根> && PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True .venv-pre/bin/python -I tools/train.py --run-name <run> --data-dir data/shards --n-embd … --batch-size … --grad-accum … --out-dir out/<run>"`，随后 `tail -5 logs/<run>-*.log` 确认 `[anchor]`/`[model]` 行正常。脱离 = `Ctrl+b d`（**勿按 Ctrl+C**）。**输出不要用 `| head`/`| tail` 截断管道**（SIGPIPE 会杀训练进程），一律 `> log` 或 `| tee`。

**监控**（每 20~30 分钟一次）：
- `grep "tok/s" logs/<run>-*.log | tail -3`（窗口值与纯训练值；纯训练值 = 决策门口径）
- `grep "\[val\]" …`（val 是否下行；train/val 背离 = 过拟合信号）
- `awk` 取 `[sample]` 段（固定 4 条中英 prompt；`decode(skip_special_tokens=False)`，EOS 可见 = 解码链路自检）
- `nvidia-smi --query-gpu=memory.used,temperature.gpu,utilization.gpu,clocks.sm --format=csv,noheader`（>75°C 关注；SM 频率掉 = 降频）
- 判活：`logs/<run>.exit` 出现 `EXIT:1` 才算失败；无标记 + 产物增长 = 正在跑

**崩溃续训**：`--resume auto`（读 `out/<run>/last.pt`，含 model/optimizer/step/tokens_seen/三路 RNG）。验证要点 = 恢复后同 step 的 val 应与 kill 前**完全相同**、`tokens_seen == step × tokens_per_step`。

**收波**：证据三分 → `reports/`（md 摘要 + csv + log）→ LAB_NOTEBOOK 当日段 → lessons（有新教训才写）→ qa 题目池 → PLAN 变更记录（有决策/日期变更才写）→ README 状态 → checkpoint/数据指纹补 PROVENANCE → `git commit -m "day-N: …"` + push。

## §3.2 SFT + 评测标准动作（Day 5~6 验证过）

**SFT 跑批**（底座 = `out/main140m/last.pt`；数据 = `data/sft-mix-v2/`，Day 7 起）：
```bash
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True .venv-pre/bin/python -I tools/sft.py \
  --init-from out/main140m/last.pt --data-dir data/sft-mix-v2 --run-name sft-v2 --out-dir out/sft-v2 \
  --batch-size 8 --grad-accum 8 --base-lr 1e-4 --warmup 100 --target-tokens 250e6 \
  --eval-every 250 --eval-iters 20 --eval-batch-size 8 --sample-every 500 --ckpt-every 250
```
- 启动前自检：`--init-from none --device cpu --max-steps 3`（随机小模型，查数据/损失/ckpt 链路）；或 `--init-from out/day3-50m/last.pt --device cpu --max-steps 1`（查底座载入路径）。两者都应 `EXIT:0`。
- 判据：SFT val 应显著低于"底座在 SFT val 上的 loss"（v1：9.82 → 4.60 PPL）；`EXIT:0`；采样里出现 chat 模板行为。
- 显存：140M bs8×accum8 → v1 峰值 **12.09GB** / v2 **12.05GB**（比预训练高 ~1.5GB：eval bs8 + 配对 labels）。
- **1 epoch 就饱和是常见形态**（v1：末 1,000 步只降 0.006）——先查数据质量再谈加 epoch。

**SFT 数据 v2/v2b/v2c 构建（Day 7~8 验证）**：
```bash
.venv-pre/bin/python -I tools/gen_sft_v2_extra.py
.venv-pre/bin/python -I tools/build_sft_v2.py --listy-keep-den 5 --calib-repeat 3 --format-repeat 2 --helpful-repeat 3
# 数学保护消融（v2b；rep-4 会升高到 0.117，见 Day 7 报告）：加 --protect-math
# v2c（Day 8）：加 --out-dir data/sft-mix-v2c --protect-math-short --en-refusal-keep-den 2 --en-helpful-upsample 5
#   选择性数学保护 = 仅 assistant 等式行 ≥3 的数学列表豁免（练习列表教算术组合，叙述罗列不豁免）
#   英文拒答保留 1/2（分支先于 calib——EN_REFUSAL_RE 与 CALIB_RE 英文部分重叠）+ 英文正例 1/5 选中上采样 2×
# v2d（机动窗口，Day 8 收官后）：v2c 参数 + --concise-repeat 3 --translate-upsample 3 --long-answer-keep-den 2 --format-repeat 3
#   ①长答案压制 = 引导型短 prompt ∧ 答案≥600 字 ∧ 非列表/数学/翻译题 → 保留 1/2（复读三题的题型源；大盘开放问答不动）
#   ②translate 方向 = 英 prompt→中 answer 非列表样本 3×（但"方向池"教不会"翻译指令行为"——v2e 要精确指令样本）
#   ③concise 正例 = 介绍/假设题→2~3 句连贯答案（50 unique，含英文 fluency 组——英文长答案不在训练集，只能加正例）
#   结果：rep-4 0.084（差 0.004 未达 <0.08）+ rubric 6/8；math-mul 回退 72（组合记忆容量边缘）；不部署
# v2e（机动第 2 轮，最后一轮）：v2d 参数 + --translate-ex-repeat 6 --math-upsample 2 --en-flu-no-upsample
#   ①extras 评测去污（12 处同型变体 + build 的 assert_no_eval_leak 断言——**造数据不许抄评测原句**）
#   注：v2e 历史构建仍含 2 条 brevity 残留（Day 11 发现）；复现它需加 --skip-eval-leak-check；
#       新构建默认严格断言（失败即改 extras），并先跑 tools/check_eval_leak.py 确认 0 撞车
#   ②translate 精确指令对 = 指令+直接译文 30 unique ×6（v2d 教训：方向池上采样教不会指令行为）
#   ③math-upsample 2 = 数学豁免 ×2（修 math-mul 组合记忆）；④en_flu 长答案不上采样
#   结果：**五项判据全过** rep-4 0.055（全系最低）/ 题库 17-18（去污后）/ translate 真译文 / math 8-42（真泛化）/ PPL +5.5%
```
- 判据：250,001,408 token / 244,142 blocks / 列表类 ≤15%（v2 9.33% / v2b 13.53% / v2c 10.55% / v2d 10.15%）/ mask 300 块 3,000+ 段 0 违规 / val 与 v1 同 sha（复用 v1 val）。
- **采样按能力域保护**：v2b 全量豁免数学（rep-4 0.117 代价）；v2c 收窄为 eqrows≥3（豁免 6,243 条，math 照样修回）。
- **采样规则作用域 = 训练集（读到的行）**：英文拒答 78% 集中 rows 800k-900k 桶、250M 预算 n_read≈810k 截断读不到；改 `--max-tokens` = 改训练分布，前后必须 meta 对账。

**LoRA（Day 7 验证，`tools/lora.py`）**：
```bash
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True .venv-pre/bin/python -I tools/sft.py \
  --init-from out/main140m/last.pt --data-dir data/sft-mix-v2 --run-name sft-lora-r8-5e4 \
  --out-dir out/sft-lora-r8-5e4 --batch-size 8 --grad-accum 8 --base-lr 5e-4 --warmup 100 \
  --target-tokens 250e6 --eval-every 250 --eval-iters 20 --eval-batch-size 8 \
  --sample-every 500 --ckpt-every 250 --lora-rank 8 --lora-alpha 16
```
- 可训练 **1.20%**（r=8，qkv/proj/gate/up/down）；peak **9.74GB**（比全参 -2.3GB）；ckpt **526MB + adapter 6.5MB**；`last.pt` 已 merge（eval/deploy 直接用），`adapter.pt` 单独存。
- **lr**：2e-4 首跑 1000 步 val 1.8839 且采样退化；5e-4 同 step 更好（500 步 1.8974）。r=8 1 epoch 仍欠拟合；**r=12 已试（Day 10）：1.79% 可训练 / val 1.8054 / 题库 15-18 / rubric 5-8 / rep-4 0.249 / peak 9.76GB——rank↑ 只补 0.02 val，距全参 0.20，仍不部署**。**r=12 2 epochs 已试（Day 12）：val 1.7921（1.75~1.80 档；epochs ×2 只买 −0.013，rank 买 −0.020——单独加码任一维都不够，距全参仍 0.19）；能力维度 2ep 有实效（holdout v3 人工 42→48、rep-4 0.249→0.176）→ LoRA 若用，2 epochs 是下限配置**。
- 冒烟：`--max-steps 50 --eval-every 0 --sample-every 0 --ckpt-every 0`，loss 应下降（实测 2.7086 → 2.5235）。

**评测协议（Day 10 八版对比沿用）**：
```bash
.venv-pre/bin/python -I tools/eval.py --ckpt base=out/main140m/last.pt --ckpt sft=out/sft-v1/last.pt \
  --out reports/<日期>-eval.md
.venv-pre/bin/python -I tools/eval_format.py --csv reports/<日期>-eval.csv --out reports/<日期>-eval-rubric.md
# 分语言 val（Day 12；zh/en PPL 分项，回答"英文上采样稀释中文"类问题；双口径 all/sup）
.venv-pre/bin/python -I tools/eval_lang.py --ckpt v1=out/sft-v1/last.pt --ckpt v2=out/sft-v2/last.pt \
  --ckpt v2e=out/sft-v2e/last.pt --out reports/<日期>-langval.md
```
- **统一 greedy**（可复现）+ 关键词判分 + **distinct-2 / rep-4** 退化指标 + 人工 rubric 抽样；
- **关键词判分有假阴/假阳**：v2 的正确回答"2027 年没有世界杯"因 `expect_any` 缺"没有"被判 ❌；v1 的"没有官方…1958"会命中但在编造。rubric 已加"没有/不存在"合法承认 + "1958/2028"编造检查；**关键词分与 rubric 分并列**，不要只看一个。
- CSV 自检：表头 8 列（model,decode,test_id,tag,pass,distinct2,rep4,answer）；答案截断 1000（列表 rubric 需要完整行）。
- **规则分会高估质量**（v1：规则 89% vs 质性 ~60%），报告必须并列质性复核；
- 解码参数（T/top-p/repetition penalty）是**质量变量**，demo 端可换但需单独声明，不混进对比表；
- 复读优先查数据（采样几乎不改善：0.131→0.123），repetition penalty 是"用事实换多样性"（1.3 压复读到 0.032 但题库 16→13）。
- **dev 之外必须有 holdout**（Day 10 立，Day 12 扩）：30 题只够"排除大差距"；**能力验收用 90 题版**（`tests-holdout-v3.json`：math 14 / translate 14 / calibration 6 能力块 + 其余 tag 扩容），三层双向去重 0 撞车；**dev 排名不可直接复用**——v2e 与 v2 在 dev 是 17 vs 15，30 题 holdout 同为 23/30（欠功效），**90 题人工校准 v2e 53 vs v2 47（+6 达阈值）**。命令与规则见 §3.4。
- **"两版无差异"结论前先算功效**（Day 12 立）：n=30 的二项 95% CI ≈ ±4 题，检测 +6 差需 ≥70 题；报告里给 CI 或"该样本量能排除的最小差距"。
- **关键词分必须配人工复核**：holdout 30 题里 moon-count 有 7 个假阳（提到"月球"但数量全错）、weather 2 个假阴（"阳光明媚"不在词表）、knowledge 2 个部分匹配；报告并列"关键词原始分 + 人工复核分"。
- **版本读数分级标注**：完全干净（无 extras，如 v1）/ 部分干净（v2e，2 题残留）/ 含记忆（v2~v2d）；残留题要给"干净子集"读数（v2e 15/16）。

## §3.4 评测集建设与去重硬门（Day 10~12 沉淀）

**holdout 建设规则**：
- 60~100+ 题，覆盖全部 tag；每题 `{id,prompt,expect_any,tag}`，与 dev 同型变体（换知识点/数字/场景），**不参与任何数据迭代**。
- **能力型块**（Day 12 定版，`tests-holdout-v3.json` 为范例）：数学 ≥10 题（多 operand/多步/两位数/换序探针/英文/应用题）、翻译 ≥10 题（双向 × 三种指令句式 + 习语探针）、calibration ≥6 题；其余 tag 各 ≥5。单题/3 题不足以代表能力——能力判据用 10~14 题块（≥70% 才称"会"）。
- **出题前先侦察 extras 覆盖面**（Day 12）：①ARITH 覆盖 2~12 全对 → 新数学题 operand 至少一个 ≥13；②两位数×个位数几乎必触发数字嵌套假阳（`16×3` ⊃ `6×3`），换序探针用 `3×13` 这类对，出题后先跑一遍检查器再定稿；③calibration 年份查覆盖（2027~2042 全占 → 用 2044+），且避开"赛年不存在"前提题（2044 夏奥/2046 世界杯其实存在——判"不编造"而非"没有"）；④concise/format 题面清单逐条避让。
- **三层双向去重**：vs dev / vs `data/sft-extra-v2/*` / vs SFT 源 user 内容。**训练样本可能是评测题前缀**（`请告诉我 2030 年世界杯的冠军。` vs `……冠军是谁`）——单向 `eval in train` 会漏。
- 数字嵌套（`3×3` ⊂ `13×3`、`3+8` ⊂ `13+8`）是**假阳**：换 operand 消除（如 13×5 / 17+6）。
- 评测：`eval.py --tests data/eval/tests-holdout-v3.json --skip-ppl`；题目改动后必须重跑并保留旧文件（`-v2`/`-v3`），不覆盖历史证据。
- **关键词 expect 表的两端缺陷**（Day 12 实测）：**假阴 = 数值写法收口缺失**（lightspeed 9/10 版答对 299,792 而 expect 只有 30万/300000 → 0/10）；**假阳 = 回声/复读碰词 + 数字嵌套**（mars 的 "red" 10/10 过；continent 的 "7" 来自 "70%"）。规则：数值类 expect_any 覆盖常见写法（阿拉伯数字/千分位/科学计数/口语单位）；标签类不能用题干原词当 expect；**验收分 = 关键词（覆盖）+ 人工校准（正确性）并列**。
- **人工校准记录法**（Day 12）：90 题 × N 版全量编码（1=语义正确/完整，0=错误/编造/拒答/回声/复读垃圾），报告给出每版"关键词分 / 人工分 / FP 数 / FN 数"四列 + 展示例；判定口径写进报告（同一复核者偏差 = 保留意见）。

**去重硬门（构建前/评测前各跑一次）**：
```bash
.venv-pre/bin/python -I tools/check_eval_leak.py \
  --eval data/eval/tests.json --eval data/eval/tests-holdout.json \
  --extra-dir data/sft-extra-v2 \
  --sft-source data/raw/minimind_dataset/sft_t2t_mini.jsonl
# EXIT 0 = 0 撞车；EXIT 1 = 有撞车（打印 id/来源/片段）→ 先改数据/题库再跑
```
- **检查器必须自测**：`assert_no_eval_leak` 内置"已知撞车必须被捕获"的自测。历史 bug = `len(prompt)>=8` 守卫跳过短 prompt（6 字「一年有几个月」/7 字「3 加 5 等于多少」）+ norm 只去空白 + 单向检查 → "0 撞车"是假阴性（`reports/2026-11-20-eval-leak-recheck.md`）。
- 断言/检查器禁止有长度/归一化静默跳过；报 0 撞车前先喂一个已知违规样本做阳性对照。

## §3.3 部署标准动作（Day 7 建立，2026-11-20 v2e 轮升级）

```bash
# 1) GGUF 导出（直接 ckpt；q/k permute 已在脚本内）
.venv-pre/bin/python -I tools/export_gguf.py --ckpt out/sft-v2e/last.pt \
  --out out/gguf/pretrain-lab-140m-sft-v2e-f16.gguf --name pretrain-lab-140m-sft-v2e
# 2) Modelfile（TEMPLATE/PARAMETER 沿用上一版）：out/Modelfile-sft-v2e
# 3) Ollama 建模型（用户级 11435；GGUF 源，勿走 safetensors experimental）
OLLAMA_HOST=127.0.0.1:11435 ollama create pretrain-lab-sft-v2e    -f out/Modelfile-sft-v2e
OLLAMA_HOST=127.0.0.1:11435 ollama create pretrain-lab-sft-v2e-q8 -f out/Modelfile-sft-v2e -q q8_0
# 4) 三同对拍（同 prompt 构造含 chat 模板 × greedy × 同 tokenizer）：
#    F16 必须 5/5 逐字一致（链路验收）；目标量化档必须通过"新学能力抽检"
#    （本轮抽检项 = math-mul 42 / translate 中文）
# 5) demo 切换 + 回滚：app_stdlib.py --model <tag>；旧 tag 保留 → 回滚 <1min
```

- **量化选档**：Q8_0 = 部署默认（173MB，保住新学能力）；**Q4_K_M 会吃掉弱记忆**（新学能力与基座强先验冲突时量化噪声让先验反扑——v2e 实测 42→72、translate 回退）→ 不用于 v2e；F16 = 逐字保真可选。
- **对拍纪律**：裸 prompt 对拍会制造假不一致（第一轮实测空输出/答错题），必须同 chat 模板同解码；差异先排除模板/解码/tokenizer 三同。
- Ollama 坑（Day 7）：safetensors experimental 走 MLX（`MLX not available`）；`-q q4_K_M` 只支持 GGUF 源。

## §3.1 数据管线标准动作（Day 2 验证过）

**训 tokenizer**：`.venv-pre/bin/python -I tools/train_tokenizer.py 2>&1 | tee logs/day2-tokenizer-$(date +%Y%m%d-%H%M%S).log`

- 判据：vocab 32,000 · 留出 zh 1.84 / en 4.23 chars/token · 往返自检过 · `data/tokenizer-32k/SHA256SUMS` 落位。~4.5 min / 峰值 RSS ~22GB。
- 坑：`show_progress` 在 `tee` 管道下不落盘（看 CPU/RSS 判活）；`decode()` 默认 `skip_special_tokens=True`（自检显式 False）。

**建分片**：`.venv-pre/bin/python -I tools/build_shards.py 2>&1 | tee logs/day2-build-$(date +%Y%m%d-%H%M%S).log`

- 判据：3,000,000,000 token（en 60%/zh 40%）· 7 个文件 sha256 全 OK · max_id=31999 · `meta.json` + `SHA256SUMS` 落位。~21 min / 2.4M tok/s。
- **建库前先算库存/需求比**：`bytes/token × 语料字节数` ≈ 全库 token；zh 3B 6:4 已耗 ~72%，加训/改配比前先核对（PLAN §5 风险表）。

**换轨冒烟**：`train_char20m.py --data-dir data/bpe-smoke`（只换数据目录）→ 首步 loss ≈ ln(32000)=**10.37**。

**校验**（每次建库/改库后）：

```bash
cd data/shards && sha256sum -c SHA256SUMS
.venv-pre/bin/python -c "import numpy as np; a=np.memmap('shard-000.bin',dtype=np.uint16,mode='r'); print('max_id=',int(a.max()))"   # < 32000
```

## §4 故障排查速查

| 症状 | 先查 | 修法/出处 |
|---|---|---|
| `device-side assert`，栈顶在 norm/ffn | 索引越界（embedding 最先炸） | `CUDA_LAUNCH_BLOCKING=1` 同步复跑定位；查数据 id 上限 |
| `bad interpreter` / venv 断链 | `.venv-pre/bin/python3` 指向 | D-07 uv 托管解释器重建（勿链 /usr/bin） |
| `no kernel image is available` | `torch.cuda.get_arch_list()` 无 sm_120 | 必须 cu128 wheel（PLAN §5 风险表） |
| 下载漏件/404 | `--include` 多 pattern；数据集改版 | PROVENANCE 下载渠道备忘（逐文件位置参数 / curl API 核对清单） |
| loss 尖峰/发散 | grad clip、LR、数据坏样本 | 从最近 checkpoint 降 LR 重启（PLAN §5） |
| 吞吐明显低于锚点 | GPU 被占/降频/bs 变化 | `nvidia-smi` 对账；参照 PLAN §8 训练运行基线（Day 1：22.2M @ bs64×512 = 187,480 字符/s） |
| 分片 `sha256sum -c` 失败 | 数据被动过/写坏 | **先查再训**，勿在坏分片上跑批；对应分片用 `tools/build_shards.py` 重建 |
| BPE 数据 token 数异常 / 解码乱码 | tokenizer 配置（ByteLevel / specials / decode） | 跑往返自检（普通文本 + specials 两段，`skip_special_tokens=False`）；同文对拍 minimind 压缩率 |
| 长任务"日志没进度"/退出码误判 | stale exit 标记、`tee` 缓冲 | 启动前 `rm -f logs/<run>.exit`；判活看 `ps -o pid,etime,%cpu,rss` + 产物文件增长，**不看日志 mtime**；`EXIT:1` 才判失败 |
| `CUDA out of memory`，`Tried to allocate N GiB` | 先看 N 与位置：N≈`positions×32000×4` = CE 的 fp32 副本 | 降 micro-bs（50M 上限 16、140M 上限 8）；或 `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`（140M 可到 10，不提速）；**别加 grad-ckpt 换 bs**（慢 23%） |
| 续训 `TypeError: RNG state must be a torch.ByteTensor` | `torch.load(map_location="cuda")` 把 RNG 字节张量搬上 GPU | 加载后 `.cpu()`（`tools/train.py` 已修）；配套检查 `tokens_seen == step × tokens_per_step` |
| 训练进程莫名 `BrokenPipeError` / EXIT:1 | 输出被 `| head`/`| tail` 截断（SIGPIPE） | 长任务一律 `> log 2>&1` 或 `| tee`，读文件不截管道 |
| 想用 `torch.compile` 提速 | sm_120 上 inductor 未走快路径（Day 3 实测 4,077 vs 52,250 tok/s） | **默认关闭**；重试须做"40 步以上、先预热 20 步、同 seed 同数据"的证伪实验 |
| 证据 log 未入库 | `.gitignore` 的 `*.log` | `!reports/*.log` 例外；收波 `git add -n .` 核对 md/csv/log 三件 |
| 评测分数好看但读起来差 | 关键词判分只测"提到" | 加 distinct-2/rep-4 + 人工 rubric；拒答模板/复读环都会骗过关键词（Day 5~6） |
| 模型复读"文化、艺术、交通…" | 先做解码对照：采样是否改善 | 采样几乎不改善 → 数据罗列癖；rp 调参只是权宜（1.3 伤事实） |
| SFT 后底座语言能力退化 | 预训练 PPL 是否上升 | v1 +6.2% 属可接受；>10% 再考虑提高预训练混入比例或降 lr/步数 |
| `--init-from` 探针打印 `[anchor] … vs ln(V)` 偏差巨大 | 底座初始化时不是随机分布 | 正常（探针代码已加 `[init-anchor]` 分支，不再误报） |
| GGUF 能加载但输出"前几个词正常、随后复读" | q/k 权重未按 llama.cpp 的 RoPE 布局重排 | `tools/export_gguf.py` 的 `permute_qk()`（对齐 llama.cpp `LlamaModel.permute`：`[n_head,2,head_dim/2,in]` → `swapaxes(1,2)`） |
| Ollama 导入 safetensors 后 run 报 `MLX not available` | Ollama 的 experimental safetensors 路径在 Linux 走 MLX runner | 改走 GGUF：`tools/export_gguf.py` → `ollama create FROM *.gguf`（不要用 `--experimental` safetensors） |
| `ollama create -q q4_K_M` 报 unsupported（safetensors 源） | 该路径只支持 int4/int8/nvfp4 等 | 先用 GGUF 源，再 `-q q4_K_M`；GGUF 路径实测支持 Q4_K_M/Q8_0 |
| Gradio 安装卡在 31.4MB wheel（镜像 0.3% CPU） | 镜像限速 | 用 `tools/app_stdlib.py`（零依赖本地页）；`tools/app.py` Gradio 版保留备用 |
| rubric 读 CSV 全空 | `eval.py` 表头 5 列 vs 行 8 列，DictReader 静默错列 | 已修 8 列表头；写完 CSV 做 `head -1` + 行字段数断言 |
| 正确回答"2027 年没有世界杯"被判 ❌ | `expect_any` 缺"没有" | rubric 加"没有/不存在"+编造检查；关键词分与语义分并列 |
| labels.bin 值域自检报 max=65,436 | 读的 dtype 错：labels 是 **int16** 存储（-100 ignore_index 的补码在 uint16 视角 = 65,436） | labels 用 `np.int16` 读，断言 `max < 32000 且 min >= -100`；token 文件（train/val.bin）才用 uint16 |
| LoRA 采样出特殊 token/乱码、val 落后全参 | r=8/lr 2e-4 在 1 epoch 内欠拟合 | 先试 lr 5e-4（500 步探针）；仍欠拟合则 r=12（≈1.80%）或 2 epochs |
| 量化后模型"变笨"（新学的答案/翻译丢失，退回首版行为） | **量化噪声冲掉弱记忆**（新学能力与基座强先验冲突）——先做三同对拍：F16 是否忠实？ | 换 Q8_0（或 F16）部署；验收用"新学能力抽检"而非只看能对话（2026-11-20 v2e：Q4 下 math 42→72） |
| 关键词判分与人工复核差很多 | 关键词表缺同义说法 / 假阳（提到关键词但事实错） | 报告并列"关键词原始分 + 人工复核分"；holdout 判别项逐题看（moon-count 7 假阳 / weather 2 假阴） |
| "0 撞车"但指标异常好 | 检查器假阴性：长度守卫、只去空白、单向包含 | 先喂已知撞车做阳性对照；用 `tools/check_eval_leak.py`（双向三层）；断言内置自测 |
| dev 修复换题就失效 | 修的是单题模式，不是能力 | 建 holdout（≥30 题，三层双向去重）；dev 只用于迭代，验收看 holdout + 干净子集 |
| GGUF 与 PyTorch 对拍大面积不一致（空输出/答错主题） | prompt 构造是否同模板？解码是否同 greedy？tokenizer 是否同文件？ | **三同原则**：chat 模板+温度0+同 tokenizer；裸 prompt 对拍无效（本轮实测差点误判导出坏） |
| `F.linear` LoRA 报 mat2 在 CPU | `apply_lora` 在 model.to(cuda) 后创建 A/B，默认 CPU | A/B 用 `device=base.weight.device, dtype=base.weight.dtype`（Day 7 已修） |
| holdout 30 题判"两版无显著差异" | **功效不足**（n=30 的 CI ≈ ±4 题 > 真实差值） | 先算"该样本量能排除的最小差距"；能力验收扩到 90 题（Day 12：v2e 53 vs v2 47，30 题时同为 23/30） |
| 关键词把正确数值判死（299,792 被判 ✗） | `expect_any` 缺数值写法变体 | 数值类 expect 补阿拉伯/千分位/科学计数/口语单位（见 §3.4）；人工校准兜底 |
| `eval_lang` 末块报 `Expected input batch_size (1024) to match target batch_size (1023)` | 全 token CE 的 y 切片 `o+1+block` 越界（末块不足 1024） | 块偏移按 eval.py 同款 `(len-1)//block` 限制（已修） |
| 分语言 PPL 相对 v1 出现 +20% / base +800% | 基线选错（v1→v2 自带分布位移；base 是预训练→SFT 差） | 只按"因果对照"读（vs v2 隔离上采样单变量）；预注册时先问"基线隔离了目标变量吗" |

## §5 红线

- `reports/` 只增不改；改错走勘误追加。
- 每份数据落位即录指纹（raw 层 17 条 Day 0 已立、字符级 3 条 Day 1 已立、tokenizer 3 条 + 分片 7 条 Day 2 已立；SFT 数据 Day 4 续录）。
- 决策门①（Day 3 吞吐 **140M 等效 ≥3.5 万 token/s**）**已判定 PASS（52,250 tok/s，2026-11-18）**；②（Day 6 loss 仍陡降→加训）**已判定不触发（最后 10% 0.0134 + 恒定 lr 探针 0.0051，2026-11-19）**，重开条件见 PLAN §4.1——两者跑前未改口径。
- SFT/评测协议（Day 6 定档，Day 7 扩展）：SFT 数据 25% 预训练混入 + assistant-only mask；评测统一 greedy + 关键词判分 + distinct-2/rep-4 + 人工 rubric；**不许用解码调参替代数据修复**。评测 CSV 固定 8 列（model,decode,test_id,tag,pass,distinct2,rep4,answer）、答案截断 1000；关键词分与 rubric 分并列报告。
- **量化保真度红线**（2026-11-20 立）：部署量化档必须通过"三同对拍 + 新学能力抽检"——F16 逐字一致才算链路忠实；目标量化档要在至少 N 条"本版新修复"的题上抽检（本项目 = math 42 / translate 中文 / refuse 表述），任一丢失即降档（Q4→Q8/F16）。**"能加载/能对话"不是验收，量化掉的恰是刚学会的。**
- **评测集去重红线**（v2e 立，Day 11 加严）：**extras/补充样本不得与评测集原句相同或近合——双向、且覆盖前缀/少字变体**（v2 起曾把 2027 世界杯/7×6/水的化学式等评测原句带进训练集；holdout 初版也漏过"训练样本是评测题前缀"的 3 题）；`build_sft_v2.py` 的 `assert_no_eval_leak` 为硬门（已修：去所有非单词字符、取消长度守卫、内置自测、同时查 dev+holdout），独立检查用 `tools/check_eval_leak.py`；造新样本先想"同型变体"而非"原题"。
- **评测双层验收红线**（2026-11-20 立）：**dev 集只用于迭代，验收必须有未见题 holdout**（≥30 题、三层双向去重 0 撞车）；关键词分必须配人工复核（30 题里误判可 >10 处）；版本读数标注 **完全干净 / 部分干净 / 含记忆**，残留题给"干净子集"读数。**dev 修复不等于能力**（v2e 的 math-add 8 是残留记忆、math-mul 42 是窄查表；13×5 全错、translate 只认精确句式）。
- **检查器自测红线**（2026-11-20 立）：报"0 撞车"之前，先喂一个已知违规样本证明检查器抓得到；禁止长度/归一化静默跳过（旧 `len(prompt)>=8` 守卫让 v2e"复扫 0 撞车"成为假阴性，dev 残留 2 题）。
- **评测功效红线**（2026-11-21 立）：判定"无显著差异/持平"前必须给 CI 或所需样本量；n=30 的 ±4 题 CI 只能排除大差距——**"30 题持平"已被 90 题推翻（v2e +6）**。能力型结论用 10~14 题块（≥70%），不用单题。
- **关键词 expect 数值变体红线**（2026-11-21 立）：数值类题目的 `expect_any` 必须覆盖常见写法（299,792 / 299,792,458 / 30万 / 3×10^5），否则"掌握了也判错"（lightspeed 9/10 版答对 → 关键词 0/10）；标签类不能用题干原词当 expect（回声假阳）。
- **数据采样按能力域保护**（Day 7 立，Day 8 收窄）：v2 一刀切列表降采样误伤数学（`math-add 15 / math-mul 72`）；v2b 全量豁免数学修回 `8/42` 但 rep-4 0.117；**v2c 定稿口径 = 仅 assistant 等式行 ≥3 的数学列表豁免**（练习列表教算术组合，写入 6,243 条，math 照样修回且列表占比 10.55%）——豁免口径按"功能特征"而非"领域标签"，改口径先做 assistant 侧分桶侦察。
- 主训练定档（Day 3）：140M bs8×accum8×T1024 · 65,536 tok/step · 45,777 步 · lr 6e-4/warmup 500 · ckpt 每 1000 步 46 件 ≈76GB；命令 = `reports/2026-11-18-day3-140m-probe.md` §6。除该报错/环境变化外不改配置。
- 模型/checkpoint/语料/原始 logs 不入库（.gitignore）；**证据快照三件（md/csv/log）必须入 `reports/` 并跟踪**（`!reports/*.log` 例外，commit 前 `git add -n` 核对）。
- 边界：nl2fem / finetune-lab 是知识上游非资产上游（PLAN §7），只引用知识不改其档案。

## §6 收波校准清单（2026-11-18 盘点批起，每日收波跑一遍）

1. **提交面**：`git status -sb` + `git add -n .`——证据三件（md/csv/log）是否都在待提交列表；数据层只应新增 `SHA256SUMS`。
2. **指纹面**：新数据层 `sha256sum -c`；`data/PROVENANCE.md` 补来源/规模/前缀。
3. **数字面**：当日读数回填 HANDOFF §4 锚点 + PLAN §8；`grep` 旧日期/旧数字残留（如 `Day 2（11-19）`）。
4. **链接面**：README/HANDOFF/PLAN/notes/reports 相对链接 0 断链（盘点批扫描 14 份文档）。
5. **状态面**：HANDOFF §1/§3/§5/§7、README 状态、LAB_NOTEBOOK 当日段、lessons/qa、PLAN 变更记录同步。
6. **导出/评测链路面**（Day 7 起）：GGUF raw 与 PyTorch 同 prompt/greedy 对拍；`eval.py` CSV 表头 8 列 + 行字段数断言；rubric 与关键词分并列；demo `/health` + `ollama ps` 显示 100% GPU。
7. **能力域采样面**（Day 7 起）：列表/降采样规则是否误伤数学/代码/翻译；七版评测的失败项按"能力域"归因（数学/校准/格式/翻译/复读），不只看总分；**修复项要连着查相邻能力域**（Day 8：en-fluency 修复伴随英文复读 + translate 方向回归）。
8. **评测面（Day 10 起）**：新数据/新题库先跑 `tools/check_eval_leak.py`（双向三层，EXIT 0）；holdout 与 dev 分表；关键词分 + 人工复核并列；版本读数标"完全干净/部分干净/含记忆"并给干净子集；去重断言自测过（已知撞车被抓）。**dev 排名不可直接写进结论——先看 holdout。**
9. **评测功效面（Day 12 起）**：新题库人工校准表（每版 关键词/人工/FP/FN 四列）+ 判据功效（CI 或"可排除的最小差距"）；数值类 expect 覆盖写法变体（见 §3.4）；分语言 val 用 `tools/eval_lang.py`（zh/en × all/sup 双口径，基线选因果对照）。
