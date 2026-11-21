# pretrain-lab — 小模型从零训练 10 天行动（PLAN）

> **过程记录（非读者入口）**：本文件是项目计划与决策记录，保留当时的本地路径与内部引用。公开读者请从 [README.md](README.md) / [docs/](docs/) 进入；发布状态见 [docs/internal/README.md](docs/internal/README.md)。
>
> 建立：2026-11-18 · 一句话：在本地 5070 Ti 16GB 上，用 10 天完整经历一个 **~140M 小模型从零预训练 → SFT → LoRA 对比 → 部署 demo** 的全生命周期，产出"完整经验 + 亲手训的模型 + 可对外讲述的报告与 demo"。**学习导向**。
> 底稿：NoteFlow `WorkingDeck/2026-09/2026-09-22/small-llm-10day-plan.md`（2026-09-22 定稿，原文标注"可作为项目执行的唯一参考底稿"）；本件是其立项落位版——原文逐日方案与风险表照搬为 §4/§5，原文 §四决策项升格为 D-01~D-08。
> 热身谱系：**nl2fem**（数据/评测/训练循环热身，收官 2026-09-27）+ **finetune-lab**（ms-swift 微调载具热身，收官 2026-09-27）——本仓是两仓共同的"下一主线"（nl2fem charter §3：微调买不到吞吐调优、训练不稳定排查、数据配比、tokenizer 设计，那些只在从零预训练里出现）。

## 1. 任务一句话

借助 coding agent，10 天假期内从零手写并训练一个 ~140M 中英双语小模型（预训练 + SFT + LoRA 对比），部署为本地可对话 demo，并完成训练报告。

## 2. 目标与成功标准（Day 10 结束时应达成）

| 门 | 内容 | 判据 |
|---|---|---|
| G1 | 从零训练最小闭环跑通 | Day 3 冒烟：手写训练循环跑通 + 50M 配置实测吞吐 + **决策门①判定落档** |
| G2 | 140M 底座训练完成 | 完整 loss 曲线 + checkpoint 谱系（每 1000 步存档） |
| G3 | SFT + LoRA 对比完成 | 全参 SFT v2 与 LoRA 版同底座对比读数（效果/显存/速度） |
| G4 | 可 demo 的本地聊天模型 | GGUF 量化 → Ollama → Gradio 页，能对话 |
| G5 | 评测框架 + 最终对比 | held-out 困惑度 + 自设计测试集；底座 vs SFT vs LoRA 三版对比 |
| G6 | 训练报告 + repo 整理 | loss 曲线、数据决策记录、评测对比、成本核算；README + 模型卡 + 复现步骤 |

**进度对照（2026-11-19 Day 7 盘点）**：

| 门 | 状态 | 依据 / 缺口 |
|---|---|---|
| G1 最小闭环 + 决策门① | **✅ 完成（Day 3）** | `tools/train.py` 框架（多分片/累积/续训/固定 val/采样）+ 50M 冒烟 + 50M 30min 预注册吞吐 + 140M 探针；**门① PASS = 140M 52,250 tok/s ≥ 35k**。证据 [reports/2026-11-18-day3-framework.md](reports/2026-11-18-day3-framework.md) · [50m-30min](reports/2026-11-18-day3-50m-30min.md) · [140m-probe](reports/2026-11-18-day3-140m-probe.md) |
| G2 140M 底座 | **✅ 完成（Day 4~5）** | 3B token / 16h07m41s / 52,171 tok/s / **val 2.7709** / 46 ckpt 谱系 ≈73GB；终版事实采样已对。证据 [reports/2026-11-19-day4-main140m.md](reports/2026-11-19-day4-main140m.md) |
| G3 SFT + LoRA | **✅ 完成（Day 7~8 + 机动窗口 + 最终阶段）** | **部署 v2e（2026-11-20 起）：val 1.6065 / rep-4 0.055（全系最低）/ 题库 17/18（2 题残留；干净子集 15/16）/ rubric 6/8 / math 8-42（字面；holdout 不成立）/ PPL +5.5%**；v2（原部署，含记忆）、v2b（全量数学豁免）、v2c（选择性保护）、v2d（复读压制，rep-4 0.084 差 0.004 不部署）为过程消融；**LoRA r=8 1.20% 可训练 / peak 9.74GB（-2.3GB）/ ckpt 526MB + adapter 6.5MB / val 1.8253 / rep-4 0.260（1 epoch 欠拟合，不部署）+ r=12 1.79% 容量对照（REPORT §6）**；同题对比见 [REPORT.md](REPORT.md) §4.7 八版终表 |
| G4 本地 demo | **✅ 完成（Day 7 + 最终阶段升级）** | GGUF F16 326MB / **Q8_0 173MB（部署默认）** / Q4_K_M 103MB；Ollama 用户级 11435 可对话；`tools/app_stdlib.py` 本地页 **7860**（Gradio 镜像卡死，stdlib 替代）；F16 与 PyTorch 逐字对拍 5/5 = 链路忠实；**Q4_K_M 在 v2e 上不保真**（math 42→72 / translate 回退）→ 量化保真度抽检入验收红线 |
| G5 评测框架 + 对比 | **✅ 八版对比 + holdout（Day 8 + 机动窗口 + Day 10）** | base / v1 / v2 / v2b / LoRA / v2c / v2d / v2e 同 val 同 18 题同 greedy；关键词 + rubric + distinct-2/rep-4；**v2e = rep-4 0.055 + 题库 17/18（2 题残留）**；v2~v2d 读数含记忆成分（已在八版终表标注）。**Day 10 holdout（30 题未见题，双向去重 0 撞车）：v2e 与 v2 人工复核同为 23/30，dev 排名不复现；`13×5` 全错、translate 只认精确句式、calibration 稳定泛化 → REPORT §5.2**。证据 [reports/2026-11-20-v2e-eval.md](reports/2026-11-20-v2e-eval.md) · [holdout-audit](reports/2026-11-20-holdout-audit.md) |
| G6 报告 + repo 整理 | **✅ 完成（Day 10，2026-11-20 提前）** | **[REPORT.md](REPORT.md) 定稿**（§5.1 评测污染章 + §4.7 八版终表 + §10 复现走查）+ `MODEL_CARD.md` v2e 口径 + 54 份 md / 152 链接 0 断链 + 证据三分核对 + v2e build bit-for-bit 复现（4/4 sha256）——[reports/2026-11-20-day10-repro-check.md](reports/2026-11-20-day10-repro-check.md) |

预期管理（底稿 §一原文）：30 亿 token 训出的 140M ≈ GPT-2 124M 水平（中英文通顺、能简单对话、知识贫乏）——**不是** Qwen3-0.6B（36 万亿 token，本方案的 1 万倍）。项目产出是经验、模型、报告与 demo，非对标开源质量。

## 3. 决策记录（追加制；D-01~D-08 源 = 底稿 §四，2026-11-18 立项落位）

