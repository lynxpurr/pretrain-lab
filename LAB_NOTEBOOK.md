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
- 补记（同日晨）：用户改判"现在开工"→ 窗口整体前移一日（Day 1 = 11-18 ~ Day 10 = 11-27，缓冲 11-26），本段"决策①"的 11-19 起算作废，以 HANDOFF §1 为准。

## Day 1 · 2026-11-18 · 手写 model.py + 字符级 20M 最小闭环（提前起跑日）

- 决策：①晨间用户改判"现在开工"，窗口整体前移：**Day 1 = 11-18 ~ Day 10 = 11-27，Day 9 缓冲 = 11-26**；②脚本目录 = `tools/`（对齐 README 预注册文档地图，从 `src/` 改名）；③Day 1 架构定型即 Day 4 主模型同款（D-02：RoPE+RMSNorm+SwiGLU+tied），字符级只换 GPTConfig——"同一实现、两套配置"保证阶梯锚定的可比性；④词表用字符级 11,765（非 32k），Day 2 换 BPE 32k 时只改 vocab_size，模型代码零改动（换轨检查项）；⑤训练量 33000 步 ≈ 10.8 亿字符（3.6 epoch），warmup 200 / lr 2e-3 cosine 至 10%。
- 现象：**最大的坑 = `str.translate` 表外字符穿透**：val 取自语料头部，含 train 未出现的字符（如生僻字/符号），translate 对表外字符原样放行 → 码点 >65535 被 uint16 截断成垃圾 id（val max 实测 65025），一路活到训练端 `torch.embedding` 才 device-assert；且 assert 异步上报，栈顶指到 RMSNorm，真凶在 embedding gather——`CUDA_LAUNCH_BLOCKING=1` 同步复跑才定位。修法 = 映射表覆盖 `set(train)|set(val)` + `encode()` 内断言 `ids.max() < vocab_size`（值域断言放数据侧，O(秒) 的检查不拖到 O(小时) 的排查）。次要坑：`mkdir` 缺 `parents=True`；log 均值分母跨窗口累积。
- 读数：参数量 **22,220,544**；首步 loss **9.4316** vs ln(11765)=**9.3727**（锚定复现，三次同值）；val 2.0414(2.5k) → 1.7890(12.5k) → 1.6865(20k) → **1.5599(33k 终版)**；train 全程跟随（终版 ~1.57）无过拟合；吞吐 **187,480 字符/秒**（5.7 it/s @ bs64×512，全程稳定）；总用时 **96.1 min**，GPU 56~57°C / 98~100% util，峰值显存 ~15GB（含 laya-triage 1.8G 常驻）。采样：step 60 字符汤 → step 3k 通顺 → step 12k 术语正确 → step 33k 结构化段落 + 写诗押韵（"绿水长流入眼前，鱼跃天涯共此时"）；"从前有一座山" 长续写仍模式坍缩（temperature 0.8 下正常，Day 3 加 top-p/重复惩罚观察）。证据 = [reports/2026-11-18-day1-char20m.md](reports/2026-11-18-day1-char20m.md)（含 csv + log 原始件）。
- 疑问：①22.2M 参数是怎么从 d=384/L=10/词表 11765 算出来的（tied 为什么省 4.5M）？②10.8 亿字符只换到 val 1.56，继续加数据/加步数的边际收益在哪看？③"从前有一座山"坍缩成"教堂"复读——为什么 prompt 越短越容易坍缩，top-p/温度/重复惩罚各自怎么作用？——已并入 [notes/qa-day-1.md](notes/qa-day-1.md) 题目池（另三题来自 Day 0 疑问池）。

<!-- 模板（复制使用）：
## Day N · YYYY-MM-DD · <主题>
- 决策：…（含 D-xx 编号引用）
- 现象：…（报错原文贴 reports/，笔记里写链接）
- 读数：…（吞吐 / loss / 评测分）
- 疑问：…（当晚三道概念检验题的来源池）
-->
