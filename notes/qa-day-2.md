# qa-day-2 — 概念检验题（2026-11-18 收波出题，题源 = Day 1 疑问池 + Day 2 现场）

> 惯例（HANDOFF §0-5 / PLAN §6-4）：**先自答**——不看资料把答案写进卡内；答不透回 [notes/lessons.md](lessons.md) 补课。每题给了出处提示，自答完再对照。
> 昨日题（[qa-day-1.md](qa-day-1.md)）仍空着的话，今天顺手回填——今天的 tokenizer 实测正好收口题 3（27.85GB parquet ≠ token 数）。
> **本卡已由 agent 预答（2026-11-20，qa-day-8 模式）**：答案可直接复核/改写；先自己答一遍再看效果最好。

## 题 1 · 32k BPE 的压缩率账（Day 2 核心）

留出集实测：ours-32000 在 zh 上 **1.841 chars/token**、en 上 **4.226**；minimind-6400 是 1.328 / 2.939。为什么词表大 5 倍，token 数只降 ~28~30%？`chars/token` 与 `bytes/token` 各说明什么？为什么 en 的 bytes/token（4.259）几乎等于 chars/token（4.226），而 zh 的 bytes/token（4.974）远大于 chars/token（1.841）？（提示：UTF-8 里中英字符的字节宽度；BPE merge 的边际收益递减；pretrain_t2t 是"中文为主但混大量英文/符号"的指令语料。）

**自答**：32k 相对 6.4k 词表大 5 倍，但 zh/en 的 token 数只降 **27.9% / 30.5%**——BPE merge 收益是长尾递减：高频中文词在 6.4k 里基本已成型，新增词表吃的是低频词/子词与英文碎片。`chars/token` 是**语言内压缩率**（同语言跨词表可比），`bytes/token` 是**跨语言可比的存储/算力口径**：en 是 ASCII，1 字节/字符，所以 4.259 ≈ 4.226；zh 是 UTF-8 3 字节/字符再混少量 ASCII/标点，平均 **4.974/1.841 ≈ 2.70 字节/字符**——两个指标回答不同问题，不能混用。

**补课**：[reports/2026-11-18-day2-tokenizer.md](../reports/2026-11-18-day2-tokenizer.md) §2 · `data/tokenizer-32k/meta.json` · tokenizers `ByteLevel` 文档

## 题 2 · ln(V) 锚的换轨用法（Day 1 教训迁移）

字符级 11,765 词表首步 loss 9.4316 ≈ ln(11765)=9.3727；换到 32k BPE，为什么首步应 ≈ ln(32000)=**10.3734**？如果实测明显**偏低**，先查什么？明显**偏高**，又先查什么？（提示：随机初始化时 logits≈0 → softmax 均匀 → CE=ln(V)；偏低常意味着"见过答案"——标签偏移/重复数据；偏高常意味着 id 与 vocab 不一致——值域/特殊 token/取批错位。）

**自答**：随机初始化时 logits≈0 → softmax 均匀 → CE=ln(V)=ln(32000)=**10.3734**，这是"模型还没学到任何东西"的免费锚。实测明显**偏低** = 见过答案：先查 labels 右移/配对错位、冒烟批次与训练数据重叠、重复数据；明显**偏高** = id 与词表不一致：值域越界、special token id、取批错位。容差随规模放宽（22M +0.06 / 140M +0.17），落在 `ln(V)+0~0.25` 且不接近 0 才算正常。

**补课**：[notes/lessons.md](lessons.md) Day 0~1 第三条 · `tools/train_char20m.py` 首步日志 · [reports/2026-11-18-day2-smoke.md](../reports/2026-11-18-day2-smoke.md)

## 题 3 · 混配比与 val 划分（Day 2 工程决策）

为什么混配比要按 **token 计数**而不是按文件字节数或文档数？`tools/build_shards.py` 的"累计缺口调度"如何保证 en:zh≈6:4？val 用 `hash % 500 == 0` 做**文档级**划分，相比"头部切分"和"随机行切分"好在哪？预算满后多余的 val 候选为什么丢弃而不是塞回 train？（提示：压缩率随语言/内容而变；文档级防泄漏；哈希划分可复现且不依赖读取顺序；val/train 混用会让"留出"名存实亡。）

**自答**：配比按 token 而非字节/文档——同一段中英文的 token 数差 2~4 倍（zh 1.841 vs en 4.226 chars/token），按字节会把中文份额系统性放大。缺口调度 = 每一步取"累计占比低于目标"的语言，使 en:zh 收敛 6:4（偏差 <0.01%）。val 用 `hash%500` 做**文档级**留出：整篇留出防近邻泄漏、不依赖读取顺序、可复现；头部切分有来源/时间偏差，随机行切分会把同一文档拆进 train/val。预算满后多余 val 候选丢弃——val 必须**固定且留出**，塞回 train 就是泄漏，扩 val 则改变评测口径。

**补课**：`tools/build_shards.py` 模块注释 + `DocFilter` 段 · [reports/2026-11-18-day2-shards.md](../reports/2026-11-18-day2-shards.md) §1~2

## 加餐 · Day 2 现场题

`tokenizer.decode(ids)` 默认 `skip_special_tokens=True`——这意味着写"编码→解码往返自检"时要注意什么？为什么自检探针里混入 `<|endoftext|>` 字面量会让断言莫名失败？（提示：特殊 token 默认被解码器吞掉；探针应拆成普通文本 + specials 两段。）

**自答**：`decode()` 默认 `skip_special_tokens=True`：special token 会被解码器吞掉，往返自检必须显式传 `False`，否则"编码→解码"看起来少了标记。文本里字面量 `<|endoftext|>` 可能先被编码成 special id、再被默认吞掉，断言就会莫名失败；探针要拆成"普通文本"与"specials"两段分别断言。

**补课**：`tools/train_tokenizer.py` 自检段注释 · LAB_NOTEBOOK Day 2 现象条