| 编号 | 决策 | 理由 | 何时重开 |
|---|---|---|---|
| D-01 | 主目标模型 **~140M**：d_model=768、16 层、12 头（**Day 2 盘点核准：137,847,552 参数**，vocab 32k / tied） | 比 50M 有说服力；比 350M 稳（40h 训练窗口一旦出事没有重跑余量） | 决策门①触发缩配（→100M/20 亿） |
| D-02 | 架构 decoder-only：RoPE + RMSNorm + SwiGLU + 词嵌入共享（tied embeddings） | 现代小模型标准配置 | — |
| D-03 | 词表 32k，中英双语 BPE | 兼顾压缩率与参数量 | tokenizer 消融（Day 8 任选） |
| D-04 | 训练量 ~30 亿 token（= **21.8×** 137.85M 参数，Chinchilla 20× 附近） | 12~25h 可承受（35k 含预留 ~25h；40k ~21h；**Day 3 实测 52.25k → 单程 15.9h**，见 §4.1） | 决策门②加训 15 亿（吃 Day 9 缓冲；zh 供给预案见 §5） |
| D-05 | 序列长度 1024（RoPE 支持外推） | 该规模注意力开销占比小 | — |
| D-06 | 数据：英文 FineWeb-Edu sample 子集；中文 SkyPile 抽样或 minimind pretrain_hq（已清洗，省一天苦工）；SFT = minimind sft / Belle | 质量 > 数量；下载走 `HF_ENDPOINT=https://hf-mirror.com` 或 ModelScope | 数据返工（Day 9 缓冲） |
| D-07 | 预训练栈：PyTorch 2.7+（**cu128，50 系硬性要求**）+ HF tokenizers + tensorboard/W&B + tmux；venv 用 **uv 托管解释器**（`.venv-pre`） | 前半 = 底稿 §四；后半 = 2026-11-18 新教训（nl2fem 双 venv 因系统 python 升级断链——venv 不链 `/usr/bin/python*`，uv 托管 3.x 免疫） | — |
| D-08 | 参考实现：**minimind**（中文全流程、与目标几乎一致）+ **nanoGPT**（必读）；晚间可看 Karpathy 视频 | 站在巨人肩上 | — |
| D-09 | **全本地执行**（.118 训练机：RTX 5070 Ti 16GB / 96GB RAM / 2TB SSD） | 底稿 §一结论：本地可完全完成，成本仅电费（~¥4~5/天）；50 系环境坑全部压到 Day 0 解决。云端备选调研在 nl2fem `research/2026-09-25-online-finetune-platforms.md` §5/§6，仅当本地栈硬性失败且不可修时启用 | 本地栈硬性失败且不可修 |
| D-10 | **SFT 载具已拍板（2026-11-18 Day 0 提前拍定）**：**A = 手写 SFT 循环为主**（与自研预训练栈同源，符合"脱稿复述完整训练循环"的立项初衷）；B = ms-swift 作对照/兜底（热身已验证，`ms-swift-finetune` skill 直接生效） | 底稿 §四 Agent 用法条："10 天后能脱稿复述整个训练循环，才算完整经历" | SFT 实测受阻 → 切 B 兜底 |

## 4. 逐日方案（底稿 §五原文照搬，微调：载具名对齐本仓）

| 天 | 主题 | 具体内容与产出 |
|---|---|---|
| **0（假期前一晚）** | 环境预铺 | 驱动/CUDA 12.8+/PyTorch cu128 验证（`torch.cuda.is_available()` + 小矩阵运算）、tmux、数据集提前下载（`HF_ENDPOINT=https://hf-mirror.com`）、clone minimind + nanoGPT。**这步不做，第一天必废** |
| **1** | 手写模型 + 最小闭环 | 上午：agent 陪写从零 `model.py`（全套现代组件）；下午：字符级 20M 小模型在小语料上训 1~2 小时，亲眼看 loss 下降、生成样本。产出：跑通的模型代码 |
| **2** | Tokenizer + 数据流水线 | 上午：训练 32k 中英 BPE tokenizer，理解压缩率；下午：下载清洗语料、去重、分词、打包成 memmap 分片（96GB 内存优势兑现）。产出：30~50 亿 token 训练集 |
| **3** | 训练框架 + 冒烟测试 | 完整训练循环（warmup+cosine、grad clip、bf16、checkpoint 续训、采样监控）；50M 配置跑 30 分钟测吞吐 + 140M 探针。**决策门①：实测 ≥3.5 万 token/s（口径 = 140M 等效，见 §4.1）→ 明天全量启动；否则缩到 100M / 20 亿 token** |
| **4** | 启动主训练 + SFT 准备 | 早上启动 140M 全量训练（预计当晚~次日中午完成），挂 tmux 后台；白天构建 SFT 数据集（chat 模板）+ 写 SFT 脚本。产出：训练中的模型 + SFT 就绪 |
| **5** | 中期 SFT + 评测框架 | 取中间 checkpoint 做一次全参 SFT，观察指令跟随雏形；搭建评测：held-out 困惑度 + 自设计小测试集（定义评测维度和评分标准——PM 强项） |
| **6** | 主训练收官 + SFT v2 | 分析完整 loss 曲线、对比各 checkpoint 生成质量；对最终底座做正式 SFT v2（融入第 5 天发现的数据问题）。**决策门②：loss 仍在陡降且质量差 → 加训 15 亿 token（吃掉第 9 天缓冲）** |
| **7** | LoRA 对比 + 部署 | 上午：同一底座用 LoRA 做 SFT，与全参对比效果/显存/速度；下午：转 GGUF 量化 → 导入 Ollama → Gradio 聊天页。产出：**能 demo 的本地聊天模型** |
| **8** | 深化理解（任选） | 学习率/warmup 扫参建立直觉 / tokenizer 消融 / DPO 偏好对齐（minimind 有现成管线）；晚间开始写训练报告（loss 曲线、数据决策、成本核算——发知乎/博客素材） |
| **9** | 缓冲日 | 专为事故预留：训练发散重跑、数据返工、环境问题。没出事则自由发挥（加数据、调 SFT 轮数、完善 demo） |
| **10** | 收尾 | 最终评测对比（底座 vs SFT vs LoRA）、repo 整理（README + 模型卡 + 复现步骤）、写总结、规划下一步（1B 需要什么、多卡怎么做） |

**预算与裁法**：10 天整块窗口 + Day 9 硬缓冲；进度超期 → Day 7~8 可整体砍（G3/G4 部分降级），G1/G2/G5 不裁（底线 = 从零预训练闭环 + 评测对比 + 报告）。

### 4.1 关键路径与门①口径校准（2026-11-18 Day 2 盘点批，**跑前**校准）

**模型配置候选**（`tools/model.py` 实测，vocab 32,000 / tied / seq 1024）：

| 用途 | d | L | H | 参数量 | non-emb | 备注 |
|---|---|---|---|---|---|---|
| **50M 冒烟（推荐）** | 576 | 8 | 9 | **50,292,288** | 31,860,288 | head_dim 64；名义 50M，d/L=72（比 140M 的 48 更宽浅，仅作管线/吞吐对照） |
| 50M 备选 | 512 | 10 | 8 | 48,507,392 | 32,123,392 | d/L=51.2，最接近 140M 的 48；OOM/对照用 |
| 100M 缩配（门①兜底） | 640 | 16 | 10 | 99,799,680 | 79,319,680 | 2B token |
| **140M 主模型** | 768 | 16 | 12 | **137,847,552** | 113,271,552 | D-01 |

**吞吐→单程时长**（按 6N FLOPs/token；3B 含 eval/ckpt 预留 +5~10%）：

| 140M 实测 tok/s | 3B 单程 | 2B 单程（100M 缩配） | 判定 |
|---|---|---|---|
| 35k | ~23.8h（+预留 ~25h） | ~15.9h（+预留 ~16.7h） | 门①下限 |
| 40k | ~20.8h | ~13.9h | 推荐区间 |
| 50k | ~16.7h | ~11.1h | 宽裕 |

**门①口径（原文"实测 ≥3.5 万 token/s"未指明模型，校准为 140M 等效）**：

- 预注册动作保留：50M 配置跑 30 min 测吞吐（同时验证管线/显存/稳定性）。
- **加一步 140M 探针**：同框架、正式 bs/T 跑 20~30 步（约 1~2 min），直接读 140M tok/s，不靠外推。
- **判定 = 140M 探针 ≥ 35k tok/s**；50M 读数按 FLOPs 比 2.74× 交叉校验（50M 需 ≥96k 才等价 35k）。
- 理由：若把 50M 的 35k 当门限，140M 实际可能仅 ~13k tok/s（3B 要 64h），与"明天全量启动"的意图直接矛盾。140M 探针成本 1~2 min，是最便宜的真值。

**门①实测回填（2026-11-18 Day 3，预注册后执行，口径未改）**：

