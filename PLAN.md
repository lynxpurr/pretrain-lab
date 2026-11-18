# pretrain-lab — 小模型从零训练 10 天行动（PLAN）

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

**进度对照（2026-11-18 Day 2 盘点）**：

| 门 | 状态 | 依据 / 缺口 |
|---|---|---|
| G1 最小闭环 + 决策门① | **✅ 完成（Day 3）** | `tools/train.py` 框架（多分片/累积/续训/固定 val/采样）+ 50M 冒烟 + 50M 30min 预注册吞吐 + 140M 探针；**门① PASS = 140M 52,250 tok/s ≥ 35k**（3B 单程 15.9h）。证据 [reports/2026-11-18-day3-framework.md](reports/2026-11-18-day3-framework.md) · [50m-30min](reports/2026-11-18-day3-50m-30min.md) · [140m-probe](reports/2026-11-18-day3-140m-probe.md) |
| G2 140M 底座 | **全部就绪，训练 Day 4 启动** | 3B token + val 4M + 32k tokenizer + 训练框架 + **门①已过（52,250 tok/s）**；主训练命令定档于 reports/2026-11-18-day3-140m-probe.md §6 |
| G3 SFT + LoRA | **数据就绪，载具已拍板** | sft_t2t_mini 1.739GB 在位；D-10 = A 主 / B 兜底 |
| G4 本地 demo | 未开始（Day 7） | 依赖 G3，超期可砍（PLAN §4 预算与裁法） |
| G5 评测框架 + 对比 | 未开始（Day 5 起） | val.bin 4M 已备；评测维度与评分标准 Day 5 定义 |
| G6 报告 + repo 整理 | 证据链按日积累中 | Day 0~3 四日证据 + 指纹全部入库 |

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

## 变更记录

