# Day 2 32k 中英 BPE tokenizer — 证据快照（2026-11-18）

> 只增不改（PLAN §6-1）。原始数据 = 同目录 `2026-11-18-day2-tokenizer.csv`（压缩率读数）· `2026-11-18-day2-tokenizer.log`（完整 stdout）。产物 = `data/tokenizer-32k/{tokenizer.json,vocab.json,merges.txt,meta.json,SHA256SUMS}`。

## 1. 配置与采样

| 项 | 值 |
|---|---|
| Tokenizer | HF `tokenizers` BPE + **ByteLevel** pre-tokenizer（initial_alphabet = 256 字节 → 任意 UTF-8 无 OOV） |
| 词表 | **32,000**（D-03）· specials：`<|endoftext|>`=0 · `<|im_start|>`=1 · `<|im_end|>`=2 |
| zh 采样 | `minimind_dataset/pretrain_t2t.jsonl` 头部 300.0MB（415,045 docs） |
| en 采样 | `fineweb-edu/sample/10BT` 头部 300.0MB（61,842 docs，按文件名序/row group 序） |
| 留出评测 | 两语言各顺延 5.0MB（zh 6,976 docs / en 1,049 docs，**不参与训练**） |
| 训练耗时 | **271.4s**（BPE merge 训练，单进程；峰值 RSS ~22GB） |

## 2. 压缩率（留出集，同文对拍）

| tokenizer | lang | chars/token | bytes/token | tokens（同文） | ours/ref token 数 |
|---|---|---|---|---|---|
| **ours-32000** | zh | **1.841** | 4.974 | 1,005,383 | **0.721×** |
| minimind-6400 | zh | 1.328 | 3.588 | 1,393,731 | 1.0 |
| **ours-32000** | en | **4.226** | 4.259 | 1,174,915 | **0.696×** |
| minimind-6400 | en | 2.939 | 2.962 | 1,689,068 | 1.0 |

- 同文 token 数比 = 0.721（zh）/ 0.696（en）：32k vs 6.4k 词表的**预期收益**，不是配置错误；en 侧 −30.4% 略越清单 ±30% 边界，解释 = 词表大 5 倍，且中文语料里混有大量英文/符号（zh bytes/token 4.97 即证据）。
- **往返自检通过**：`中文English mixed: 你好，世界! 🌍👩‍🚀 — ﬀ ①𠀀` byte-level 无损（`skip_special_tokens=False`）；specials `[0,1,2]` 解码正确。首次跑挂在自检上暴露过一个语义坑：`decode()` 默认 `skip_special_tokens=True`，会把探针里的特殊 token 字面量吞掉——自检探针因此拆成「普通文本」+「特殊 token」两段。

## 3. 对 Day 3+ 的直接推论（token 账）

| 语料 | 磁盘字节 | 实测 bytes/token | 全库粗估 token | 3B 混配需求 | 消耗占比 |
|---|---|---|---|---|---|
| zh（pretrain_t2t） | 8.275GB | 4.974 | ~1.66B | 1.2B（40%） | **~72%** |
| en（fineweb-edu） | 27.85GB | 4.259 | ~6.54B | 1.8B（60%） | ~28% |

- **决策点①（SkyPile 是否预下载）**：暂不下载——zh 现有库可覆盖 1.2B 需求（约 72%），先跑通 3B；若 Day 6 决策门②要加训 1.5B，zh 侧需复用/补源，届时再拍。
- 混配比按 **token 级 6:4 动态缺口**实现（`tools/build_shards.py`），不依赖 chars→token 估算，编码时直接计数。

## 4. 复现命令

```bash
cd /home/zenz/projects/pretrain-lab
.venv-pre/bin/python -I tools/train_tokenizer.py 2>&1 | tee logs/day2-tokenizer-$(date +%Y%m%d-%H%M%S).log
# → data/tokenizer-32k/ + reports/2026-11-18-day2-tokenizer.csv（~4.5 min）
```

## 5. 指纹与锚点

| 锚 | 值 |
|---|---|
| tokenizer.json sha256 | `05e9ef17eda551bf76cd90fc74ae10fdd4486e58b9289ce2ed8554e24d2066c6` |
| vocab.json / merges.txt sha256 | `5928cdf6…` / `4189dd83…`（详见 `data/tokenizer-32k/SHA256SUMS`） |
| zh 压缩率 | 1.841 chars/token（minimind 1.328） |
| en 压缩率 | 4.226 chars/token（minimind 2.939） |
| 训练耗时 | 271.4s（600MB 中英混采，32k merges） |