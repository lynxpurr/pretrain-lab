# qa-day-7 — 概念检验题（2026-11-19 收波出题，题源 = SFT v2/v2b 数据侧修正 + GGUF + rubric）

> 惯例（HANDOFF §0-5 / PLAN §6-4）：**先自答**——不看资料把答案写进卡内；答不透回 [notes/lessons.md](lessons.md) 补课。前日题（[qa-day-5.md](qa-day-5.md)）仍空着的话，今天顺手回填——SFT v2 的评测账正好收口题 1/3。

## 题 1 · 为什么"按列表长度降采样"会误伤数学能力？

SFT v2 为压"文化/艺术/交通"式罗列癖，把 assistant 任一段 ≥5 编号行的样本保留 1/5；结果 `math-add`/`math-mul` 从 v1 的 8/42 退化为 15/72。为什么"列表"这个表面格式会把数学推理一起带走？如果要按"能力域"设计保护规则，你会怎么分类、用什么特征、如何验证保护生效？（提示：长数学题解天然是编号步骤；按文本形状分类 ≠ 按能力分类；v2b 用"用户句含数学关键词+数字，或答案含公式/等式"豁免降采样，列表类仍 13.5% ≤15%。）

**自答**：

**补课**：[notes/lessons.md](lessons.md) Day 7 第一条 · [reports/2026-11-19-day7-eval.md](../reports/2026-11-19-day7-eval.md) · `tools/build_sft_v2.py` `is_math()`

## 题 2 · GGUF 的 q/k permute 在做什么？

把本仓 checkpoint 直接写成 GGUF 后，F16 和 Q4 都能加载，但输出"前几个词正常、随后复读"。为什么补上 `permute_qk()` 就恢复了？这个重排改的是权重行的什么顺序？如果不做，为什么 embedding/FFN 看起来正常、只有注意力错位？（提示：llama.cpp 的 `LlamaModel.permute` 按 head 把 `[n_head,2,head_dim/2,in]` swapaxes(1,2)，对齐 half-split RoPE 的 q/k 维度顺序；RoPE 只作用于 q/k，所以症状集中在注意力。）

**自答**：

**补课**：[notes/lessons.md](lessons.md) Day 7 第二条 · `tools/export_gguf.py` `permute_qk` · llama.cpp `conversion/llama.py` L177-191 · [reports/2026-11-19-day7-deploy.md](../reports/2026-11-19-day7-deploy.md)

## 题 3 · 关键词判分什么时候会同时假阳性和假阴性？

v2 的正确回答"2027 年没有世界杯。世界杯每四年举办一次，所以 2027 年没有冠军。"因 `expect_any` 缺"没有"被判 ❌；v1 的回答"没有官方的官方记录，但以下是 1958…"含"没有官方"却会命中，实际在编造。为什么同一套关键词会同时把正确判错、把错误判对？rubric 应该加哪些断言才能把两者分开？报告里关键词分和 rubric 分应该怎么并列？（提示：关键词只测"是否提到"，不测"是否正确/是否编造"；rubric = 承认不知道/纠正前提 **且** 无编造年份；两者并列，不互相替代。）

**自答**：

**补课**：[notes/lessons.md](lessons.md) Day 7 第四/五条 · `tools/eval_format.py` · `reports/2026-11-19-day7-eval-rubric-v2.md`

## 加餐 · Day 7 工具现场题

`eval.py` 的 CSV 头是 5 列、每行却写了 8 列，rubric 脚本按 `DictReader` 读到 `test_id="greedy"`、`answer="1"`，整张表静默为空。为什么这种 schema 错误不会报错、只会"看起来没数据"？以后写证据 CSV 时，你会加哪一条自检？（提示：DictReader 按头映射、多余列被塞进 `None` 键；自检 = `head -1` + 每行字段数断言 + 关键列取值域检查。）

**自答**：

**补课**：[notes/lessons.md](lessons.md) Day 7 第三条 · `tools/eval.py` CSV 段