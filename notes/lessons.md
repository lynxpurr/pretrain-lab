# lessons — 学习者补课笔记（追加制）

> 惯例：每晚三道概念检验题自答 → 暴露的理解空洞回本件补课；条目**带出处**（当日笔记段 / 证据文件 / 参考实现文件行号）；只追加不覆写，过期靠新条目声明取代。

## 上游知识指针（热身仓沉淀，开工前按需回看——非本仓 lessons，勿混写）

- finetune-lab `notes/lessons.md`：四杠杆×四失败轴地图 v4 · OOD 缺口三层分解 · 预注册判决与校准块机制 · 评测锚点切换目标/守门换位 · 改善分层归因
- `ms-swift-finetune` skill（`~/.agents/skills/`）：SFT 载具操作与坑清单（D-10 选 B 时生效）
- nl2fem `notes/ref-finetune-pipeline.md` / `ref-training-concepts.md`：训练循环与微调管线概念

## 本仓 lessons（按日追加）

<!-- 模板：
## YYYY-MM-DD · Day N · <主题>
- <条目：一句话结论 + 展开两三句 + 出处>
-->

## 2026-11-18 · Day 0~1 · 环境预铺 + 字符级最小闭环

- **查表编码必须假设"输入字符集 ⊄ 表"——编码后值域断言是生死线**（Day 1 最大坑）：字符编码用 `str.translate` 提速（C 级查表），但它对**表外字符原样放行**；val 取自语料头部、含 train 未出现的字符，穿透映射后码点 >65535 被 uint16 截断成垃圾 id（实测 val max = 65025），直到训练端 embedding device-assert 才炸——数据 bug 跑进了训练阶段。修法 = 映射表覆盖 `set(train)|set(val)` + `encode()` 内断言 `ids.max() < vocab_size`。通用化：**值域断言放在编码处（数据侧），不放在训练侧**——数据管线收尾时是 O(秒) 的检查，进训练后是 O(小时) 的排查。出处：tools/prepare_char20m.py 编码段注释；LAB_NOTEBOOK Day 1。
- **device-side assert 异步上报，报错栈位置 ≠ 真凶**：CUDA assert 会在出错后的某个后续 kernel 处抛出（本例栈顶指到 RMSNorm，真凶是 embedding gather 的越界索引）。定位法 = `CUDA_LAUNCH_BLOCKING=1` 同步复跑，栈顶即真凶。出处：两次冒烟 trace 对比（logs/smoke/，CUDA_LAUNCH_BLOCKING 前后）。
- **初始 loss = ln(V) 是免费的复现检查锚**：随机初始化的 LM 起步 loss 应 ≈ ln(vocab_size)（均匀分布的熵）。本仓三次实证：冒烟 bs32 = 9.4297 / bs64 = 9.4316 / 正式 run = 9.4316，对 ln(11765) = 9.3727 同值域。**首步 loss 显著偏离 ln(V) ⇒ 编码/词表/取批必有 bug**——比"训不动才发现"便宜一个数量级。出处：logs/smoke/loss_curve.csv + 正式 run 日志首行（收波快照至 reports/）。
- **hf CLI `--include` 多 pattern 只吃第一个**（Day 0）：`hf download <repo> --include "a" "b" "c"` 从第二个 pattern 起被解析成位置参数文件名（告警 "Ignoring --include"），静默漏下大件。要么逐文件位置参数（`hf download <repo> file.jsonl`），要么 `--include` 传单个 glob。**教训：CLI 告警必须逐条读，"Ignoring/Deprecated" 类告警常伴随静默行为偏差。**出处：data/PROVENANCE.md 下载渠道备忘。
- **数据集现行名以 repo 实时清单为准，旧文档会过期**（Day 0）：minimind 数据文件 pretrain_hq/sft_512 → pretrain_t2t(_mini)/sft_t2t(_mini) 已改版，旧名 404；ModelScope 也无此库（"record not found"）。下单前先 `curl /api/datasets/<id>/tree/main` 核对文件清单，再对照官方仓 README 现行段。出处：data/PROVENANCE.md 下载渠道备忘 · `~/projects/minimind/README.md` L122-423。