| 动作 | 配置 | 实测 | 判定 |
|---|---|---|---|
| 50M 30min 预注册 | d576/L8/H9 · bs16×accum4 · T1024 | **120,517 tok/s**（215.7M token / 30m01s，峰值 10.72GB） | ✅ 折算 44.0k ≥ 96k 门限 ✓ |
| 140M 探针 | d768/L16/H12 · bs8×accum8 · T1024 | **52,250 tok/s**（40 步，峰值 10.51GB） | ✅ **门① PASS（超 49%）** |
| micro-bs 变体 | bs10 / bs16+grad-ckpt | 51,230 / 40,449 tok/s | 选 bs8（最快且余量最大） |

**判定结果：PASS → 按 D-01 启动 140M / 3B（100M/2B 兜底不启用）**；3B 单程 15.9h（+开销 ~16.0h），45,777 步 @ 1.25s/步，ckpt 46 件 ≈76GB。证据 [reports/2026-11-18-day3-140m-probe.md](reports/2026-11-18-day3-140m-probe.md)。

**门②口径（Day 5 用中期曲线定标，Day 6 判定前不改）**："loss 仍陡降"是定性表述，需在 Day 5 拿到中期 val 曲线后量化阈值（候选：**最后 10% 步数 val 降幅 >0.02~0.03 且采样质量明显不足**）；同时受 zh 供给约束（见 §5），加训方案须先定配比再启动。

**门② 判定结果（2026-11-19 Day 6 落档，口径未改）**：**不触发 → 不加训 15 亿**。

| 证据 | 读数 | 阈值 | 结论 |
|---|---|---|---|
| 预注册量：最后 10% 步（41,500→45,777）val 降幅 | **0.0134**（2.7843→2.7709） | >0.02~0.03 | 未触发 |
| 混杂诊断：恒定 lr 6e-5 探针 300 步（从 `ckpt-0041000`） | **0.0051**（2.7869→2.7818，逐段衰减 0.0024→0.0014→0.0013；重置 Adam 动量 → 乐观上界） | >0.01 视为仍有显著余量 | 未触发 |
| 门② 第二条件（采样质量明显不足） | 终版事实采样已对（北京 / Paris）；SFT 后题库 89% | 明显不足 | 不成立 |

成本账：加 1.5B ≈ 8.0h GPU，换 ≤0.01~0.02 val（且 zh 供给已用 72%），并挤占 G3/G4/G6。
重开条件（三条，任一成立才重新考虑）：①SFT v2 后题库 <70% 且归因"底座语言能力不足"；②系统性事实错误率 >50% 且与 token 量强相关；③Day 8/9 缓冲兑现后仍有 ≥8h，作为对照实验而非救火。
证据：[reports/2026-11-19-day6-gate2.md](reports/2026-11-19-day6-gate2.md) · 分析：[reports/2026-11-19-day6-decode.md](reports/2026-11-19-day6-decode.md)

**检查点/磁盘预算**：140M ckpt ≈1.65GB（fp32 权重 + Adam 态）；bs64×1024 → 45.8k 步，每 1000 步存 46 个 ≈76GB；bs32 → 92 个 ≈152GB。磁盘余 2.3TB 充足，但 Day 3 定 bs 时把 ckpt 体积写进配置（G2 要求每 1000 步谱系）。

**关键路径与缓冲**：

- 关键路径 = Day 3 框架 + 门① ✅（11-18 完成）→ Day 4 140M 启动 → 次日收官（实测 15.9h）→ Day 5/6 SFT v2 + 门② → Day 7 部署 → Day 10 报告。
- 缓冲 = **11-19 / 11-20 两天**（Day 2/3 均于 11-18 提前完成置换）+ Day 9（11-26）硬缓冲。主训练须在 Day 6 中午前完成，否则砍 Day 7/8 深化项。
- 门②（Day 6）若触发加训 1.5B：zh 供给不足（见 §5 风险表），优先 en-heavy 扩展或 Day 6 下载 SkyPile，Day 9 兜底。

## 5. 风险与预案（底稿 §六 + 2026-11-18 新增一条）

| 风险 | 概率 | 预案 |
|---|---|---|
| 50 系环境坑（`no kernel image is available` 等，源于 CUDA <12.8 或旧版 PyTorch/flash-attn/bitsandbytes） | 高 | 全部压到 Day 0 解决；报错直接贴给 agent。**栈差经验现成**：finetune-lab PLAN §9（cu128/sm_120 已验证）+ 阿里云双镜像 + `UV_TORCH_BACKEND=cu128` 缺一不可 |
| **venv 解释器断链**（系统 python 升级致 `/usr/bin/pythonX.Y` 消失——2026-11-18 在 nl2fem 双 venv 实证） | 中 | D-07：venv 一律 uv 托管解释器（`uv venv --python=3.x` 落 `~/.local/share/uv/python`），venv 内 `python` 永不指向 `/usr/bin`；HANDOFF 复现检查含 venv 断链项 |
| 吞吐低于预期 | 中 | Day 3 决策门①按 **140M 探针**判定（见 §4.1）：缩模型或缩 token 量，不硬扛 |
| **zh 语料供给不足（门②加训 1.5B）** | 中 | Day 2 实测 pretrain_t2t ≈1.66B token，3B 已用掉 1.2B（~72%）。若门②加训 1.5B：优先 en-heavy 扩展（如 en:zh=8:2，zh 再耗 ~0.3B）+ 或 Day 6 立即下载 SkyPile 抽样补 zh（下载+tokenize ~2h，Day 9 兜底）；不建议单纯重复 zh 语料超 1 epoch |
| 训练中 loss 尖峰/发散 | 中 | 每 1000 步存档 + 梯度裁剪 + 降学习率从最近 checkpoint 重启 |
| SFT 后小模型幻觉加重 | 高（正常现象） | SFT 数据混 20~30% 预训练语料；限制 epoch 数 |
| 进度超期 | 中 | Day 7~8 可整体砍；Day 9 是硬缓冲 |
| 国内下载 HuggingFace 数据受阻 | 中 | `HF_ENDPOINT=https://hf-mirror.com` 或改用 ModelScope（ModelScope 直连+断点续传实测经验在 finetune-lab `notes/skills-map.md`） |
| mini 主机长时间高负载过热降频 | 低 | 训练前调激进风扇曲线，保持风道清洁，长期 80°C+ 会拖慢训练 |

## 6. 纪律（延续热身仓惯例，轻量版）

1. **证据只增不改**：`reports/` 落训练日志快照、评测读数、决策门判定；改错走勘误追加，不覆写。
2. **锚定先行**：新脚本先在小配置复现已知答案（字符级 20M → 50M → 140M 阶梯，类比 finetune-lab A 波 run1 复现）。
3. **逐日记账**：`LAB_NOTEBOOK.md` 每天记决策与现象——10 天几十个小决策，不记就忘。
4. **每晚三道概念检验题**（学习者模式）：自答为主，答案卡落 `notes/qa-day-N.md`；理解空洞回 `notes/lessons.md` 补课（追加制、带出处）。
5. **git 惯例**：develop 主干直提为主（提交信息带 `day-N` 标签）；大改动（训练框架重构等）用 `feature/day-N-<slug>` → `--no-ff` 合入；模型/checkpoint/语料 gitignore（纪律见 .gitignore）。
6. **数据指纹**：`data/PROVENANCE.md` + SHA256SUMS 从 Day 2（数据流水线）起立——语料分片、tokenizer、SFT 数据全部录指纹（finetune-lab 最值钱的惯例平移）。**补记（2026-11-18 Day 0~1 实测）**：纪律实为"每份数据落位即录"——raw 层 17 件（37.9GB）Day 0 已录 `data/raw/SHA256SUMS`，Day 1 字符级切片已录 `data/day1-char20m/SHA256SUMS`；Day 2 起续录分片/tokenizer/SFT。

## 7. 边界（与热身仓的关系）

