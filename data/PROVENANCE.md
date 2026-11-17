# PROVENANCE — 数据出处与指纹（Day 0 预下载起即记账）

> 纪律（PLAN §6-6，平移自 finetune-lab）：每份数据落位即录来源、许可证、指纹；语料分片 / tokenizer / SFT 数据三表分开记。**指纹不一致 = 数据被动过，先查再训。**

## 预训练语料（Day 2 产出 memmap 分片）

| 数据集 | 来源与版本 | 许可证 | 规模 | 指纹（sha256 前缀） | 落位 |
|---|---|---|---|---|---|
| （待 Day 0 预下载 / Day 2 分片回填） | | | | | |

## Tokenizer（Day 2 产出）

| 件 | 训练语料 | 词表 | 指纹 | 落位 |
|---|---|---|---|---|
| （待回填） | | 32k BPE（D-03） | | |

## SFT 数据（Day 4 构建）

| 数据集 | 来源 | 格式 | 指纹 | 落位 |
|---|---|---|---|---|
| （待回填；D-06：minimind sft / Belle，混 20~30% 预训练语料防幻觉加重） | | | | |

## 下载渠道备忘

- HuggingFace：`HF_ENDPOINT=https://hf-mirror.com`（国内受阻预案，PLAN 风险表）
- ModelScope：直连 + 断点续传实测经验（finetune-lab `notes/skills-map.md`：`--max-workers 8` 分片并发、换网口后重启下载进程）
