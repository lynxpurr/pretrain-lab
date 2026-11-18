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
| 脚本 | `tools/`（model.py 模型 · prepare_* 数据 · train_* 训练 · train_tokenizer.py 训 BPE · build_shards.py 建 memmap 分片；都在仓根跑，勿从子目录启动） |
| run 证据（只增不改） | `reports/<日期>-<主题>.{md,csv,log}` 三分 |
| Tokenizer | `data/tokenizer-32k/`（32k ByteLevel BPE，specials endoftext/im_start/im_end；sha 见其 `SHA256SUMS`；重训 `tools/train_tokenizer.py` ~4.5min） |
| 训练数据 | `data/shards/`（3,000,000,000 token · en 60%/zh 40% · 6×1GB 片 + val 4M · uint16；指纹 `data/shards/SHA256SUMS`；重建 `tools/build_shards.py` ~21min） |
| 数据与指纹 | `data/raw/`（gitignore）+ `data/PROVENANCE.md` + 各层 `SHA256SUMS` |
| 产物 | `out/<run>/last.pt`（gitignore）· `logs/`（gitignore，证据快照拷 reports/） |
| 环境 | `.venv-pre/`（D-07 uv 托管 3.12.13 + torch 2.11.0+cu128；重建命令见 reports/2026-11-18-day0-env-snapshot.md） |

## §3 训练跑批标准动作（Day 1 验证过的最小闭环）

**启动前**（缺一不跑）：
1. 数据现值域自检：`python -c "…memmap.max() < vocab_size…"`（lesson：值域断言前置数据侧）。
2. 锚定预判：首步 loss 应 ≈ ln(vocab_size)（字符级 11765 → 9.37；BPE 32k → 10.37）。跑后第一行日志对账，偏差 >0.2 即停查管线。
3. 冒烟：小配置 60 步内 loss 明显下降（9.43→5.37 是 Day 1 参考形态），再上正式跑。
4. 参数检查：`--max-minutes`（兜底）> 预估时长；`--ckpt-every` ≤ 2000 步；`--eval-every`/`--sample-every` 已设。

**启动**：`tmux new-session -d -s <run>"cd <仓根> && .venv-pre/bin/python tools/train_*.py --out-dir out/<run> --log-dir logs …"`，随后 `tail -3 logs/<run>-*.log` 确认首行正常。脱离 = `Ctrl+b d`（**勿按 Ctrl+C**）。

**监控**（每 10~20 分钟一次，或挂后台守护等会话结束）：
- `grep "tok/s" logs/<run>-*.log | tail -3`（吞吐是否衰减）
- `grep "\[val\]" …`（val 是否下行；train/val 背离 = 过拟合信号）
- `awk` 取 `[sample]` 段（质性信号；固定 prompt 对比不同 step）
- `nvidia-smi --query-gpu=memory.used,temperature.gpu,utilization.gpu --format=csv,noheader`（>80°C 关注散热）

**收波**：证据三分 → `reports/`（md 摘要 + csv + log）→ LAB_NOTEBOOK 当日段 → lessons（有新教训才写）→ qa 题目池 → PLAN 变更记录（有决策/日期变更才写）→ README 状态 → checkpoint/数据指纹补 PROVENANCE → `git commit -m "day-N: …"` + push。

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
| 长任务"日志没进度"/退出码误判 | stale exit 标记、`tee` 缓冲 | 启动前 `rm -f logs/<run>.exit`；判活看 `ps -o pid,etime,%cpu,rss` + 产物文件增长，**不看日志 mtime** |
| 证据 log 未入库 | `.gitignore` 的 `*.log` | `!reports/*.log` 例外；收波 `git add -n .` 核对 md/csv/log 三件 |

## §5 红线

- `reports/` 只增不改；改错走勘误追加。
- 每份数据落位即录指纹（raw 层 17 条 Day 0 已立、字符级 3 条 Day 1 已立、tokenizer 3 条 + 分片 7 条 Day 2 已立；SFT 数据 Day 4 续录）。
- 决策门①（Day 3 吞吐 **140M 等效 ≥3.5 万 token/s**；50M 需 ≥96k 折算或直接跑 140M 探针）/②（Day 6 loss 仍陡降→加训）预注册于 PLAN §4/§4.1，跑前不改。
- 模型/checkpoint/语料/原始 logs 不入库（.gitignore）；**证据快照三件（md/csv/log）必须入 `reports/` 并跟踪**（`!reports/*.log` 例外，commit 前 `git add -n` 核对）。
- 边界：nl2fem / finetune-lab 是知识上游非资产上游（PLAN §7），只引用知识不改其档案。

## §6 收波校准清单（2026-11-18 盘点批起，每日收波跑一遍）

1. **提交面**：`git status -sb` + `git add -n .`——证据三件（md/csv/log）是否都在待提交列表；数据层只应新增 `SHA256SUMS`。
2. **指纹面**：新数据层 `sha256sum -c`；`data/PROVENANCE.md` 补来源/规模/前缀。
3. **数字面**：当日读数回填 HANDOFF §4 锚点 + PLAN §8；`grep` 旧日期/旧数字残留（如 `Day 2（11-19）`）。
4. **链接面**：README/HANDOFF/PLAN/notes/reports 相对链接 0 断链（盘点批扫描 14 份文档）。
5. **状态面**：HANDOFF §1/§3/§5/§7、README 状态、LAB_NOTEBOOK 当日段、lessons/qa、PLAN 变更记录同步。
