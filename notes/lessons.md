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
- **训练跑批三件套 = 时间预算 + 滚动 checkpoint + tmux 脱离**（Day 1 实测 96 分钟零事故）：①`--max-minutes` 时间兜底让"到点收尾"成为预期路径而非事故（正式跑设 100min > 预估 96min，收尾时仍完整存盘并算终版 val）；②`--ckpt-every 2000` 保证任何中断最多损失 2000 步（≈6 分钟）；③tmux 托管 + `Ctrl+b d` 脱离，让"关闭终端"不等于"杀掉训练"——**这三件是无人值守跑批的最低配置，缺一即把可控实验变成赌博**。补充坑：训练进程运行中重命名其代码目录（本次 src→tools）不会影响已加载的进程，但会破坏任何运行中的相对路径读取（如中途 import/重载）——**改名放到跑批结束后做**。出处：tools/train_char20m.py 参数段 · LAB_NOTEBOOK Day 1。
- **证据三分法：摘要 md + 曲线 csv + 原始 log**（Day 1 起用，30 分钟定稿）：`reports/` 每次 run 落三件——①摘要 md（配置/里程碑表/采样对比/复现命令，人读）；②曲线 csv（每 log/eval 一行，机读可再分析）；③原始 stdout（完整现场，争议时的终审证据）。只交摘要会丢现场，只交 log 则无法快速对账——**三者成本几乎为零（cp 三条命令），却把"事后能否复盘"从运气变成必然**。出处：reports/2026-11-18-day1-char20m.{md,csv,log}。
- **loss 是量化信号，采样是质性信号——两者必须同时看**（Day 1）：val 从 2.04 单调降到 1.56 全程"健康"，但采样才暴露出短 prompt 长续写的模式坍缩（"教堂"复读）——这个缺陷 loss 曲线完全看不见。**跑批时每 1000 步固定 prompt 采样并留在 log 里，收波时对比不同 step 的同一 prompt**，才能同时回答"学得好不好"（loss）与"学成了什么样"（采样）。出处：reports/2026-11-18-day1-char20m.md §3 采样进化链。

## 2026-11-18 · Day 2 · tokenizer + memmap 数据流水线

- **BPE 训练成本按"语料词数"放大，不按字节线性**（Day 2 实测）：600MB 中英混采训 32k merges → 271s、峰值 RSS **~22GB**；HF `train_from_iterator` 先做全量词频统计，内存与"word 单元数"成正比（中文按字切、英文按词切）。小机器上 100~300MB/语言是合理折中。另：`show_progress` 的 tqdm 在 `tee` 管道下不落盘——**日志没进度 ≠ 进程卡死**，先看 CPU/RSS（本次 300~450% CPU、20GB RSS 属正常计算态）。
- **`decode()` 默认 `skip_special_tokens=True`——往返自检必须显式 False**（Day 2 首次跑挂）：探针里混入 `<|endoftext|>` 字面量时，编码被识别成 special id，解码默认把它吞掉，往返断言莫名失败。修法 = 探针拆两段：①普通文本（含 emoji/生僻字/零宽字符）验 byte-level 无损；②specials 单独 `decode(..., skip_special_tokens=False)` 验编号与解码。出处：tools/train_tokenizer.py 自检段。
- **混配比按 token 级缺口调度，不按字节/文档估算**（Day 2）：压缩率随语言/内容变化（同语料 zh 1.84 / en 4.23 chars/token），先估 chars 再换算引入误差；`build_shards.py` 每编码一篇文档就按"目标比例×(总量+1)−已累计"选语言，3B 实际落成 en 60.0% / zh 40.0%（偏差 <0.01%）。val 用 `hash % 500` 做**文档级**划分：随机、可复现、不依赖读取顺序，且与 train 天然不共享文档；预算满后多余候选**丢弃**而非塞回 train——否则"留出集"名存实亡。出处：tools/build_shards.py 注释段 + reports/2026-11-18-day2-shards.md §3。
- **分片大小的决定因素是"指纹/校验/增量重建成本"，不是"能否全进内存"**（Day 2 拍板）：3B token 全量才 6GB，96GB 内存显然装得下，但仍选 1GB/片——单文件 6GB 会让每次校验/重建都要动整块；1GB×6 片 + val 共 7 条 SHA256，`sha256sum -c` 3.5s 全量对账，坏一片只重跑一片。**"内存放得下"回答的是能不能，分片回答的是坏了以后赔多少。**出处：HANDOFF §7 Day 2 决策点③ + reports/2026-11-18-day2-shards.md §2。

## 2026-11-18 · Day 2 盘点校准批 · 跑批观测与 spec 写作

- **长任务轮询先清 stale exit 标记，判活看 PID/CPU/产物增长**（Day 2 实测）：第一次 tokenizer 跑挂在自检上、留下 `logs/day2-tokenizer.exit=EXIT:1`；第二次启动后我直接读到旧标记，误判"又失败了"。另外 `tee` 管道下 tqdm 进度不落盘、日志 mtime 也不动，**"日志没更新"同样不能作为死亡判据**。正确姿势 = 启动前 `rm -f <exit marker>`；判活看 `ps -o pid,etime,%cpu,rss` + 输出文件/目录是否增长。出处：logs/day2-tokenizer-* + LAB_NOTEBOOK Day 2 补记。
- **证据 log 会被 `*.log` 静默吞掉——收波必须 `git add -n` 核对三件套**（Day 2 盘点发现）：Day 1 报告白纸黑字引用 `reports/2026-11-18-day1-char20m-train.log`，但 `.gitignore` 的 `*.log` 让它从未入库——跨机复现时"证据链"直接断。修法 = `.gitignore` 加 `!reports/*.log`；**收波检查从"文件在磁盘上"升级为"文件在 `git add -n` 列表里"**。出处：.gitignore · commit `79ae2fe`。
- **建库前先算"token 库存/需求比"，再拍 token 预算**（Day 2 校准）：用 tokenizer 留出集的 `bytes/token` × 语料磁盘字节数估全库 token——本次 zh ≈1.66B、en ≈6.54B；3B 的 6:4 要 zh 1.2B = **72% 库存**，门②再加 1.5B 就告急。**先算库存/需求比、把"某语言见底"的风险前置**，否则跑到 90% 才发现只能改配比/补数据。出处：reports/2026-11-18-day2-tokenizer.md §3 · PLAN §5 风险表。
- **50M 的 tok/s 不是 140M 的 tok/s——决策门必须写清"在哪个模型上测"**（Day 2 校准，spec 写作教训）：吞吐 ∝ 1/(FLOPs/token)，140M 是 50M 的 2.74×。Day 1 实测有效算力 ~25 TFLOPS → 140M 理论仅 ~30k tok/s；若把 50M 的 35k 当门限放行，3B 实际要 ~64h。**门限要么直接在主模型上测（20~30 步探针仅 1~2 min），要么显式写折算系数**；指标不注明测量对象 = 没定义。出处：PLAN §4.1 · HANDOFF §4 门①口径行。