- **finetune-lab / nl2fem = 知识上游，非资产上游**：本仓的模型、数据、代码全部自建，与 nl2fem 的 FEM 数据/评测件/求解器无交集（原则上不借用；若确需借用沿用 finetune-lab D-02 只读纪律）。
- **知识回填方向**：本仓产出（预训练吞吐体感、tokenizer 经验、训练稳定性排查）反向充实 finetune-lab `notes/lessons.md` 地图缺失的"从零预训练"列——回填经本仓 lessons 记录即可，不改热身仓档案。
- **素材索引（按 Day 取用，源 = finetune-lab PLAN §8 + 两仓 HANDOFF）**：
  - Day 0：cu128/sm_120 栈验证记录 + 镜像策略（finetune-lab PLAN §9）· ModelScope 下载实测（finetune-lab `notes/skills-map.md` 待办节）
  - Day 4~6（若 D-10 选 B）：`ms-swift-finetune` skill（`~/.agents/skills/`，版本戳 4.5.3）· swift 工具谱系（finetune-lab `tools/`）
  - Day 5 评测：预注册判决 · 双守纪律 · 锚点切换目标/守门换位 · 拆轴子读数（finetune-lab `notes/lessons.md` LAB-H 批）
  - Day 7 QLoRA：全容量档显存账（finetune-lab HANDOFF §4 锚点表）
  - Day 8 DPO：剂量学（3 步开关/β 不敏感）· 负例生成器选型（finetune-lab `notes/lessons.md` G/H 批 + `tools/{check,build}_dpo_g4.py`）

## 8. 环境快照（Day 0 回填）

- 机器：.118 · RTX 5070 Ti 16GB（Blackwell, sm_120）· AMD Ryzen Pro 9 · 96GB RAM · 2TB SSD；开发机 = Windows 笔记本（8845HS，无 CUDA，WSL2 建议）
- GPU 现状（2026-11-18 实测）：空闲 13998 MiB；常驻 laya-triage（1820 MiB）在位，tei-embed/tei-rerank 不在位——预训练无需清空常驻（显存余量足），14B 级实验才需按 runbook 清空
- `.venv-pre`：✅ 2026-11-18 建立（D-07：uv 托管 CPython 3.12.13，`~/.local/share/uv/python`，不链 /usr/bin）· torch 2.11.0+cu128 · transformers 5.23.0 · tokenizers 0.23.3 · datasets 5.2.0 · tensorboard/wandb/matplotlib/numpy 在位；验证 = CUDA True + sm_120 在 arch list + bf16 矩阵过（证据 = [reports/2026-11-18-day0-env-snapshot.md](reports/2026-11-18-day0-env-snapshot.md)，装法平移 nl2fem runbook §3 / finetune-lab PLAN §9）
- 参考实现：✅ minimind @ `233d00f`、nanoGPT @ `3adf61e`，落 `~/projects/`（D-08；注意 minimind 数据文件现行名 = `pretrain_t2t(_mini)/sft_t2t(_mini)`，旧名 pretrain_hq/sft_512 已弃）
- 数据集：✅ Day 0 预下载落位（D-06）：FineWeb-Edu sample-10BT 27.85GB（英，ODC-BY）+ minimind pretrain_t2t 8.275GB（中，Apache-2.0）+ sft_t2t_mini 1.739GB + dpo 0.054GB；**ModelScope 无 minimind_dataset（"record not found"）→ 回落 hf-mirror 渠道**；指纹 = `data/raw/SHA256SUMS`（17 条）+ `data/PROVENANCE.md` 前缀表；**Day 2 已用自训 32k tokenizer 实测回填：fineweb ≈6.5B token（4.259 bytes/token）· pretrain_t2t ≈1.66B token（4.974 bytes/token）**
- 训练运行基线（2026-11-18 Day 1 实测）：22.2M 字符级模型 @ bs64×512 → **187,480 字符/秒** · GPU 占用峰值 ~15GB（含常驻 1.8G）· 温度 56~57°C @ 98-100% util（无降频）· 96.1 min 单程无中断。**主模型外推（Day 2 校准）：Day 1 有效算力 ≈25 TFLOPS（22.2M×6×187k tok/s）；140M 每 token ≈0.83 GFLOPs → 同 MFU 仅 ~30k tok/s，门① 35k 需 MFU 再高 ~17%。结论：50M 读数必须按 FLOPs 比 2.74× 折算，或直接跑 140M 探针——不能拿 50M 的 35k 当 140M 的 35k（口径见 §4.1）。**
- 数据流水线基线（2026-11-18 Day 2 实测）：tokenizer 32k BPE（zh 1.841 / en 4.226 chars/token 留出）· 训练集 3,000,000,000 token（en 60.0%/zh 40.0%，6×1GB 片 + val 4M，uint16 max_id 31999）· 单进程构建吞吐 **2.42M token/s**（20.7 min）· BPE 换轨冒烟首步 **10.4542** ≈ ln(32000)=10.3735（+0.081）· 29.99M 冒烟 @ bs32×512 ~148k tok/s（非基准）
- **训练框架基线（2026-11-18 Day 3 实测，`tools/train.py`）**：50M（d576/L8/H9）@ **bs16×accum4×T1024 = 65,536 tok/step → 120,517 tok/s**（6N 口径 36.4 TFLOPS，30min/215.7M token，val 3.6377）· 140M（d768/L16/H12）@ **bs8×accum8 → 52,250 tok/s**（43.2 TFLOPS，3B 单程 15.9h）· 峰值显存 10.72 / 10.51 GB（含常驻 1.78G）· GPU 58°C / 98% util / 2797 MHz · eval+sample+ckpt 开销 0.6% · **micro-bs 边界：50M=16、140M=8**（50M bs24 OOM；140M bs10 需 `expandable_segments`、bs12 OOM；140M bs16+grad-ckpt 仅 40,449 tok/s）· **torch.compile 4,077 tok/s（慢 13×，弃用）** · 续训 kill→restore val 一字不差（7.6893）
- **主训练基线（2026-11-19 Day 4~5 实测）**：140M × **3,000,041,472 token** / **16h07m41s** / **52,171 tok/s** / **val 2.7709**（train 2.677，gap 0.094）· 开销 0.96% · 0 尖峰（2,289 窗口）· 46 ckpt ≈73GB · 末段每 500 步降幅 −0.0009
- **SFT/评测基线（2026-11-19 Day 5~6 实测，`tools/sft.py` + `tools/eval.py`）**：SFT v1（250M token / 1 epoch / lr 1e-4）**1h19m26s / 3,815 步 / 53,004 tok/s / SFT val 1.5515**；base → sft：预训练 PPL **15.350→16.307**（遗忘 +6.2%）· SFT PPL **9.818→4.596** · 题库 **6/18→16/18（89%，规则判分）**；解码对照 rep-4：greedy 0.131 / 采样 0.123 / rp1.2 0.057 / rp1.3 0.032（题库 16/15/15/13）——**复读为数据侧问题，解码不是主因**
- **SFT v2/v2b + LoRA + 部署基线（2026-11-19 Day 7 实测，`tools/build_sft_v2.py` + `tools/lora.py` + `tools/export_gguf.py`）**：SFT v2（`data/sft-mix-v2` 250M token / lr 1e-4）**1h19m46s / 3,815 步 / 52,825 tok/s / val 1.6038 / peak 12.05GB**；base → v1 → v2：预训练 PPL 15.350→16.307→**16.185（+5.4%）**· SFT PPL 9.818→4.596→4.845· 题库 6→16→15（语义 16）· rep-4 0.727→0.131→**0.066**；v2b（数学保护）val 1.5981 / rep-4 0.117 / 数学修回（3+5=8、7×6=42）但 translate+capability 回归（不部署）；LoRA r=8 **1.20% 可训练 / peak 9.74GB（-2.3GB）/ ckpt 526MB + adapter 6.5MB / 5e-4 全量 1 epoch / final val 1.8253 / 题库 15-18 / rep-4 0.260 / SFT PPL 6.090 / 预训练 PPL 15.690（更少遗忘）**（lr 2e-4 1000 步 1.8839 vs 5e-4 500 步 1.8974）；GGUF F16 326MB / **Q4_K_M 103MB** / Q8_0 173MB，raw 与 PyTorch 输出对拍一致
- **SFT v2c + 六版评测基线（2026-11-20 Day 8 实测，`tools/build_sft_v2.py` v2c 参数）**：v2c 数据（250M token / 列表 10.55% / 会话 587,344 / 监督 76.16% / eqrows≥3 豁免写入 6,243 + 英文拒答砍 2,383 + 英文正例上采样写入 32,754）· 训练 **1h19m40s / 3,815 步 / 52,925 tok/s / val 1.6018 / peak 12.05GB**；六版评测（base/v1/v2/v2b/lora/v2c 同题库同 greedy）：题库 6→16→15→15→15→**17**、rubric 1/8→1/8→4/8→5/8→4/8→**5/8**、rep-4 0.727→0.131→0.066→0.117→0.260→0.135、预训练 PPL 15.350→16.307→16.185→16.186→15.690→**16.184**；**en-fluency 四版全挂 → v2c 首修**；translate-en2zh 仅 v2 过（v2c/v2b 英答英回归）——**修复在评测维度迁移，loss 维度几乎不动（v2c/v2@1000 差 0.0013）**
- **SFT v2e + 八版评测基线（2026-11-20 机动窗口第 2 轮实测）**：v2e 数据 = v2d 规则 + extras 评测去污（12 处 + `assert_no_eval_leak` 断言）+ translate 精确对 180 条 + `--math-upsample 2`（12,500）+ `--en-flu-no-upsample`（770 条 1×）→ 250,001,408 token / 列表 11.47% / 会话 595,348 / 监督 75.99% · 训练 **1h19m19s / 3,815 步 / 53,098 tok/s / val 1.6065 / peak 12.05GB**；八版评测 **rep-4 0.055（全系最低）+ 题库 17/18 + rubric 6/8 + distinct-2 0.860**、translate "我热爱机器学习。"、en-fluency 0.208 / zh-flu 0.224 / reason 0.095 → dev 判据字面全过（首个）；教训 = 按评测缺陷造数据必须配评测集去重（v2~v2d 读数含记忆成分，v1 16/18 反而是干净版）/ 精确指令对 ≠ 方向池。**Day 11 复核修正**：题库 17/18 中 2 题仍残留 brevity（`一年有几个月`/`3 加 5`）；`math-add 8` 是残留记忆、`math-mul 42` 是窄查表（holdout 未见组合全错）；去重断言有假阴性，已修复并新增双向检查器——详见 Day 11 变更条。
- **SFT v2d + 七版评测基线（2026-11-20 机动窗口实测，`tools/build_sft_v2.py` v2d 四新参数）**：v2d 数据（250,001,408 token / 列表 10.15% / 会话 613,180 / 监督 75.65% / ①长答案 keep-den 2：砍 6,507 留 6,296 ②translate-upsample 3：写入 2,106 ③concise-repeat 3：150 条 ④format-repeat 3）+ v2c 规则全沿用 · 训练 **1h19m44s / 3,815 步 / 52,851 tok/s / val 1.6059 / peak 12.05GB**；七版评测：rep-4 **0.084**（SFT 最低档，v2c 0.135 砍 38%）、rubric **6/8 历史最高**、reason 0.728→**0.088** / en-fluency 0.708→0.371 / zh-fluency 0.516→0.303、math-add 纯数字"8"；未达 = rep-4（差 0.004）/ math-mul（回退 72）/ translate 行为（英答中但字词解释，rubric 过关键词不过）/ 关键词题库 15/18（两题假阴，语义 17/18）——**按预注册不部署**。新教训：组合记忆脆弱（小扰动翻转）/ 方向池 ≠ 指令行为 / 英文长答案缺席只能加正例

