# qa-day-3 — 概念检验题（2026-11-18 收波出题，题源 = Day 3 现场）

> 惯例（HANDOFF §0-5 / PLAN §6-4）：**先自答**——不看资料把答案写进卡内；答不透回 [notes/lessons.md](lessons.md) 补课。昨日题（[qa-day-2.md](qa-day-2.md)）仍空着的话，今天顺手回填——今天的 throughput 读数正好收口题 3（混配比/压缩率的账）。

## 题 1 · 16GB 显存里谁是大头（Day 3 核心）

140M 模型参数 fp32 权重只有 0.55GB、优化器态 1.1GB，但 micro-bs 只能到 8。`F.cross_entropy` 在 bf16 autocast 下实际保留了哪**三份**与 logits 同尺寸的张量？按 bs16×1024×vocab 32000 算各多大？为什么梯度累积摊不薄这块峰值？（提示：bf16 logits 本身 + 内部升 fp32 + 反向保留的 log_softmax；CE 逐 token 独立，micro-batch 内全部位置一次前向就产生全部 logits；累积只在 batch 维度重复。）

**自答**：

**补课**：[reports/2026-11-18-day3-framework.md](../reports/2026-11-18-day3-framework.md) §3 · [reports/2026-11-18-day3-memsweep.log](../reports/2026-11-18-day3-memsweep.log)（OOM 分配尺寸原文）

## 题 2 · 续训到底要恢复什么

`last.pt` 里除了 model/optimizer/step，为什么还要存 torch、cuda、data **三路** RNG？少存 data RNG 会怎样（loss 曲线？val？）？为什么本例恢复后 step 40 的 val 能与 kill 前**一字不差**（7.6893），而 step 41 的 train loss 却不会与"没被杀"的假想轨迹相同？（提示：val = 固定窗口 + eval 模式（无 dropout）+ 同一权重 → 确定性；训练下一步看哪条数据由 data RNG 决定，dropout/采样由 torch/cuda RNG 决定；分布相同不等于序列相同。）

**自答**：

**补课**：[reports/2026-11-18-day3-framework.md](../reports/2026-11-18-day3-framework.md) §4 · `tools/train.py` 续训段注释 · [notes/lessons.md](lessons.md) Day 3 第一条

## 题 3 · 为什么 140M 反而比"按 50M 折算"更快

50M 实测 120,517 tok/s，按 FLOPs 比 2.74× 折算到 140M 应是 ~44.0k，但 140M 实测 **52,250**（高 19%）。6N 口径（每 token 6×参数量 FLOPs）在这个对比里漏掉了什么？为什么 50M 的"单位 FLOP 效率"反而更低？（提示：词表投影 + softmax 的**每 token 成本与模型宽度无关**（V×d 的 lm_head 前向/反向 + 32k 类 softmax），而 50M 的 lm_head 占参数 37%、140M 只占 18%；另外 bs 不同（50M 用 16、140M 用 8），SDPA 在 T=1024 时两者都喂得满。）

**自答**：

**补课**：[reports/2026-11-18-day3-50m-30min.md](../reports/2026-11-18-day3-50m-30min.md) §4 · [reports/2026-11-18-day3-140m-probe.md](../reports/2026-11-18-day3-140m-probe.md) §3

## 加餐 · Day 3 现场题

同一个 140M 模型，eager 52,250 tok/s，`torch.compile` 只有 4,077 tok/s（1/13）。列出至少三个可能原因，并说明为什么"编译后应该更快"这个先验在这台机器上不成立；如果要在 Day 8 重试，你会怎样设计一次**能证伪**的实验？（提示：sm_120 新架构的 inductor 后端覆盖、SDPA/attention 融合是否命中、动态 shape 重编译、编译时间摊到短跑；证伪设计 = 同配置 40 步以上、先预热 20 步再计时、与 eager 同 seed 同数据。）

**自答**：

**补课**：[reports/2026-11-18-day3-framework.md](../reports/2026-11-18-day3-framework.md) §5 · [notes/lessons.md](lessons.md) Day 3 第四条