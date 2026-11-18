# qa-day-1 — 概念检验题（2026-11-18 收波出题，题源 = Day 0 疑问池 + Day 1 现场加餐）

> 惯例（HANDOFF §0-5 / PLAN §6-4）：**先自答**——不看资料把答案写进卡内；答不透回 [notes/lessons.md](lessons.md) 补课。每题给了出处提示，自答完再对照。

## 题 1 · venv 断链免疫（Day 0 疑问①）

为什么 uv 托管解释器（`uv venv --python=3.12`）能免疫系统 python 升级导致的 venv 断链，而链 `/usr/bin/python3.x` 的 venv 会断？（提示：`readlink -f .venv-pre/bin/python3` 指向哪？venv 的 `pyvenv.cfg` 里 `home` 写的是什么？）

**自答**：

**补课（自答后再看）**：PLAN D-07 · nl2fem 2026-11-18 双 venv 断链实录 · `~/.local/share/uv/python/`

## 题 2 · 50 系为什么必须 cu128（Day 0 疑问②）

RTX 5070 Ti（sm_120）为什么必须 CUDA ≥ 12.8 的 PyTorch wheel？装了 cu118/cu124 的 torch 会在哪一步报什么错？（提示：`torch.cuda.get_arch_list()` 里没有 sm_120 意味着什么？报错发生在 import 时、首次 .cuda() 时，还是 kernel launch 时？）

**自答**：

**补课**：PLAN §5 风险表第 1 条 · finetune-lab PLAN §9 · [reports/2026-11-18-day0-env-snapshot.md](../reports/2026-11-18-day0-env-snapshot.md)

## 题 3 · parquet 字节数 ≠ token 数（Day 0 疑问③，Day 2 实测收口）

27.85GB 的 FineWeb-Edu parquet 为什么不能直接换算成 token 数？在用自训 32k BPE 实测计数之前，至少有哪三个换算环节是未知数？（Day 2 训完 tokenizer 实测后，把数字回填 data/PROVENANCE.md——这道题的最终答案就是 Day 2 的产出之一。）

**自答**：

**补课**：data/PROVENANCE.md 预训练语料表 · Day 2 压缩率读数（reports/）

## 加餐 · Day 1 现场题

`str.translate` 查表编码为什么会漏字符（表外字符的默认行为是什么）？如何从"设计"上让这类 bug 死在数据准备阶段，而不是训练阶段才炸？

**自答**：

**补课**：[notes/lessons.md](lessons.md) Day 0~1 首条 · tools/prepare_char20m.py 编码段注释