- 2026-11-18：建立。立项 = 用户拍板（10 天计划启动拍板前置：新仓 pretrain-lab，同日拍板）；底稿 = NoteFlow `small-llm-10day-plan.md`（2026-09-22）原文照搬逐日方案/风险表 + 决策项升格 D-01~D-08；新增 D-09（全本地）、D-10（SFT 载具待拍板）；风险表补 venv 断链条（nl2fem 双 venv 断链同日实证）；启动时机（10 天连续窗口）待用户拍板，Day 0 清单见 HANDOFF §3。
- 2026-11-18（晚，Day 0）：**启动时机拍板 = Day 1 = 2026-11-19（周四）~ Day 10 = 2026-11-28（周五）**，Day 9 硬缓冲 = 11-27；HANDOFF §5 波次队列已换算实际日期。**D-10 提前拍板 = A 手写 SFT 为主、B ms-swift 对照/兜底**。§2 复现检查同日全绿（GPU 空闲 13998 MiB 与锚点一致 · 磁盘余 2.3T · tmux 在位 · develop 干净同步）。
- 2026-11-18（Day 1）：**用户改判"现在开工"→ 窗口整体前移一日：Day 1 = 2026-11-18（周三）~ Day 10 = 2026-11-27（周四），Day 9 硬缓冲 = 11-26**（原 11-19 起算作废）。Day 1 收官：手写 `tools/model.py`（D-02 全套，22,220,544 参数）+ 字符级 20M 最小闭环（33,000 步 / 96.1 min / 187,480 字符/秒 / val 1.5599，锚定 ln(V)=9.3727 复现）——证据 [reports/2026-11-18-day1-char20m.md](reports/2026-11-18-day1-char20m.md)。脚本目录定 `tools/`（对齐 README 预注册地图）。经验 5 条入 `notes/lessons.md`（首条 = 查表编码表外字符穿透 + 值域断言前置纪律）。
- 2026-11-18（Day 2，当日续跑）：**32k 中英 BPE + 3B memmap 数据流水线收官**。①tokenizer = `data/tokenizer-32k/`（32,000 词表，ByteLevel BPE，specials endoftext/im_start/im_end；留出压缩率 zh 1.841 / en 4.226 chars/token，对 minimind-6400 同文 token 数 0.721×/0.696×）；②**D-06 补充拍板 = en:zh 6:4、token 级、3,000,000,000 token**（实际落成 en 60.0%/zh 40.0%，偏差 <0.01%）；③清洗轻量版 = 长度 100~50k + blake2b-64 精确去重（去重率 en 0.68% / zh 0.00%；MinHash 留 Day 9）；④训练集 = `data/shards/shard-000…005.bin`（1GB/片 × 6）+ `val.bin` 4M（hash%500 文档级留出），全部 sha256 入库、max_id=31999；⑤换轨冒烟首步 loss **10.4542** vs ln(32000)=10.3735（+0.081 ✓），同款 `train_char20m.py` 零代码改动。证据 = [reports/2026-11-18-day2-tokenizer.md](reports/2026-11-18-day2-tokenizer.md) · [reports/2026-11-18-day2-shards.md](reports/2026-11-18-day2-shards.md) · [reports/2026-11-18-day2-smoke.md](reports/2026-11-18-day2-smoke.md)。**Day 2 记为 11-18 当日续跑，Day 3 起日期不变（窗口 11-18~11-27，机制上多出一天缓冲）。**
- 2026-11-18（Day 3，当日续跑）：**完整训练框架 + 决策门① PASS**。①`tools/train.py`（多分片加权取批 / 梯度累积 / token 预算定 cosine / 三路 RNG 续训 / 固定 val 窗口 / 双语固定 prompt 采样 / `EXIT:0|1` 标记）；②50M 定档 d576/L8/H9 **50,292,288**、micro-bs 16（封顶），30min 预注册跑 **120,517 tok/s / 215.7M token / val 3.6377**；③**门①判定 = 140M 探针 52,250 tok/s ≥ 35k → PASS**（超 49%，100M/2B 兜底不启用），3B 单程 **15.9h**（比原估 23.8h 省 ~8h）；④140M 主训练定档 bs8×accum8 = 65,536 tok/step、lr 6e-4/warmup 500/cosine→6e-5、ckpt 每 1000 步 46 件 ≈76GB，命令见 reports/2026-11-18-day3-140m-probe.md §6；⑤续训闭环 kill 验证通过（恢复后 step 40 val 7.6893 与 kill 前一致）；⑥负面结果入档：torch.compile 4,077 tok/s（慢 13×，弃用）、CE fp32 三份副本是显存上限主因、micro-bs 非单调提速。证据 [reports/2026-11-18-day3-framework.md](reports/2026-11-18-day3-framework.md) · [2026-11-18-day3-50m-30min.md](reports/2026-11-18-day3-50m-30min.md) · [2026-11-18-day3-140m-probe.md](reports/2026-11-18-day3-140m-probe.md)。**Day 3 记为 11-18 当日续跑；主训练启动时点待用户拍板（默认 Day 4 = 11-19）**。
- 2026-11-18（Day 2 盘点校准批，**跑前**）：①**门①口径校准 = 140M 等效 ≥35k tok/s**（50M 30min 预注册动作保留 + 140M 20~30 步探针；50M 按 FLOPs 比 2.74× 交叉校验，需 ≥96k 才等价），避免"50M 35k 放行、140M 实际 ~13k"的误判（原文未指明测量模型，见 §4.1）；②配置核准 = 140M d768/L16/H12 **137,847,552** 参数；50M 推荐 d576/L8/H9 **50,292,288**（d/L=72，宽浅对照；备选 d512/L10/H8 **48,507,392**，d/L=51.2 更接近 140M 的 48）；100M 兜底 d640/L16/H10 **99,799,680**；③3B 单程时长表（35k→~23.8h / 40k→~20.8h / 50k→~16.7h）与 ckpt 预算（1.65GB×46≈76GB @bs64）落档；④新增风险「zh 语料供给不足（门②加训 1.5B）」及预案（en-heavy 扩展 / SkyPile / 不超 1 epoch）；⑤**门②量化口径待 Day 5 中期曲线定标**（最后 10% val 降幅候选 >0.02~0.03）；⑥进度对照 G1~G6 落 PLAN §2；证据链复核：分片+tokenizer 指纹复算全过、14 份文档 0 断链、`.gitignore` 补 `reports/*.log` 例外（Day 1 日志漏入库已修）。
