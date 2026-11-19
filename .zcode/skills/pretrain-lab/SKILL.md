# pretrain-lab — 操作路由（仓内 skill）

> 只路由不双写：本件告诉 agent（和我自己）在这个仓里标准动作走哪、红线在哪；细节事实源见指针。范围 = 本仓 10 天行动（2026-11-18 ~ 11-27）。

## §1 开工序（每次新会话/每日开工）

1. 读 [HANDOFF.md](../../../HANDOFF.md) §0（开工序）+ §1（状态一段话）+ §3（已完成摘要）+ §5（波次状态）+ **§7 当日清单**（后续日同法追加）。
2. 跑 HANDOFF §2 复现检查（约 1 分钟，红项先修不盲目重装）。
3. 读 [LAB_NOTEBOOK.md](../../../LAB_NOTEBOOK.md) 最近一日段 + `notes/qa-day-(N-1).md`（昨晚三题暴露的疑问 = 今日选题池）。
4. 当日事项按 PLAN §4 逐日方案 + HANDOFF 波次队列执行；决策门判定跑前不改（PLAN §4/§4.1 预注册；门①口径 = **140M 等效 ≥35k tok/s**，50M 读数需按 FLOPs 比 2.74× 折算或跑 140M 探针）。

## §2 资产坐标

| 件 | 位置 |
|---|---|
| 计划/决策/逐日/风险 | [PLAN.md](../../../PLAN.md)（D-01~D-10 · §4 决策门 · §6 纪律） |
| 会话交接 + 当日清单 | [HANDOFF.md](../../../HANDOFF.md)（§0 开工序 · §2 复现检查 · §7 Day 3+） |
| 逐日记账 | [LAB_NOTEBOOK.md](../../../LAB_NOTEBOOK.md)（决策/现象/读数/疑问，按日追加） |
| 可复用教训（补课用） | [notes/lessons.md](../../../notes/lessons.md)（追加制带出处） |
| 概念检验题（先自答） | `notes/qa-day-N.md` |
| 脚本 | `tools/`（model.py 模型 · prepare_* 数据 · **train.py 预训练框架（多分片/累积/续训/采样/`--init-from` 探针）** · **sft.py 全参 SFT（配对 labels + ignore_index）** · **eval.py 评测（双口径 PPL + 题库 + distinct-2/rep-4）** · build_sft.py SFT 数据 · train_char20m.py 字符级闭环 · train_tokenizer.py 训 BPE · build_shards.py 建 memmap 分片；都在仓根跑，勿从子目录启动） |
| run 证据（只增不改） | `reports/<日期>-<主题>.{md,csv,log}` 三分 |
| Tokenizer | `data/tokenizer-32k/`（32k ByteLevel BPE，specials endoftext/im_start/im_end；sha 见其 `SHA256SUMS`；重训 `tools/train_tokenizer.py` ~4.5min） |
| 训练数据 | `data/shards/`（3,000,000,000 token · en 60%/zh 40% · 6×1GB 片 + val 4M · uint16；指纹 `data/shards/SHA256SUMS`；重建 `tools/build_shards.py` ~21min） |
| SFT 数据 / 评测集 | `data/sft-mix/`（250,001,408 token = 404,210 会话 + 25% 预训练块 · assistant-only mask · 指纹 `SHA256SUMS`；重建 `tools/build_sft.py` 4min）· `data/eval/tests.json`（18 题 / 9 tag 题库） |
| 模型产物 | `out/main140m/last.pt`（底座 · val 2.7709）· `out/sft-v1/last.pt`（SFT v1 · val 1.5515）· 底座谱系 46 ckpt ≈73GB |
| 数据与指纹 | `data/raw/`（gitignore）+ `data/PROVENANCE.md` + 各层 `SHA256SUMS` |
| 产物 | `out/<run>/last.pt`（gitignore）· `logs/`（gitignore，证据快照拷 reports/） |
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

