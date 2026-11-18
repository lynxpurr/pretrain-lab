# qa-day-2 — 概念检验题（2026-11-18 收波出题，题源 = Day 1 疑问池 + Day 2 现场）

> 惯例（HANDOFF §0-5 / PLAN §6-4）：**先自答**——不看资料把答案写进卡内；答不透回 [notes/lessons.md](lessons.md) 补课。每题给了出处提示，自答完再对照。
> 昨日题（[qa-day-1.md](qa-day-1.md)）仍空着的话，今天顺手回填——今天的 tokenizer 实测正好收口题 3（27.85GB parquet ≠ token 数）。

## 题 1 · 32k BPE 的压缩率账（Day 2 核心）

留出集实测：ours-32000 在 zh 上 **1.841 chars/token**、en 上 **4.226**；minimind-6400 是 1.328 / 2.939。为什么词表大 5 倍，token 数只降 ~28~30%？`chars/token` 与 `bytes/token` 各说明什么？为什么 en 的 bytes/token（4.259）几乎等于 chars/token（4.226），而 zh 的 bytes/token（4.974）远大于 chars/token（1.841）？（提示：UTF-8 里中英字符的字节宽度；BPE merge 的边际收益递减；pretrain_t2t 是"中文为主但混大量英文/符号"的指令语料。）

**自答**：

**补课**：[reports/2026-11-18-day2-tokenizer.md](../reports/2026-11-18-day2-tokenizer.md) §2 · `data/tokenizer-32k/meta.json` · tokenizers `ByteLevel` 文档

## 题 2 · ln(V) 锚的换轨用法（Day 1 教训迁移）

字符级 11,765 词表首步 loss 9.4316 ≈ ln(11765)=9.3727；换到 32k BPE，为什么首步应 ≈ ln(32000)=**10.3734**？如果实测明显**偏低**，先查什么？明显**偏高**，又先查什么？（提示：随机初始化时 logits≈0 → softmax 均匀 → CE=ln(V)；偏低常意味着"见过答案"——标签偏移/重复数据；偏高常意味着 id 与 vocab 不一致——值域/特殊 token/取批错位。）

**自答**：

**补课**：[notes/lessons.md](lessons.md) Day 0~1 第三条 · `tools/train_char20m.py` 首步日志 · [reports/2026-11-18-day2-smoke.md](../reports/2026-11-18-day2-smoke.md)

## 题 3 · 混配比与 val 划分（Day 2 工程决策）

为什么混配比要按 **token 计数**而不是按文件字节数或文档数？`tools/build_shards.py` 的"累计缺口调度"如何保证 en:zh≈6:4？val 用 `hash % 500 == 0` 做**文档级**划分，相比"头部切分"和"随机行切分"好在哪？预算满后多余的 val 候选为什么丢弃而不是塞回 train？（提示：压缩率随语言/内容而变；文档级防泄漏；哈希划分可复现且不依赖读取顺序；val/train 混用会让"留出"名存实亡。）

**自答**：

**补课**：`tools/build_shards.py` 模块注释 + `DocFilter` 段 · [reports/2026-11-18-day2-shards.md](../reports/2026-11-18-day2-shards.md) §1~2

## 加餐 · Day 2 现场题

`tokenizer.decode(ids)` 默认 `skip_special_tokens=True`——这意味着写"编码→解码往返自检"时要注意什么？为什么自检探针里混入 `<|endoftext|>` 字面量会让断言莫名失败？（提示：特殊 token 默认被解码器吞掉；探针应拆成普通文本 + specials 两段。）

**自答**：

**补课**：`tools/train_tokenizer.py` 自检段注释 · LAB_NOTEBOOK Day 2 现象条