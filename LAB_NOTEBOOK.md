# LAB_NOTEBOOK — 逐日记账

> 方案 §七执行建议第 2 条：10 天里会做几十个小决策，不记就忘了。**每天睡前写当日段**；格式 = 决策 / 现象 / 读数 / 疑问 四行起，多了不限。

## 使用方式

- 每日一段（`## Day N · 日期 · 主题`），按日追加，不改旧段（勘误用"补记"）。
- 与 `reports/` 分工：笔记记"为什么这么决策、当时看到什么"，证据文件记"原始读数"；笔记里引用证据路径。
- 与 `notes/lessons.md` 分工：笔记是流水账，lessons 是提炼后的可复用条目（带出处）；每晚三题时顺手把值得沉淀的搬过去。

---

## Day 0 · 2026-11-18 · 环境预铺

- 决策：①窗口拍板 = **Day 1 = 2026-11-19（周四）~ Day 10 = 2026-11-28（周五）**，Day 9 硬缓冲 = 11-27；②D-10 提前拍板 = **A 手写 SFT 为主、B ms-swift 对照/兜底**（PLAN §3 更新完毕）；③`.venv-pre` 按 D-07 用 uv 托管解释器（`uv venv --python=3.12 --seed` → 3.12.13 落 `~/.local/share/uv/python`），装法平移 finetune-lab PLAN §9（cu128 + 阿里云双镜像）；④数据组合按 D-06 = FineWeb-Edu sample-10BT（英文主力）+ minimind pretrain_t2t（中文主力）+ sft_t2t_mini（SFT 底稿）+ dpo（Day 8 备用）。
- 现象：§2 复现检查全绿（GPU 空闲 13998 MiB 与锚点一字不差）；ModelScope 无 `minimind_dataset`（jingyaogong/gongjy 两命名空间均 "record not found"）→ 按 D-06 预案回落 hf-mirror，一次到位；**hf CLI 坑**：`--include` 多 pattern 时第 2 个起被解析成位置文件名（告警 "Ignoring --include"），大件 pretrain_t2t 首次漏下，改显式文件名重下解决（已录 PROVENANCE 下载渠道备忘）；**minimind 数据已改版**：pretrain_hq/sft_512 旧名 404，现行名 = pretrain_t2t(_mini)/sft_t2t(_mini)（对照刚 clone 的 minimind README L122-423 确认）。
- 读数：torch 2.11.0+cu128 · CUDA True · sm_120 在 arch list · bf16 2048² 矩阵过（GPU 空闲 13.4GiB）——证据落 [reports/2026-11-18-day0-env-snapshot.md](reports/2026-11-18-day0-env-snapshot.md)；数据落位 17 件共 ~37.9GB（fineweb-edu 27.85GB 14 分片 + minimind 10.07GB 3 件），SHA256 全量落 `data/raw/SHA256SUMS`、前缀录 `data/PROVENANCE.md`。
- 疑问：①uv 托管解释器为什么免疫系统 python 升级断链？（3.12.13 落 uv 管理目录，venv 不再链 /usr/bin）②50 系为什么必须 cu128？（sm_120 内核只在 CUDA ≥12.8 的 wheel 里编译过）③27.85GB parquet ≈ 多少 token 为什么不能拍脑袋？（压缩率 + tokenizer 未定，Day 2 用自训 32k BPE 实测计数）——今晚三题池，Day 1 晚 `notes/qa-day-1.md` 展开。

<!-- 模板（复制使用）：
## Day N · YYYY-MM-DD · <主题>
- 决策：…（含 D-xx 编号引用）
- 现象：…（报错原文贴 reports/，笔记里写链接）
- 读数：…（吞吐 / loss / 评测分）
- 疑问：…（当晚三道概念检验题的来源池）
-->
