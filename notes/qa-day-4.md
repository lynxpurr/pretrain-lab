# qa-day-4 — 概念检验题（2026-11-18 收波出题，题源 = Day 4 现场）

> 惯例（HANDOFF §0-5 / PLAN §6-4）：**先自答**——不看资料把答案写进卡内；答不透回 [notes/lessons.md](lessons.md) 补课。昨日题（[qa-day-3.md](qa-day-3.md)）仍空着的话，今天顺手回填——SFT 的 mask 账正好收口题 1。

## 题 1 · SFT 的 label 右移与 `ignore_index=-100`

我们的 `train.bin` 与 `train.labels.bin` 是**同一偏移的配对**：`labels[i]` 是"位置 i 应该预测的 token"，而不是"位置 i 的 token"。为什么必须这样设计（而不是像预训练那样用 `x` 右移一位）？`F.cross_entropy(..., ignore_index=-100)` 在求平均时**分母**是全部位置还是非 -100 的位置？如果 user 段不 mask 会学到什么坏习惯？（提示：配对布局让"哪些位置算 loss"完全由数据侧决定；`ignore_index` 既跳过 loss 也跳过梯度；不 mask 则模型会学习复述提问、并在 user 段末尾预测 assistant 的开头，等于把"该说什么"变成"该抄什么"。）

**自答**：

**补课**：`tools/build_sft.py` `BlockWriter._flush` + `conversation_segments` 注释 · [reports/2026-11-18-day3-framework.md](../reports/2026-11-18-day3-framework.md) §1

## 题 2 · 为什么"会话不跨块"

把 token 流按 1024 硬切（跨块）能多塞进 ~13% 的 token，但我们在 `build_sft.py` 里选择"装不下就补 EOS 收块"。跨块的具体代价是什么？为什么块尾 `label` 必须是 -100？（提示：后半段缺 `<|im_start|>` 头 → 模型在缺失上下文的 fragment 上算 loss；块尾 label 若指向下一块的 token，就等价于教模型"块边界处任意跳转"，且下一块的 token 位置不在本块视野内、无法用段级断言校验。）

**自答**：

**补课**：[notes/lessons.md](lessons.md) Day 4 第二条 · `tools/build_sft.py` `BlockWriter.add_conversation`

## 题 3 · 25% 预训练混入为什么能压幻觉

SFT 数据里按块混入 25% 的预训练语料（正常 LM 目标）。从优化目标的角度解释：纯 SFT 训练会把模型推向什么分布？混入预训练项相当于给目标加了什么约束？为什么"按块混"和"按样本混"在数学上不完全等价、但都能起作用？（提示：纯 SFT 只在这些问答对上最小化 CE → 分布收窄到 SFT 的说话方式，对训练分布外的事实问题更容易编；混入项等价于 λ·CE_SFT + (1−λ)·CE_LM 的多任务目标，抑制参数偏离预训练解；块级 vs 样本级只是混合粒度，块内不再混合 → 梯度方差更大但期望相同。）

**自答**：

**补课**：PLAN §5 风险表「SFT 后小模型幻觉加重」行 · `data/sft-mix/meta.json` 的 `pretrain_mix` 段

## 加餐 · Day 4 现场题

主训练 bs8 的峰值显存是 10.51GB，而 eval 用 bs16 时峰值**也是 10.51GB**。evals 是 forward-only（没有梯度和优化器态），为什么显存没有明显下降？（提示：eval 的常驻部分是参数 fp32 2.2GB + CE 的三份副本（B·T·V·2 + 2×B·T·V·4，bs16 时约 5.25GB），而 forward-only 的中间激活在 `no_grad` 下逐层释放；训练时 bs8 的激活 ~3GB + CE ~2.6GB + 参数/优化器 2.2GB ≈ 10.5GB，两条路径恰好都落在同一个量级——**显存上限往往由与 batch 线性增长的 CE 副本而非激活决定**。）

**自答**：

**补课**：[reports/2026-11-18-day3-framework.md](../reports/2026-11-18-day3-framework.md) §3 · Day 4 预检日志（`[val] ... peak 9.49 / 10.51 GB`）