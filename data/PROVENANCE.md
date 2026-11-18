# PROVENANCE — 数据出处与指纹（Day 0 预下载起即记账）

> 纪律（PLAN §6-6，平移自 finetune-lab）：每份数据落位即录来源、许可证、指纹；语料分片 / tokenizer / SFT 数据三表分开记。**指纹不一致 = 数据被动过，先查再训。**

## 预训练语料（Day 2 产出 memmap 分片）

| 数据集 | 来源与版本 | 许可证 | 规模 | 指纹（sha256 前缀） | 落位 |
|---|---|---|---|---|---|
| FineWeb-Edu sample-10BT（英文主力） | HF `HuggingFaceFW/fineweb-edu` @ main，经 hf-mirror（2026-11-18 Day 0 下载，14 个 parquet 分片） | ODC-BY v1.0（另受 CommonCrawl ToU 约束） | 27.85GB（≈10B tokens；实测 token 数待 Day 2 自训 tokenizer 计数回填） | 14 片各自前缀见 `data/raw/SHA256SUMS`（首片 `b1ba7b2ce4cb5ea6`，末片 `b393f51fefab26cd`） | `data/raw/fineweb-edu/sample/10BT/` |
| minimind pretrain_t2t（中文主力） | HF `jingyaogong/minimind_dataset` @ main，经 hf-mirror（ModelScope 无此库，回落渠道）；现行文件名对照 minimind 仓 README L122-423 | Apache-2.0 | 8.275GB（中英混合、中文为主；token 数 Day 2 实测回填） | `31efc9a6fa743076` | `data/raw/minimind_dataset/pretrain_t2t.jsonl` |

> 原始下载层全量指纹 = `data/raw/SHA256SUMS`（17 条，Day 0 记账）；Day 2 产出的 memmap 分片 / tokenizer 指纹另起文件录入（PLAN §6-6）。

## Tokenizer（Day 2 产出）

| 件 | 训练语料 | 词表 | 指纹 | 落位 |
|---|---|---|---|---|
| （待回填） | | 32k BPE（D-03） | | |

## SFT 数据（Day 4 构建）

| 数据集 | 来源 | 格式 | 指纹 | 落位 |
|---|---|---|---|---|
| minimind sft_t2t_mini（D-10 选项 A 的 SFT 底稿，Day 4 构建 chat 模板） | HF `jingyaogong/minimind_dataset` @ main（hf-mirror），Apache-2.0 | jsonl（t2t 对话，短序列） | `abb1e76b2056e147` | `data/raw/minimind_dataset/sft_t2t_mini.jsonl` |
| minimind dpo（Day 8 任选备用） | 同上 | jsonl | `ee934a8a455ccc99` | `data/raw/minimind_dataset/dpo.jsonl` |

> SFT 构建纪律（PLAN 风险表）：正式 SFT 集须混 20~30% 预训练语料防幻觉加重；Belle 备选未下载，需要时再按本表格式补录。

## 下载渠道备忘

- HuggingFace：`HF_ENDPOINT=https://hf-mirror.com`（国内受阻预案，PLAN 风险表）
- ModelScope：直连 + 断点续传实测经验（finetune-lab `notes/skills-map.md`：`--max-workers 8` 分片并发、换网口后重启下载进程）；**2026-11-18 实测 `jingyaogong/minimind_dataset` 在 ModelScope 不存在（"record not found"）→ minimind 数据走 hf-mirror，ModelScope 留给 Qwen 系模型**
- **hf CLI 坑（Day 0 实证）**：`hf download <repo> --include "a" "b" "c"` 中 `--include` 只吃第一个 pattern，其余被解析成位置参数文件名并告警 "Ignoring --include"——要么逐个文件用位置参数（`hf download <repo> file.jsonl`），要么 `--include` 传单个 glob（如 `"sample/10BT/*"`）
- minimind 数据文件已改版：`pretrain_hq/sft_512/sft_2043` → `pretrain_t2t(_mini)/sft_t2t(_mini)`，旧名 404，勿按旧文档下单