**SFT 跑批**（底座 = `out/main140m/last.pt`；数据 = `data/sft-mix/`）：
```bash
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True .venv-pre/bin/python -I tools/sft.py \
  --init-from out/main140m/last.pt --run-name sft-v2 --out-dir out/sft-v2 \
  --batch-size 8 --grad-accum 8 --base-lr 1e-4 --warmup 100 --target-tokens 250e6 \
  --eval-every 250 --eval-iters 20 --eval-batch-size 8 --sample-every 500 --ckpt-every 250
```
- 启动前自检：`--init-from none --device cpu --max-steps 3`（随机小模型，查数据/损失/ckpt 链路）；或 `--init-from out/day3-50m/last.pt --device cpu --max-steps 1`（查底座载入路径）。两者都应 `EXIT:0`。
- 判据：SFT val 应显著低于"底座在 SFT val 上的 loss"（v1：9.82 → 4.60 PPL）；`EXIT:0`；采样里出现 chat 模板行为。
- 显存：140M bs8×accum8 → 峰值 **12.09GB**（比预训练高 1.5GB：eval bs8 + 配对 labels）。
- **1 epoch 就饱和是常见形态**（v1：末 1,000 步只降 0.006）——先查数据质量再谈加 epoch。

**评测协议（Day 10 三版对比沿用）**：
```bash
.venv-pre/bin/python -I tools/eval.py --ckpt base=out/main140m/last.pt --ckpt sft=out/sft-v1/last.pt \
  --out reports/<日期>-eval.md
```
- **统一 greedy**（可复现）+ 关键词判分 + **distinct-2 / rep-4** 退化指标 + 人工 rubric 抽样；
- **规则分会高估质量**（v1：规则 89% vs 质性 ~60%），报告必须并列质性复核；
- 解码参数（T/top-p/repetition penalty）是**质量变量**，demo 端可换但需单独声明，不混进对比表；
- 复读优先查数据（采样几乎不改善：0.131→0.123），repetition penalty 是"用事实换多样性"（1.3 压复读到 0.032 但题库 16→13）。

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

## §5 红线

- `reports/` 只增不改；改错走勘误追加。
- 每份数据落位即录指纹（raw 层 17 条 Day 0 已立、字符级 3 条 Day 1 已立、tokenizer 3 条 + 分片 7 条 Day 2 已立；SFT 数据 Day 4 续录）。
- 决策门①（Day 3 吞吐 **140M 等效 ≥3.5 万 token/s**）**已判定 PASS（52,250 tok/s，2026-11-18）**；②（Day 6 loss 仍陡降→加训）**已判定不触发（最后 10% 0.0134 + 恒定 lr 探针 0.0051，2026-11-19）**，重开条件见 PLAN §4.1——两者跑前未改口径。
- SFT/评测协议（Day 6 定档）：SFT 数据 25% 预训练混入 + assistant-only mask；评测统一 greedy + 关键词判分 + distinct-2/rep-4 + 人工 rubric；**不许用解码调参替代数据修复**。
- 主训练定档（Day 3）：140M bs8×accum8×T1024 · 65,536 tok/step · 45,777 步 · lr 6e-4/warmup 500 · ckpt 每 1000 步 46 件 ≈76GB；命令 = `reports/2026-11-18-day3-140m-probe.md` §6。除该报错/环境变化外不改配置。
- 模型/checkpoint/语料/原始 logs 不入库（.gitignore）；**证据快照三件（md/csv/log）必须入 `reports/` 并跟踪**（`!reports/*.log` 例外，commit 前 `git add -n` 核对）。
- 边界：nl2fem / finetune-lab 是知识上游非资产上游（PLAN §7），只引用知识不改其档案。

## §6 收波校准清单（2026-11-18 盘点批起，每日收波跑一遍）

1. **提交面**：`git status -sb` + `git add -n .`——证据三件（md/csv/log）是否都在待提交列表；数据层只应新增 `SHA256SUMS`。
2. **指纹面**：新数据层 `sha256sum -c`；`data/PROVENANCE.md` 补来源/规模/前缀。
3. **数字面**：当日读数回填 HANDOFF §4 锚点 + PLAN §8；`grep` 旧日期/旧数字残留（如 `Day 2（11-19）`）。
4. **链接面**：README/HANDOFF/PLAN/notes/reports 相对链接 0 断链（盘点批扫描 14 份文档）。
5. **状态面**：HANDOFF §1/§3/§5/§7、README 状态、LAB_NOTEBOOK 当日段、lessons/qa、PLAN 变更记录同步。
