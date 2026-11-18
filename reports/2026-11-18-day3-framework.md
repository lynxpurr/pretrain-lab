# Day 3 · 完整训练框架 + 显存边界 + 续训闭环

> 2026-11-18 · 产出 = `tools/train.py`（Day 4 主训练载具）· 证据同目录：`2026-11-18-day3-{50m-smoke,memsweep,resume-killed,resume-restored}.{log,csv}` · 吞吐读数见 `2026-11-18-day3-50m-30min.md` 与 `2026-11-18-day3-140m-probe.md`
> 任务来源：HANDOFF §7 清单 1/2/3（框架 · 续训 · 50M 配置定档）· PLAN §4.1（配置/时长/ckpt 预算）

## 1. 框架设计（`tools/train.py`，约 430 行）

相比 Day 1 `train_char20m.py`（最小闭环）新增六件，全部为本仓自建：

| # | 能力 | 实现要点 |
|---|---|---|
| 1 | **多分片 memmap 取批** | `ShardedTrainData`：读 `data/shards/meta.json` 的 shards 清单 → 6 个 `np.memmap`；按各片 token 数加权选片（片内同分布，跨片拼接无收益），片内均匀随机取窗口；一次读 `T+1` 个 token，x/y 共享同一缓冲（省一半拷贝）。同时兼容单文件 `train.bin`（`data/bpe-smoke` 老路径不掉） |
| 2 | **梯度累积 + token 预算定步数** | `tokens_per_step = micro_bs × T × grad_accum = 8×1024×8 = 65,536`；`total_steps = ceil(target_tokens / tokens_per_step)` → **LR 调度与墙钟解耦**，中断续训后 cosine 仍落在同一条上（`--max-minutes` 只做兜底） |
| 3 | **续训闭环** | `last.pt` = model / optimizer / step / tokens_seen / **torch+cuda+data 三路 RNG** / config；`--resume auto` 读 `out/<run>/last.pt`，加载前逐项校验 config 一致（防静默换配置） |
| 4 | **可比的 val** | `FixedValData`：块编号 `permutation(n_blocks)` 固定种子抽样、块不重叠 → 不同 step / 不同 resume / 不同 run 的 val 读数直接可比（本例恢复后 step 40 的 val 与 kill 前**完全相同**） |
| 5 | **采样可读性** | HF `tokenizers` 直接编解码，`decode(..., skip_special_tokens=False)`（Day 2 坑的正面用法）；固定 4 条 prompt（中 2 英 2），每 `--sample-every` 步写入 log（附带 `<|endoftext|>` 可见性 = 解码链路自检） |
| 6 | **可观测 + 可判活** | csv 每 log/eval 行 flush（列：step/train_loss/val_loss/lr/tok_per_s/tokens_seen/elapsed_s/peak_gb）；吞吐双读数（窗口含开销、纯训练扣掉 eval/sample/ckpt 墙钟）；`logs/<run>.exit` 写 `EXIT:0/1`（stale exit 教训机制化；启动前自动删除旧标记） |

补充：`--grad-ckpt`（逐块激活检查点）与 `--compile` 为可选实验项，均已实测（见 §3/§5），默认关闭。

## 2. 50M 冒烟（100 步，正式配置）

配置：d576/L8/H9（**50,292,288** 参数）· T1024 · bs16×accum4 = 65,536 tok/step · lr 6e-4 warmup50。证据 `2026-11-18-day3-50m-smoke.{log,csv}`。

| 项 | 读数 |
|---|---|
| 首步 loss 锚 | **10.4756** vs ln(32000)=10.3735（**+0.102**，与 Day 2 同词表冒烟 +0.081 同量级） |
| loss / val | 100 步 10.47 → **6.9312**；val@50 7.4547 → **val@100 6.9161** |
| 吞吐 | **116,274 tok/s**（纯训练；为 30min 跑 120.5k 的前哨） |
| 峰值显存 | 10.72 GB（含常驻 laya-triage 1.8G） |
| 采样（step 100） | 中文 prompt 出中文片段（"…希望这些，他们影响将可以描述的…"）、EOS `<|endoftext|>` 原样可见 → tokenizer 解码链路正确；英文样本为通顺但无意义的续写（100 步 = 650 万 token，符合预期） |

## 3. 显存边界扫描（16GB 卡 + 1.78GB 常驻）

证据 `2026-11-18-day3-memsweep.log`（每配置 4 步，含 OOM 现场原文）。

