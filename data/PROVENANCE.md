# PROVENANCE — 数据出处与指纹（Day 0 预下载起即记账）

> 纪律（PLAN §6-6，平移自 finetune-lab）：每份数据落位即录来源、许可证、指纹；语料分片 / tokenizer / SFT 数据三表分开记。**指纹不一致 = 数据被动过，先查再训。**

## 预训练语料（Day 2 产出 memmap 分片）

| 数据集 | 来源与版本 | 许可证 | 规模 | 指纹（sha256 前缀） | 落位 |
|---|---|---|---|---|---|
| FineWeb-Edu sample-10BT（英文主力） | HF `HuggingFaceFW/fineweb-edu` @ main，经 hf-mirror（2026-11-18 Day 0 下载，14 个 parquet 分片） | ODC-BY v1.0（另受 CommonCrawl ToU 约束） | 27.85GB（上游名义 10B GPT-2 token；本仓 32k BPE 实测 4.259 bytes/token → 全库约 **6.5B token**） | 14 片各自前缀见 `data/raw/SHA256SUMS`（首片 `b1ba7b2ce4cb5ea6`，末片 `b393f51fefab26cd`） | `data/raw/fineweb-edu/sample/10BT/` |
| minimind pretrain_t2t（中文主力） | HF `jingyaogong/minimind_dataset` @ main，经 hf-mirror（ModelScope 无此库，回落渠道）；现行文件名对照 minimind 仓 README L122-423 | Apache-2.0 | 8.275GB（中英混合、中文为主；本仓 32k BPE 实测 4.974 bytes/token → 全库约 **1.66B token**） | `31efc9a6fa743076` | `data/raw/minimind_dataset/pretrain_t2t.jsonl` |
| Day 1 字符级切片（字符级闭环专用，可再生产物） | 从 pretrain_t2t 流式切片：train 301,469,872 / val 3,010,935 字符，词表 11,765（覆盖 99.9968%），文档级切分 | 继承上游 Apache-2.0 | train.bin 575.0MB + val.bin 5.7MB | train `00ad3d6eda6fe4ed` · val `2820a2563965c0e8` · meta `b6ce2b1a9068eee9`（全量见 `data/day1-char20m/SHA256SUMS`） | `data/day1-char20m/`（重跑 `tools/prepare_char20m.py` 可再生） |

> 原始下载层全量指纹 = `data/raw/SHA256SUMS`（17 条，Day 0 记账）；Day 1 字符级切片 = `data/day1-char20m/SHA256SUMS`（3 条）；Day 2 tokenizer = `data/tokenizer-32k/SHA256SUMS`（3 条）；Day 2 memmap 分片 = `data/shards/SHA256SUMS`（7 条）——各层均入库（PLAN §6-6）。

## Memmap 分片（Day 2 产出，训练集）

| 件 | 构成 | 规模 | 指纹（sha256 前缀） |
|---|---|---|---|
| train 分片 `shard-000…005.bin` | 32k BPE token 流，en:zh = 60:40（token 级），每文档尾接 `<|endoftext|>`(0)；每片 536,870,912 token（末片 315,645,440） | 合计 **3,000,000,000 token** / 6.0GB | `f60bfe17` · `3fcba79b` · `00cea4c7` · `72a601f6` · `b8bb1577` · `ffe7068a` |
| `val.bin` | 文档级 `hash % 500` 留出，en 2.4M / zh 1.6M | 4,000,000 token / 7.6MB | `a549752d` |
| `data/bpe-smoke/` | shard-000 头部切片（train 50M + val 2M），换轨冒烟专用 | 50M + 2M token | 可再生（`build_shards.py` 自动生成） |

> 全量指纹与分片 token 数见 `data/shards/SHA256SUMS` + `meta.json`；构建证据 = `reports/2026-11-18-day2-shards.md`（实测去重率 en 0.68% / zh 0.00%，值域 max_id=31999）。**指纹一致性检查**：`cd data/shards && sha256sum -c SHA256SUMS`（2026-11-18 全 OK）。

## 模型 checkpoint（本地产物，gitignore；指纹用于对账/续训）

| 件 | 来源 | 规模 | 指纹（sha256 前缀） | 落位 |
|---|---|---|---|---|
| day1-char20m last.pt | Day 1 字符级 20M 终版（step 33000，val 1.5599，含 optimizer 态） | 266.7MB | `5d97b5f73852a2e9` | `out/day1-char20m/last.pt`（`reports/2026-11-18-day1-char20m.md` 有完整配置与复现命令） |
| day3-50m last.pt | Day 3 50M 30min 预注册跑终版（d576/L8/H9 = 50,292,288；step 3292，val 3.6377，含 optimizer + 三路 RNG 态） | 603.6MB | `71fc274be289c3c2` | `out/day3-50m/last.pt`（`reports/2026-11-18-day3-50m-30min.md`） |
| day3-140m-probe last.pt | Day 3 140M 探针（d768/L16/H12 = 137,847,552；step 40，val 8.9169；门①判定用） | 1.65GB | `df8fc7ac351415db` | `out/day3-140m-probe/last.pt`（`reports/2026-11-18-day3-140m-probe.md`） |
| **main140m last.pt** | **Day 4~5 正式主训练终版**（d768/L16/H12 = 137,847,552；step 45,777 · 3,000,041,472 token · **val 2.7709** · 52,171 tok/s · 16h07m41s；含 optimizer + 三路 RNG 态） | 1.65GB | `0c0096cc172e8a58` | `out/main140m/last.pt` + **谱系 46 个 `ckpt-XXXXXXX.pt`**（step 1000…45777，共 73GB）（`reports/2026-11-19-day4-main140m.md`） |
| **sft-v1 last.pt** | **Day 5 SFT v1 终版**（同架构 137,847,552；3,815 步 / 250M token / **SFT val 1.5515** / 1h19m26s；含 optimizer 态） | 1.65GB | `853322df4583bfa2` | `out/sft-v1/last.pt`（`reports/2026-11-19-day5-eval.md` · `...-sft-v1.log`） |

