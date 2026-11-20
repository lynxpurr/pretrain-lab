# qa-day-7 — 概念检验题（2026-11-19 收波出题，题源 = SFT v2/v2b 数据侧修正 + GGUF + rubric）

> 惯例（HANDOFF §0-5 / PLAN §6-4）：**先自答**——不看资料把答案写进卡内；答不透回 [notes/lessons.md](lessons.md) 补课。前日题（[qa-day-5.md](qa-day-5.md)）仍空着的话，今天顺手回填——SFT v2 的评测账正好收口题 1/3。
> **本卡已由 agent 预答（2026-11-20，qa-day-8 模式）**：答案可直接复核/改写；先自己答一遍再看效果最好。

## 题 1 · 为什么"按列表长度降采样"会误伤数学能力？

SFT v2 为压"文化/艺术/交通"式罗列癖，把 assistant 任一段 ≥5 编号行的样本保留 1/5；结果 `math-add`/`math-mul` 从 v1 的 8/42 退化为 15/72。为什么"列表"这个表面格式会把数学推理一起带走？如果要按"能力域"设计保护规则，你会怎么分类、用什么特征、如何验证保护生效？（提示：长数学题解天然是编号步骤；按文本形状分类 ≠ 按能力分类；v2b 用"用户句含数学关键词+数字，或答案含公式/等式"豁免降采样，列表类仍 13.5% ≤15%。）

**自答**：长数学题解天然是"编号步骤"（`1. 设… 2. 列式… 3. 得…`），所以**"列表"这个表面格式与"数学推理"高度重合**。v2 对 assistant 任一段 ≥5 编号行的样本保留 1/5，等于把数学题解砍掉 80% → math-add 15、math-mul 72（v1 是 8/42）。能力域保护要问"这条样本靠什么特征教这个能力"：v2b 用"用户句含数学关键词+数字，或答案含公式/等式"豁免（列表 13.53%），数学修回但 rep-4 0.117；v2c 再收窄到**assistant 等式行 ≥3 的练习列表**（6,243 条），math 8/42 且列表 10.55%。验证 = 数学读数 + 列表占比 ≤15% + 相邻复读指标不被抬回。

**补课**：[notes/lessons.md](lessons.md) Day 7 第一条 · [reports/2026-11-19-day7-eval.md](../reports/2026-11-19-day7-eval.md) · `tools/build_sft_v2.py` `is_math()`

## 题 2 · GGUF 的 q/k permute 在做什么？

把本仓 checkpoint 直接写成 GGUF 后，F16 和 Q4 都能加载，但输出"前几个词正常、随后复读"。为什么补上 `permute_qk()` 就恢复了？这个重排改的是权重行的什么顺序？如果不做，为什么 embedding/FFN 看起来正常、只有注意力错位？（提示：llama.cpp 的 `LlamaModel.permute` 按 head 把 `[n_head,2,head_dim/2,in]` swapaxes(1,2)，对齐 half-split RoPE 的 q/k 维度顺序；RoPE 只作用于 q/k，所以症状集中在注意力。）

**自答**：llama.cpp 的 `LlamaModel.permute` 按 head 把 q/k 权重从 `[n_head, 2, head_dim/2, in]` 做 `swapaxes(1,2)`，对齐 **half-split RoPE** 的维度顺序（RoPE 把 head_dim 切成前后两半做旋转）。不做这一步，权重行顺序与推理时的 RoPE 布局错位 → q/k 投影"看起来有值但语义错"，注意力从第一个 token 起就偏；embedding/FFN 不参与 RoPE，所以它们正常。症状就是"前几个词正常、随后复读/跑偏"——**不是量化坏，是布局坏**。

**补课**：[notes/lessons.md](lessons.md) Day 7 第二条 · `tools/export_gguf.py` `permute_qk` · llama.cpp `conversion/llama.py` L177-191 · [reports/2026-11-19-day7-deploy.md](../reports/2026-11-19-day7-deploy.md)

## 题 3 · 关键词判分什么时候会同时假阳性和假阴性？

v2 的正确回答"2027 年没有世界杯。世界杯每四年举办一次，所以 2027 年没有冠军。"因 `expect_any` 缺"没有"被判 ❌；v1 的回答"没有官方的官方记录，但以下是 1958…"含"没有官方"却会命中，实际在编造。为什么同一套关键词会同时把正确判错、把错误判对？rubric 应该加哪些断言才能把两者分开？报告里关键词分和 rubric 分应该怎么并列？（提示：关键词只测"是否提到"，不测"是否正确/是否编造"；rubric = 承认不知道/纠正前提 **且** 无编造年份；两者并列，不互相替代。）

**自答**：关键词只测"提到"，同时缺"正确性"和"编造检查"两个维度：正确答案"2027 年没有世界杯…没有冠军"因为 `expect_any` 里没有"没有"被判 ❌（**假阴**）；v1 的"没有官方的官方记录，但以下是 1958…"含"没有官方"会命中、实际在编造（**假阳**）。rubric 要加两条断言：**承认不知道/纠正前提** 且 **无编造年份/事实**；报告里关键词分与 rubric 分并列（v2 该题关键词 ❌ / rubric ✅），不互相替代。

**补课**：[notes/lessons.md](lessons.md) Day 7 第四/五条 · `tools/eval_format.py` · `reports/2026-11-19-day7-eval-rubric-v2.md`

## 加餐 · Day 7 工具现场题

`eval.py` 的 CSV 头是 5 列、每行却写了 8 列，rubric 脚本按 `DictReader` 读到 `test_id="greedy"`、`answer="1"`，整张表静默为空。为什么这种 schema 错误不会报错、只会"看起来没数据"？以后写证据 CSV 时，你会加哪一条自检？（提示：DictReader 按头映射、多余列被塞进 `None` 键；自检 = `head -1` + 每行字段数断言 + 关键列取值域检查。）

**自答**：`DictReader` 按**表头**做键映射：表头 5 列、行有 8 列时，多出的 3 列被塞进 `None` 键，不会抛错；于是 `test_id` 读到 `"greedy"`、`answer` 读到 `"1"`，整表"看起来没数据"。自检三件：`head -1` 核对表头、逐行断言字段数 == 表头数、关键列取值域检查（`pass ∈ {0,1}`、`rep4 ∈ [0,1]`）。写完 CSV 立刻跑，别等到 rubric 读空才发现。

**补课**：[notes/lessons.md](lessons.md) Day 7 第三条 · `tools/eval.py` CSV 段