| 模型 | micro-bs | grad-ckpt | expandable_segments | 峰值 | 结果 |
|---|---|---|---|---|---|
| 50M d576/L8/H9 | 16 | — | — | **10.53 GB** | ✅ 封顶配置 |
| 50M | 24 | — | — | — | ❌ OOM：`Tried to allocate 2.93 GiB` |
| 50M | 32 / 48 | — | — | — | ❌ OOM（3.91 / 2.93 GiB 分配失败） |
| 140M d768/L16/H12 | 4 | — | — | 5.99 GB | ✅ |
| 140M | 6 | — | — | 7.98 GB | ✅ |
| 140M | 8 | — | — | **10.03 GB** | ✅ 封顶配置（主训练采用） |
| 140M | 10 | — | — | — | ❌ OOM（12.19GB allocated 后仍差 1.22GB） |
| 140M | 10 | — | ✅ | 12.05 GB | ✅（仅多 2GB 余量，不提速，不采用） |
| 140M | 12 | — | ✅ | — | ❌ OOM |
| 140M | 16 | ✅ | ✅ | 8.84 GB | ✅ 但吞吐降到 40,449 tok/s（重算代价） |

**为什么是交叉熵卡住显存（关键账）**：参数/优化器态只占 2.2GB（140M：fp32 权重 0.55 + 梯度 0.55 + Adam 两态 1.10），大头是 `lm_head` 的 logits 三份副本——autocast 下 logits 本身 bf16（B·T·V·2），`F.cross_entropy` 内部把 logits 升 fp32 做 log_softmax 且为反向保留输出（各 B·T·V·4）。bs16×1024×32000 时三份 ≈ 1.05 + 2.10 + 2.10 = **5.25 GB**；bs24 时单份升到 3.14GB，直接撞墙。**梯度累积摊薄不了这块**：CE 是逐 token 独立的，micro-batch 内所有位置一次性算完才 backward，累积省的是 batch 维度的重复，不是单次前向的 logits 体积。这也解释了 50M（词表投影占参数 37%）为什么比 140M 更容易先撞 CE 上限。

## 4. 续训闭环（硬 kill 实验）

流程：50M bs16×accum4、ckpt-every 40、max-steps 160 → 跑到 step ~55 时 `kill -9`（模拟崩溃，非优雅退出）→ `--resume auto` 续到 160。证据 `2026-11-18-day3-resume-{killed,restored}.log`。

| 检查 | 读数 | 判定 |
|---|---|---|
| 被杀时的最后 checkpoint | `ckpt-0000040.pt` / `last.pt`（无 exit 标记 = 硬崩溃现场） | ✓ |
| 恢复日志 | `[resume] out/day3-resume/last.pt → step=40 / total=160 tokens_seen=2,621,440` | ✓ step 与 tokens_seen 精确对齐（40×65,536） |
| **val 连续性** | kill 前 step 40 val **7.6893** → 恢复后立刻重算 step 40 val **7.6893** | ✓ 一字不差（固定 val 窗口 + eval 模式无 dropout） |
| loss 连续性 | step 41 起 7.6x → 6.49 @160，曲线无跳变 | ✓ 优化器态（含 Adam moments）完整恢复 |
| 收尾 | `EXIT:0 step=160 val=6.5226 tps=123701` | ✓ |

**踩到的坑（已修）**：`torch.load(..., map_location="cuda")` 把 RNG 字节张量也搬上 GPU，`torch.set_rng_state` 要求 CPU ByteTensor → `TypeError: RNG state must be a torch.ByteTensor`。修法 = 加载后 `.cpu()`。**这就是清单第 2 项要求"kill 一次验证"的价值：不跑这一步，主训练第一次续训才会炸。**

## 5. torch.compile 负面结果（已弃用）

140M bs8 + `--compile`：10 步用时 34s，**纯训练 4,077 tok/s**（约为基线的 1/13），峰值显存 7.12GB。首步编译 18s，其后每步仍 ~1.5s（基线 0.16s/步）——sm_120 上 inductor 对 SDPA/注意力的代码生成未走快路径。**结论：不引入 compile；记录在案避免 Day 8 "再试一次"浪费时间。**

## 6. 复现命令

```bash
cd /home/zenz/projects/pretrain-lab
# 冒烟（100 步，~1 min）
.venv-pre/bin/python -I tools/train.py --run-name x --n-embd 576 --n-layer 8 --n-head 9 \
  --block-size 1024 --batch-size 16 --grad-accum 4 --target-tokens 6553600 --max-steps 100 \
  --eval-every 50 --sample-every 50 --ckpt-every 100 --out-dir out/x
# 续训检查
.venv-pre/bin/python -I tools/train.py --run-name x --resume auto [同配置]
```