## Tokenizer（Day 2 产出）

| 件 | 训练语料 | 词表 | 指纹 | 落位 |
|---|---|---|---|---|
| `tokenizer-32k`（BPE + ByteLevel） | zh：pretrain_t2t 头部 300MB（415,045 docs）+ en：fineweb-edu 头部 300MB（61,842 docs）；各留出 5MB 评测 | **32,000**（specials：`<|endoftext|>`=0 / `<|im_start|>`=1 / `<|im_end|>`=2） | tokenizer.json `05e9ef17eda551bf` · vocab.json `5928cdf631e91e1d` · merges.txt `4189dd83aeadce9c`（全量 `data/tokenizer-32k/SHA256SUMS`） | `data/tokenizer-32k/`（重跑 `tools/train_tokenizer.py` 可再生，~4.5 min；压缩率读数 = `reports/2026-11-18-day2-tokenizer.md`） |

## SFT 数据（Day 4 构建）

| 数据集 | 来源 | 格式 | 指纹 | 落位 |
|---|---|---|---|---|
| minimind sft_t2t_mini（D-10 选项 A 的 SFT 底稿，Day 4 构建 chat 模板） | HF `jingyaogong/minimind_dataset` @ main（hf-mirror），Apache-2.0 | jsonl（t2t 对话，短序列） | `abb1e76b2056e147` | `data/raw/minimind_dataset/sft_t2t_mini.jsonl` |
| minimind dpo（Day 8 任选备用） | 同上 | jsonl | `ee934a8a455ccc99` | `data/raw/minimind_dataset/dpo.jsonl` |

> SFT 构建纪律（PLAN 风险表）：正式 SFT 集须混 20~30% 预训练语料防幻觉加重；Belle 备选未下载，需要时再按本表格式补录。

### SFT 训练集 `data/sft-mix/`（Day 4 构建，`tools/build_sft.py`）

| 件 | 构成 | 规模 | 指纹（sha256 前 16） |
|---|---|---|---|
| `train.bin` + `train.labels.bin` | minimind `sft_t2t_mini` 404,210 条对话（模板 `<\|im_start\|>{role}\n{content}<\|im_end\|>\n`，assistant-only mask）+ **25% 预训练块**（`data/shards` 随机窗口，全 mask） | **250,001,408 token**（244,142 块 × 1024；监督 token 195,371,224 = 78.15%） | `f60b3b5cdba43cfd` / `ca1e50d4e108650e` |
| `val.bin` + `val.labels.bin` | 同分布的文档级留出（`blake2b64(line) % 100 == 0`，4,281 条对话） | 2,001,920 token（监督占比 71.05%） | `8287b49028dd2f58` / `1a5184449637176b` |

> 构建 4.0 min · `block_size` 1024 · 长会话截断 1,012 条（0.11%）· 分段编码 vs 整段编码抽样自检 30 例全过 · 全量 `data/sft-mix/SHA256SUMS`。重建：`.venv-pre/bin/python -I tools/build_sft.py --max-tokens 250e6 --val-tokens 2e6 --pretrain-ratio 0.25`。

## 下载渠道备忘

- HuggingFace：`HF_ENDPOINT=https://hf-mirror.com`（国内受阻预案，PLAN 风险表）
- ModelScope：直连 + 断点续传实测经验（finetune-lab `notes/skills-map.md`：`--max-workers 8` 分片并发、换网口后重启下载进程）；**2026-11-18 实测 `jingyaogong/minimind_dataset` 在 ModelScope 不存在（"record not found"）→ minimind 数据走 hf-mirror，ModelScope 留给 Qwen 系模型**
- **hf CLI 坑（Day 0 实证）**：`hf download <repo> --include "a" "b" "c"` 中 `--include` 只吃第一个 pattern，其余被解析成位置参数文件名并告警 "Ignoring --include"——要么逐个文件用位置参数（`hf download <repo> file.jsonl`），要么 `--include` 传单个 glob（如 `"sample/10BT/*"`）
- minimind 数据文件已改版：`pretrain_hq/sft_512/sft_2043` → `pretrain_t2t(_mini)/sft_t2t(_mini)`，旧名 404，勿按旧文档下单