## 变更记录

- 2026-11-18：建立。立项 = 用户拍板（10 天计划启动拍板前置：新仓 pretrain-lab，同日拍板）；底稿 = NoteFlow `small-llm-10day-plan.md`（2026-09-22）原文照搬逐日方案/风险表 + 决策项升格 D-01~D-08；新增 D-09（全本地）、D-10（SFT 载具待拍板）；风险表补 venv 断链条（nl2fem 双 venv 断链同日实证）；启动时机（10 天连续窗口）待用户拍板，Day 0 清单见 HANDOFF §3。
- 2026-11-18（晚，Day 0）：**启动时机拍板 = Day 1 = 2026-11-19（周四）~ Day 10 = 2026-11-28（周五）**，Day 9 硬缓冲 = 11-27；HANDOFF §5 波次队列已换算实际日期。**D-10 提前拍板 = A 手写 SFT 为主、B ms-swift 对照/兜底**。§2 复现检查同日全绿（GPU 空闲 13998 MiB 与锚点一致 · 磁盘余 2.3T · tmux 在位 · develop 干净同步）。
- 2026-11-18（Day 1）：**用户改判"现在开工"→ 窗口整体前移一日：Day 1 = 2026-11-18（周三）~ Day 10 = 2026-11-27（周四），Day 9 硬缓冲 = 11-26**（原 11-19 起算作废）。Day 1 收官：手写 `tools/model.py`（D-02 全套，22,220,544 参数）+ 字符级 20M 最小闭环（33,000 步 / 96.1 min / 187,480 字符/秒 / val 1.5599，锚定 ln(V)=9.3727 复现）——证据 [reports/2026-11-18-day1-char20m.md](reports/2026-11-18-day1-char20m.md)。脚本目录定 `tools/`（对齐 README 预注册地图）。经验 5 条入 `notes/lessons.md`（首条 = 查表编码表外字符穿透 + 值域断言前置纪律）。
- 2026-11-18（Day 2，当日续跑）：**32k 中英 BPE + 3B memmap 数据流水线收官**。①tokenizer = `data/tokenizer-32k/`（32,000 词表，ByteLevel BPE，specials endoftext/im_start/im_end；留出压缩率 zh 1.841 / en 4.226 chars/token，对 minimind-6400 同文 token 数 0.721×/0.696×）；②**D-06 补充拍板 = en:zh 6:4、token 级、3,000,000,000 token**（实际落成 en 60.0%/zh 40.0%，偏差 <0.01%）；③清洗轻量版 = 长度 100~50k + blake2b-64 精确去重（去重率 en 0.68% / zh 0.00%；MinHash 留 Day 9）；④训练集 = `data/shards/shard-000…005.bin`（1GB/片 × 6）+ `val.bin` 4M（hash%500 文档级留出），全部 sha256 入库、max_id=31999；⑤换轨冒烟首步 loss **10.4542** vs ln(32000)=10.3735（+0.081 ✓），同款 `train_char20m.py` 零代码改动。证据 = [reports/2026-11-18-day2-tokenizer.md](reports/2026-11-18-day2-tokenizer.md) · [reports/2026-11-18-day2-shards.md](reports/2026-11-18-day2-shards.md) · [reports/2026-11-18-day2-smoke.md](reports/2026-11-18-day2-smoke.md)。**Day 2 记为 11-18 当日续跑，Day 3 起日期不变（窗口 11-18~11-27，机制上多出一天缓冲）。**
- 2026-11-19（Day 5）：**SFT v1 + 对比评测**。SFT v1（预注册配置 lr 1e-4 / warmup 100 / 1 epoch over 250M）= 3,815 步 / 1h19m26s / 53,004 tok/s / **SFT val 1.5515** / `EXIT:0`。评测（新增 `tools/eval.py` + `data/eval/tests.json` 18 题 / 9 tag）：**base 预训练 PPL 15.350 / SFT PPL 9.818 / 题库 6-18（33%）** → **sft 预训练 PPL 16.307（遗忘 +6.2%）/ SFT PPL 4.596 / 题库 16-18（89%）**；质性复核发现复读环/编造推理/拒答模板/译错方向，**规则分高估质量**。门② 双证据补齐（最后 10% 降幅 0.0134 + 恒定 lr 探针 0.0051）。
- 2026-11-19（Day 6）：**门② 正式判定 = 不加训 15 亿**（`reports/2026-11-19-day6-gate2.md`），重开条件三条入档。**解码对照（`reports/2026-11-19-day6-decode.md`）证伪"greedy 放大复读"**：greedy rep-4 0.131 vs 采样 0.123；rp1.1/1.2/1.3 → 0.087/0.057/0.032 但题库 15/15/13 —— **复读来自 SFT 数据罗列风格，校准缺失（refuse-unknown 5 配置全挂）与格式跟随（math-mul）也与解码无关** → SFT v2 走数据侧。评测协议定档 = greedy + 关键词判分 + distinct-2/rep-4 + 人工 rubric；`tools/eval.py` 加解码参数与退化指标、`model.generate` 加 top_p/repetition_penalty/greedy。
- 2026-11-19（Day 7）：**SFT 数据 v2/v2b + LoRA + GGUF/Ollama demo**。①供给实测修正：会话级 grep 高估——assistant 侧列表类 34.2%（前 40 万条 46%，非 28.5%）、"只回答"仅 46 条（非 1,703）→ 列表保留 1/5；②`data/sft-mix-v2` 250,001,408 token（校准 13,281 / 格式 6,094 / 列表 9.33% / mask 300 块 3,155 段 0 违规 / val 复用 v1）；**SFT v2 val 1.6038 / rep-4 0.066 / 预训练 PPL 16.185（+5.4%）/ 题库 15-18 关键词（语义 16-18）**；校准/翻译/格式修好，数学回归（3+5=15、7×6=72）；③`data/sft-mix-v2b` 数学/推理样本豁免列表降采样（列表 13.53% / 数学列表 23,253 条）→ **数学修回（8/42）但 rep-4 0.117、translate+capability 回归**，不部署；④LoRA r=8 1.20% 可训练 / peak 9.74GB（-2.3GB）/ ckpt 526MB + adapter 6.5MB；lr 2e-4 1000 步欠拟合（1.8839），5e-4 500 步 1.8974 → 全量 5e-4 1 epoch；⑤GGUF 导出补 llama.cpp 的 q/k RoPE permute（漏掉会"前几词正常后复读"）；F16 326MB / Q4_K_M 103MB / Q8_0 173MB，raw 与 PyTorch 对拍一致；⑥本地 demo `tools/app_stdlib.py` 7860（Ollama 用户级 11435；Gradio 镜像卡死）；⑦评测工具修 CSV 头 5→8 列 + 答案截断 200→1000；rubric 加"没有/不存在"合法承认 + 编造检查。证据 [reports/2026-11-19-day7-sft-v2.md](reports/2026-11-19-day7-sft-v2.md) · `...-day7-eval-v2b.md` · `...-day7-deploy.log`。
- 2026-11-20（Day 8，11-19 晚提前开工）：**v2c 选择性数学保护 + 英文再平衡 + 六版评测 + 报告开写**。①侦察先行：assistant 侧全库 905,718 行统计——英文正例 118,063 / 英文拒答 21,345（78% 集中 rows 800k-900k 桶，250M 预算读不到）/ 数学列表 26,184 按等式行分桶（eqrows≥3 = 9,693 条练习列表）；②`data/sft-mix-v2c` 三规则 = 仅 eqrows≥3 数学列表豁免（写入 6,243）+ 英文拒答保留 1/2（分支先于 calib）+ 英文正例 1/5 选中上采样 2×（写入 32,754）→ 250,001,408 token / 列表 10.55% / mask 0 违规；③**SFT v2c val 1.6018 / 1h19m40s / 52,925 tok/s**，六版评测 = **题库 17/18 + rubric 5/8 双历史最高**、math 修回（8/42）、**en-fluency 四版全挂题首次修复**、refuse-unknown 双过；rep-4 0.135 未达 <0.08 + translate-en2zh 回归（英答英）→ **按预注册保持 v2 部署**，v2c 入档能力最优消融（切换与否列待拍板）；④**REPORT.md 起稿**（11 章骨架 + Day 0~8 素材，G6 从"已起"推进）；⑤教训三条入 lessons（功能特征收窄 / 采样作用域=训练集 / 修复翻新伤口——缺陷在评测维度迁移）。证据 [reports/2026-11-20-day8-v2c.md](reports/2026-11-20-day8-v2c.md) · `...-day8-eval{,-rubric}.md` · [REPORT.md](REPORT.md)。
- 2026-11-20（Day 8 盘点校准批，收波后）：**盘点 + 文档/skill 校准 + 机动窗口计划落档**（[reports/2026-11-20-day8-review.md](reports/2026-11-20-day8-review.md)）。①扫描修复 8 处校准点：REPORT 头部状态/§4.4 标题去"待回填"、§8 GPU 累计精确化 ≈26.1h、§9 Top 13、§0/§11 v2c 行、PROVENANCE 补 sft-v2c ckpt 行、HANDOFF Day 10 行升六版口径、§0/§7 挂盘点报告链；②**v2d 预注册判据落档**（rep-4 <0.08 / translate-en2zh 恢复 / 题库 ≥16 保持 / math 保持 / PPL ≤10%）+ 失败路径（两轮不收敛则锁定 v2 进 Day 10）；③备选 = LoRA r=12 / DPO（dpo.jsonl 0.054GB 在位）/ 中文稀释验证（分语言 val 或 zh tag 分项）；④日程锚点：11-20 缓冲 → 11-22~25 机动（v2d 约半天）→ 11-26 硬缓冲 → 11-27 Day 10 六版定稿。G1~G5 全闭环，机动窗口全是改进项。
- 2026-11-18（Day 4，18:46 起跑）：**140M 主训练启动 + SFT 数据/脚本就绪**。①主训练 `main140m` = 用户拍板"现在起跑"，bs8×accum8×T1024（65,536 tok/step · 45,777 步），起跑读数 `[anchor] 10.5431`（与探针同值）· **52.8k tok/s** · 1.25s/步 · peak 10.51GB · 58°C · **val@500 4.9742**（比按探针外推的 8.5~9.0 低得多——早期曲线是凸的，外推必须按 token 数并注明区间依据）· ETA 11-19 ~10:30；②SFT 数据 `data/sft-mix/` = **250,001,408 token**（404,210 条对话，模板 `<|im_start|>{role}\n{content}<|im_end|>\n` + 25% 预训练块，assistant-only mask，监督占比 78.15%）+ val 2M（文档级留出），构建 4.0 min，指纹入库；③`tools/sft.py`（底座载入 + `ignore_index=-100` + chat 采样，CPU 3 步自检 EXIT:0），GPU 冒烟待主训练让出显存；④`tools/model.py` forward 加 `ignore_index` 参数（默认 -100，预训练行为不变）；⑤起跑前预检 eval bs16（peak 10.51GB 不 OOM）；⑥教训 6 条入 lessons（pkill 自匹配 / 会话不跨块 / 段级 mask 断言 / val 留出率决定读盘量 / eval bs 单独预检 / 早期 loss 不外推）。
- 2026-11-18（Day 3，当日续跑）：**完整训练框架 + 决策门① PASS**。①`tools/train.py`（多分片加权取批 / 梯度累积 / token 预算定 cosine / 三路 RNG 续训 / 固定 val 窗口 / 双语固定 prompt 采样 / `EXIT:0|1` 标记）；②50M 定档 d576/L8/H9 **50,292,288**、micro-bs 16（封顶），30min 预注册跑 **120,517 tok/s / 215.7M token / val 3.6377**；③**门①判定 = 140M 探针 52,250 tok/s ≥ 35k → PASS**（超 49%，100M/2B 兜底不启用），3B 单程 **15.9h**（比原估 23.8h 省 ~8h）；④140M 主训练定档 bs8×accum8 = 65,536 tok/step、lr 6e-4/warmup 500/cosine→6e-5、ckpt 每 1000 步 46 件 ≈76GB，命令见 reports/2026-11-18-day3-140m-probe.md §6；⑤续训闭环 kill 验证通过（恢复后 step 40 val 7.6893 与 kill 前一致）；⑥负面结果入档：torch.compile 4,077 tok/s（慢 13×，弃用）、CE fp32 三份副本是显存上限主因、micro-bs 非单调提速。证据 [reports/2026-11-18-day3-framework.md](reports/2026-11-18-day3-framework.md) · [2026-11-18-day3-50m-30min.md](reports/2026-11-18-day3-50m-30min.md) · [2026-11-18-day3-140m-probe.md](reports/2026-11-18-day3-140m-probe.md)。**Day 3 记为 11-18 当日续跑；主训练启动时点待用户拍板（默认 Day 4 = 11-19）**。
- 2026-11-18（Day 2 盘点校准批，**跑前**）：①**门①口径校准 = 140M 等效 ≥35k tok/s**（50M 30min 预注册动作保留 + 140M 20~30 步探针；50M 按 FLOPs 比 2.74× 交叉校验，需 ≥96k 才等价），避免"50M 35k 放行、140M 实际 ~13k"的误判（原文未指明测量模型，见 §4.1）；②配置核准 = 140M d768/L16/H12 **137,847,552** 参数；50M 推荐 d576/L8/H9 **50,292,288**（d/L=72，宽浅对照；备选 d512/L10/H8 **48,507,392**，d/L=51.2 更接近 140M 的 48）；100M 兜底 d640/L16/H10 **99,799,680**；③3B 单程时长表（35k→~23.8h / 40k→~20.8h / 50k→~16.7h）与 ckpt 预算（1.65GB×46≈76GB @bs64）落档；④新增风险「zh 语料供给不足（门②加训 1.5B）」及预案（en-heavy 扩展 / SkyPile / 不超 1 epoch）；⑤**门②量化口径待 Day 5 中期曲线定标**（最后 10% val 降幅候选 >0.02~0.03）；⑥进度对照 G1~G6 落 PLAN §2；证据链复核：分片+tokenizer 指纹复算全过、14 份文档 0 断链、`.gitignore` 补 `reports/*.log` 例外（Day 1 日志漏入库已修）。
- 2026-11-20（机动窗口 · v2d 数据迭代，Day 8 收官当日）：**用户拍板"机动选题 = v2d；部署保持 v2"**。侦察两轮（池形状 + 预算截断作用域）→ `build_sft_v2.py` 四新参数（`--long-answer-keep-den 2` / `--translate-upsample 3` / `--concise-repeat 3` / `--format-repeat 3`）+ `gen_sft_v2_extra.py` 新增 concise 类（50 unique，含英文 fluency 组）→ `data/sft-mix-v2d`（250,001,408 token 同预算 / 列表 10.15% / mask 0 违规 / 指纹 4 条）。SFT v2d = **val 1.6059 / 1h19m44s / 52,851 tok/s / EXIT:0**。七版评测：**rep-4 0.084（SFT 最低档，v2c 0.135 砍 38%）+ rubric 6/8（历史最高）**、reason 0.728→**0.088**、en-fluency 0.708→0.371、math-add 纯数字"8"；未达判据 = rep-4（差 0.004）/ math-mul（回退 72）/ translate 行为（字词解释）/ 关键词题库 15/18（语义 17/18）。**按预注册不切换部署（v2 保持）**；v2d 入档"复读修复最有效 + rubric 最高"消融。同步：REPORT 加 §4.5 v2d + 七版表 + loss 图（`tools/plot_loss.py` 新脚本）；lessons 四条新教训（组合记忆脆弱 / 方向池≠指令行为 / 英文长答案缺席 / 判据差 0.004 也不放行）。v2e 候选（translate 精确样本扩容 + math 专项重复 + en_flu 降采样）留 11-22~25 拍板——预注册失败路径：两轮不收敛则锁定 v2 进 Day 10。证据 [reports/2026-11-20-v2d.md](reports/2026-11-20-v2d.md) · `...-v2d-eval{,-rubric}.md`。
- 2026-11-20（机动窗口第 2 轮 · v2e 去污轮）：**开工发现评测污染**——v2 起 extras（calibration/format/helpful）与 18 题原句系统性撞车（2027 世界杯=refuse-unknown / ARITH 7×6=math-mul / 水的化学式=fact-water / 中国的首都=fact-capital-cn / 学习编程=list-3 / 机器学习定义=def-ml / 下雨=reason；v2d concise 又加 ocean&北京），**v2~v2d 题库分含记忆成分、v1 的 16/18 反而是干净读数**。v2e 改动 5 项：①12 处同型变体去污（calibration 1,630→1,628 / format 989→979）+ `assert_no_eval_leak` 硬断言；②translate.jsonl 精确指令对 30×6=180；③`--math-upsample 2`（6,250→12,500）；④`--en-flu-no-upsample`（770 条 1×）；⑤v2d 其余沿用。构建 250,001,408 token / 列表 11.47% / mask 0 违规 / 4.8 min；训练 **EXIT:0 / val 1.6065 / 1h19m19s / 53,098 tok/s**；八版评测 **rep-4 0.055（全系最低）/ 题库 17/18（去污后）/ rubric 6/8 / distinct-2 0.860 / translate "我热爱机器学习。" / math 8+42 真泛化 / PPL +5.5%** → **五项预注册判据全过**，全面优于 v2 → **部署切换 v2e 列待拍板**（对外可见动作：GGUF/Ollama/demo/模型卡联动）。三条新教训入 lessons（评测集去重纪律 / 去污证明"能力不足"部分为记忆假象 / 精确指令对 vs 方向池）。证据 [reports/2026-11-20-v2e.md](reports/2026-11-20-v2e.md) · `...-v2e-eval{,-rubric}.md`。
- 2026-11-20（最终阶段 spec 推进）：**部署切 v2e + 报告扩写**（用户"按 spec 存档并推进"，spec = `specs/2026-11-20-final-phase.md`）。T1：v2e GGUF F16（sha `eee10822`）→ Ollama 三 tag（F16/Q8/Q4）→ demo 7860 切 **`pretrain-lab-sft-v2e-q8`**，旧 v2 tag 全保留（回滚 <1min）。**新发现：Q4_K_M 量化吃掉新学能力**（math 42→72、translate 退回英文原句）——F16 三同对拍 5/5 逐字一致、Q8_0 保住全部新能力 → 部署默认 Q8_0；新增"量化保真度抽检"验收条款（spec AC11）与 skill 红线。T2：REPORT §5.1 评测污染独立章（撞车清单/12 处去污/assert_no_eval_leak/干净读数结论）+ §10 复现→v2e + §0 成绩单 v2e 口径 + 五轮迭代结论。验收 AC2~AC8 命令级通过。证据 `reports/2026-11-20-deploy-v2e.md` · commit `d0c973d`/`5fc4d2c`。
- 2026-11-20（**Day 10 终检，提前 7 天收官**）：用户持卡执行 HANDOFF §7 T4。①§5 实际日期改为 **Day 10 = 11-20**（原定 11-27）；②**八版终表**（§0 8 行 × 7 列 + **"读数性质（含记忆/干净）"列** + §4.7 裁决表；与 v2e-eval/rubric 逐项对账）；③repo 整理（README 收官态 / MODEL_CARD 全面转 v2e 口径 / 断链扫描 / 证据 md-csv-log 三分核对 / PROVENANCE 补 lora-r12 指纹）；④**§10 复现走查**：v2e build **bit-for-bit**（4/4 sha256 + meta 全字段）、eval **18/18 行逐字节**、deploy **F16 5/5** + Q8 保住新学能力；⑤**LoRA r=12**（1.79% 可训练 / val 1.8054 / 题库 15-18 / rubric 5-8 / rep-4 0.249 / peak 9.76GB）——rank↑ 只补 0.02 val，仍不部署；⑥终检修正 **demo 温度 T0.7→T0.3**（translate 方向 16/20→20/20）；⑦REPORT 置 **FINAL**、spec 置 **COMPLETED**（AC1~AC11 核验；AC1 口径勘误 = 1 个 F16 GGUF + Ollama `-q` 两档量化，非 3 个 .gguf）；⑧成本重算 **≈30.3h GPU / ~145GB 磁盘**。证据 [reports/2026-11-20-day10-repro-check.md](reports/2026-11-20-day10-repro-check.md) · `...-deploy-v2e-recheck.log` · `...-lora-r12-eval{,-rubric}.md`。
- 2026-11-20（**Day 10 holdout 复核**）：用户选择"推进 holdout"。新写 **30 题未见题**（13 tag，同型变体；三层去重：vs dev 18 题 / vs `sft-extra-v2/*` / vs minimind SFT 源 905,718 行 user 内容；初稿 8 处撞车逐条换成变体；**Day 11 双向复检又换 4 题**）→ `data/eval/tests-holdout.json`（**v2 修订版 sha `e6e31aaa`**）→ 9 ckpt 同 greedy 重跑（`--skip-ppl`）。**关键词原始分** 21~23/30（SFT 全版），**人工复核（v2）**：base 12 / v1 21 / v2 **23** / v2b 21 / v2c 21 / v2d 22 / v2e **23** / lora8 19 / lora12 19——**dev 集的 v2e 17 vs 15 优势不复现**。关键逐题：`13 乘以 5` 全错（56/40/35）、`17 加 6` 答 19、`100 减 37` 答 37（math 42 是窄查表不是算术）；`Knowledge is power` 回英文（translate 精确指令对只教句式）；**calibration 三道未来题 v2~v2e 稳定拒绝编造**（base/v1/LoRA 会编）。关键词判分在 holdout 上假阳/假阴明显（moon-count 7 假阳 / weather 2 假阴 / knowledge 2 部分匹配 / reason 1 偶然命中）→ 报告新增 §5.2、§0/§4.6/§4.7/§5.1/§9/§11 表述降级修正、lessons 两条、MODEL_CARD 限制更新。**部署不变**（v2e-q8 holdout 不劣于 v2、rep-4 0.105 最低），对外表述改为"dev 全面最优 + holdout 无显著差异 + 复读最低"。证据 [reports/2026-11-20-holdout-audit.md](reports/2026-11-20-holdout-audit.md) · `...-holdout-eval-v2.md`。
- 2026-11-20（**收官后复核 · 去重假阴性**）：用新检查器 `tools/check_eval_leak.py` 双向复扫历史数据，发现两处问题。①**dev 集仍有 2 题残留**：`一年有几个月`/`3 加 5` 藏在 format brevity extras（4 条）——旧 `assert_no_eval_leak` 的 `len(prompt)>=8` 守卫 + 只去空白的 norm 让 v2e 的"0 撞车"成为假阴性。按 16 题干净子集重算：v1 14 / v2 14 / v2c 15 / **v2e 15**（v2b/v2d/LoRA 13）；v2e 的 17/18 降级为"17/18，2 题残留"，五项判据 = "dev 字面全过、数学实质未过"（math-add 8 是残留记忆、math-mul 42 是窄查表）。②**holdout 初版 3 题近重复**（2030 世界杯/光合作用/人工智能——训练样本是评测题前缀；上海在 concise），单向检查漏掉 → 换题（冬奥/细胞呼吸/引力/成都）+ 数学换 13×5/17+6 消除数字嵌套 → 复扫 0 撞车 → 重跑 v2（sha `e6e31aaa`）：**人工复核 v2e 与 v2 同为 23/30**，结论不变。修复：断言 norm 去所有非单词字符、取消长度守卫、内置已知撞车自测、同时查 dev+holdout；新增 `tools/check_eval_leak.py`（双向三层）。**决策：不重建不重训**（两轮为限；残留不改变部署结论），改为披露 + 干净子集读数。证据 [reports/2026-11-20-eval-leak-recheck.md](reports/2026-11-20-eval-leak-recheck.md) · `...-holdout-eval-v2.md` · `...-holdout-audit.md` §7。
- 2026-11-21（**Day 12 · 收官后深化**）：用户拍板 HANDOFF §7 建议顺序 1→2→3 → spec `specs/2026-11-21-post-final-deepening.md`（预注册判据跑前冻结）。①**holdout 扩容 90 题**（`tests-holdout-v3.json`，sha `2539aa2b`；math 14 / translate 14 / calibration 6 能力块；出题避让 = ARITH 2~12 全对 → operand ≥13、calibration 年份 → 2044+、concise 题面清单；首轮 23 处撞车换 8 题后 EXIT 0）；**三块判据 = 数学 ✗（0~3/14）· 翻译 ✗（0~5/14）· calibration ✓（v2 系 5~6/6）；人工校准 v2e 53 vs v2 47（+6 达预注册阈值 ≥5）——30 题"无显著差异"系欠功效**；`今天非常冷`全员译 hot（先验反扑探针）；lightspeed 9/10 版答对 299,792 而关键词全灭（数字写法 FN 教训）。②**LoRA r12 2ep**：EXIT:0 / val 1.7921（1.75~1.80 档）/ 2h37m / holdout 人工 48（+6 vs 1ep）/ rep-4 0.176——**rank 与 epochs 单独加码都不够（−0.020 / −0.013）**，"低秩 × 少 epoch 组合不足"取代"1 epoch 欠拟合"表述。③**分语言 val**（新工具 `tools/eval_lang.py`）：英文上采样对 zh sup ±0.15% **无稀释**（Day 8 遗留疑问收口）；预注册"vs v1"基线混杂 v2 自身改动，判读改按因果口径（vs v2）并披露。部署不变（v2e-q8）。证据 [reports/2026-11-21-holdout-audit-v3.md](reports/2026-11-21-holdout-audit-v3.md) · `...-lora-r12-2ep.md` · `...-langval.md`。
- 2026-11-21（**公开发布 Phase 1**）：用户拍板"对外发布"→ 立 spec [`specs/2026-11-21-public-release.md`](specs/2026-11-21-public-release.md)。完成发布阻断项：①许可证/归属（Apache-2.0 + CC-BY-4.0 + NOTICE + CITATION + CHANGELOG）；②英文 README + 中文 README + docs 五件（quickstart/reproduction/evaluation/architecture/faq）+ 内部文档 banner；③requirements + scripts（setup/download_data/download_model/run_demo/reproduce_eval）；④v2e HF fp16（137,847,552 参数 / 262.9 MiB / greedy 30/30 与 PyTorch 一致）+ 独立 Q8_0 GGUF（174 MB / sha `8b64b668…` / Ollama 输出与部署 tag 逐字一致）+ F16 指纹；⑤轻量 CI（题库 schema / 去重检查器阳性对照 / holdout v3 0 撞车 / 12 份读者面文档 0 断链 / compileall 全过）。**未做公网推送/上传**；Phase 2（900 格标签 + McNemar/CI + 独立复核 + v2f 决策）与 Phase 3（HF Hub / GitHub Release / 长文）待执行。
- 2026-11-21（**公开发布 Phase 2 部分完成**）：900 格逐题标签落盘（`reports/2026-11-21-holdout-v3-manual-labels.csv`）+ `tools/score_manual.py` 复算：**v2e 52 vs v2 45（+7；audit +6）**；**McNemar 精确 p=0.0923（不显著）**，bootstrap 95% CI [0.000,0.156]；分 tag fluency-en +5、reason +2，数学 −1、翻译/calibration 持平；old30 +2 / new60 +5。**对外措辞降级为"达到预注册阈值、统计上不显著"**；独立复核与 v2f 决策待执行。
