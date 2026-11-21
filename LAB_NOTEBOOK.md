# LAB_NOTEBOOK — 逐日记账

> **过程记录（非读者入口）**：本文件是项目逐日开发笔记，保留当时的本地路径与内部引用。公开读者请从 [README.md](README.md) / [docs/](docs/) 进入；发布状态见 [docs/internal/README.md](docs/internal/README.md)。
>
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

## Day 2 · 2026-11-18（Day 1 当日续跑）· 32k BPE tokenizer + memmap 数据流水线

- 决策：①用户要求当日续跑 → Day 2 记为 11-18，Day 3 起日期不动（窗口 11-18~11-27 不变，机制上多出一天缓冲）；②tokenizer = **32k ByteLevel BPE**（D-03），zh/en 各采样 300MB 训 merge、各留 5MB 评测；③specials = `<|endoftext|>`=0 / `<|im_start|>`=1 / `<|im_end|>`=2，不引入 BOS（SFT 阶段再用 im 标记）；④混配比 **en:zh = 6:4、token 级、目标 3B**（D-06 补充拍板；按累计缺口调度而非 chars→token 估算）；⑤清洗轻量版 = 长度 100~50k + **blake2b-64 精确去重**（MinHash 近似去重留 Day 9 缓冲）；⑥val = `hash % 500 == 0` 文档级留出 4M token（预算满后多余候选丢弃、不回 train）；⑦分片 **1GB/片 × 6**（536,870,912 token/片，末片 315,645,440）+ val，uint16、每文档尾接 EOS；⑧**SkyPile 暂不下载**——zh 现有库可覆盖 1.2B 需求的 ~72%，加训缺口 Day 6 决策门②再拍。
- 现象：BPE 训练吃内存（600MB 采样 → 峰值 RSS ~22GB、271s；词频统计与语料词数成正比）；`show_progress` 的 tqdm 在 `tee` 管道下不落盘——**日志没进度 ≠ 卡死**，看 CPU/RSS；首次自检挂在 `decode()` 默认 `skip_special_tokens=True` 把探针里的 `<|endoftext|>` 吞掉（修 = 普通文本 + specials 两段自检）；建片单进程 2.42M tok/s 无中断，`sha256sum -c` 7/7 OK，值域扫描 max_id=31999；冒烟复用 `train_char20m.py` **零代码改动**，只换 `--data-dir`。
- 读数：词表 **32,000**；留出压缩率 zh **1.841** / en **4.226** chars/token（minimind-6400 为 1.328 / 2.939，同文 token 数 **0.721× / 0.696×**）；全量流压缩率 en 4.294 / zh 1.783；去重率 en **0.68%** / zh **0.00%**；训练集 **3,000,000,000 token**（en 60.0% / zh 40.0%，6 片 6.0GB）+ val 4M，构建 **20.7 min**；换轨冒烟首步 **10.4542** vs ln(32000)=**10.3735**（+0.081 ✓），60 步 10.45→7.75 / val 7.77。证据 = [reports/2026-11-18-day2-tokenizer.md](reports/2026-11-18-day2-tokenizer.md) · [reports/2026-11-18-day2-shards.md](reports/2026-11-18-day2-shards.md) · [reports/2026-11-18-day2-smoke.md](reports/2026-11-18-day2-smoke.md)。
- 疑问：①BPE 词表大 5 倍、token 只省 ~30%，边际收益为什么递减（qa-day-2 题 1）？②3B token 里 zh 用掉全库 ~72%，若决策门②加训 1.5B 从哪补（SkyPile / 复用 / 降 zh 比例）？③首步 loss 比 ln(32000) 高 0.081——差值来自初始化 logits 方差还是数据分布（qa-day-2 题 2）？——已并入 [notes/qa-day-2.md](notes/qa-day-2.md) 题目池。
- 补记（2026-11-18 盘点校准批）：**门①口径校准为 140M 等效 ≥35k tok/s**——原文"50M 跑 30min 测吞吐"未指明测量模型；按 Day 1 有效算力 25 TFLOPS 外推，50M 的 35k ≈ 140M 的 ~13k（3B 要 64h），直接放行会误判。Day 3 加 140M 20~30 步探针，50M 按 FLOPs 比 2.74× 交叉校验。配置核准：140M = 137,847,552；50M 推荐 d576/L8/H9 = 50,292,288；100M 兜底 d640/L16/H10 = 99,799,680。3B 单程 35k≈23.8h / 40k≈20.8h；ckpt ≈1.65GB/个（bs64 → 46 个 ≈76GB）。新增风险：zh 供给（门②加训 1.5B 需 en-heavy 或 SkyPile）。证据链复核：tokenizer/分片指纹复算全过、14 份文档 0 断链、`reports/*.log` 例外已补。

## Day 3 · 2026-11-18（当日续跑）· 完整训练框架 + 50M/140M 探针 + 决策门①

- 决策：①`tools/train.py` 六件 = 多分片加权取片（不拼单文件）/ **token 预算定 total_steps**（LR 与墙钟解耦）/ 续训含 torch+cuda+data 三路 RNG / 固定块 val 窗口（跨 step、跨 resume 可比）/ 双语固定 prompt 采样（`skip_special_tokens=False`）/ `logs/<run>.exit` 标记（stale exit 机制化）；②50M 定档 d576/L8/H9 = 50,292,288，micro-bs **16**（封顶），bs16×accum4 = 65,536 tok/step；③**140M 主训练定档 bs8×accum8**（三个变体实测最快：52,250 vs bs10 51,230 vs bs16+grad-ckpt 40,449），lr 6e-4 / warmup 500 / cosine→6e-5 / wd 0.1 / clip 1.0，ckpt 每 1000 步 46 件 ≈76GB（G2 谱系）；④**决策门① PASS**：140M 探针 52,250 tok/s ≥ 35k（超 49%），**不启用 100M/2B 兜底**；3B 单程 **15.9h**（比 PLAN §4.1 预估的 23.8h 省 ~8h）；⑤Day 3 记为 11-18（用户要求提前开工），主训练启动时点未拍板 → 默认按 DAY 4 = 11-19 起跑，命令已在报告 §6 备好。
- 现象：①**续训坑**：`torch.load(map_location="cuda")` 把 RNG 字节张量也搬上 GPU，`set_rng_state` 要 CPU ByteTensor → `TypeError`；修 = `.cpu()`（清单第 2 项"kill 一次验证"直接兜住了这个坑）；②`torch.compile` 在 sm_120 上反而慢 13 倍（4,077 tok/s），弃用并记录；③**CE 三份副本卡显存**：autocast 下 logits bf16 + fp32 升档 + log_softmax 保留，bs16×1024×32k 时 ≈5.25GB，梯度累积摊不薄（逐 token 独立）；④两次自伤：`head -13` 截断管道把训练打成 BrokenPipe → `EXIT:1`（非训练问题）；探索跑的 log 被我 `rm` 过，按证据纪律补跑留存后才写报告。
- 读数：50M 30min 预注册跑 = **3,292 步 / 215.7M token / 120,517 tok/s / val 3.6377**（峰值 10.72GB · 58°C · 98% util · 无降频）；140M 探针 40 步 = **52,250 tok/s / val 8.9169**（峰值 10.51GB）；50M 冒烟首步锚 **10.4756**（+0.102），100 步 val 6.9161；续训 kill→restore：step 40 val 前后均 **7.6893**，step/tokens 精确对齐，`EXIT:0`。证据 = [reports/2026-11-18-day3-framework.md](reports/2026-11-18-day3-framework.md) · [reports/2026-11-18-day3-50m-30min.md](reports/2026-11-18-day3-50m-30min.md) · [reports/2026-11-18-day3-140m-probe.md](reports/2026-11-18-day3-140m-probe.md)（各附 csv+log）。
- 疑问：①为什么 micro-bs 8 比 10/16 都快（不是越大越快）？②首步锚偏差随规模单调上升（+0.059 → +0.081 → +0.170），是残差流累积还是初始化尺度？③50M 按 2.74× 折算 44k、140M 实测 52k——6N 口径漏掉了什么？——已并入 [notes/qa-day-3.md](notes/qa-day-3.md) 题目池。

## Day 4 · 2026-11-18（晚起跑，已收官）· 140M 主训练 + SFT 数据/脚本

- 决策：①用户拍板"现在起跑"→ 主训练 18:46 启动（Day 4 记为 11-18 晚，收官预计 11-19 ~10:30）；②起跑前加 1 分钟预检（同命令 + eval bs16）确认 eval 峰值 10.51GB 不 OOM——避免跑到 step 500 第一次 eval 才炸；③SFT 模板定档 `<|im_start|>{role}\n{content}<|im_end|>\n`（对齐 minimind 原格式，specials 1/2，不二次翻译）；④SFT 打包**会话不跨块**（装不下补 EOS 收块），代价 ~13% 填充换语义完整；⑤SFT 数据 = **250M token**（404,210 会话 + 25% 预训练块防幻觉）、val 2M 文档级留出（`blake2b64(line)%100`）；⑥`tools/sft.py` 与 `train.py` 同源（复用 lr_at/make_optimizer/fmt_dur），只换数据/损失/初始化三处。
- 现象：①预检时我用 `| head -6` 截断管道，SIGPIPE 把预检进程打成 EXIT:1（第二次犯同一错，已入 lessons）；②`build_sft.py` 第一版把会话截断到块边界（段被切断），改为"会话不跨块 + EOS 填充"后段级自检 0 违规；③`pkill -f "run-name _preflight"` 又把自己的 shell 杀了（pattern 自匹配，第三次）——安全姿势 = 按 `/proc/<pid>/comm` 过滤只杀 python。
- 读数：主训练起跑 `[anchor] 10.5431 (+0.170)`（与探针完全同值）· **52.8k tok/s** · 1.25s/步 · peak 10.51GB · 58°C / 97~99% util / SM 2797MHz；**val@500 = 4.9742**（我预判 8.5~9.0 严重偏高——500 步已是 32.8M token，是探针 40 步的 12.5 倍，早期 loss 下降远快于线性外推）；ckpt@1000 起每 1000 步滚动。SFT 数据构建 **4.0 min**：250,001,408 token / 244,142 块 / 监督占比 78.15% / 长会话截断 1,012 条（0.11%）/ 分段编码自检 30 例过；`tools/sft.py` CPU 3 步自检 `EXIT:0`（随机小模型 anchor 10.3615 ≈ ln(32000)）。
- 疑问：①SFT 的 `ignore_index=-100` 在 bf16 下与 fp32 的数值差异会不会影响收敛（Day 5 对照）？②25% 预训练混入是"按块"的，块内没有混合——这种粗粒度混配对比按样本混合差多少？③eval loss 在 SFT 阶段应看"监督 token 的 CE"还是全 token CE（我们把二者混在一个数里）？——留 Day 5 概念题。

## Day 5 · 2026-11-19 · 140M 主训练收官 + SFT v1 + 门② 预读

- 决策：①**终版 `out/main140m/last.pt`（step 45,777）为 SFT 底座**；②门② 预读 = **不加训**（最后 10% val 降幅 **0.0134 < 0.02~0.03** 阈值），正式判定留 Day 6，并加一道**恒定 lr 探针**（从 ckpt-0041000 起 300 步 @6e-5）分辨"lr 退火"与"数据饱和"；③SFT v1 预注册不变（lr 1e-4 / warmup 100 / 1 epoch over 250M ≈3,815 步 ≈1.3h）；④46 个 ckpt 全留（G2 谱系），SFT 后再按需清理。
- 现象：16h07m41s **一次跑完**——0 次 loss 尖峰（2,289 窗口）、0 次 OOM、0 次中断，`EXIT:0`；GPU 收官后自动回落空闲（1,863 MiB / 37°C）。开销仅 **9m17s（0.96%）**：92 次 eval + 22 次采样 + 46 次 ckpt 写盘。吞吐全程 52.2~52.8k，无热降频（SM 恒 2797MHz）。
- 读数：**val 2.7709**（train 窗口 2.677，gap 0.094）· 曲线 10.533 →@500 4.9742 →@4k 3.3932 →@20k 2.9936 →@32k 2.8576 →@45,777 **2.7709**；每 500 步降幅 4.5k −0.046 → 45k **−0.0009**。**事实采样翻转**：@20k "中国的首都是巴黎" / "France is Dauphin" → @44k **"中国的首都是北京" / "The capital of France is Paris"**，并自发英译中与总结。证据 = [reports/2026-11-19-day4-main140m.md](reports/2026-11-19-day4-main140m.md)（含 csv+log）· ckpt 谱系 46 件 ≈73GB。
- 疑问：①事实正确性从 20k 的"巴黎"翻转到 44k 的"北京"，是高频共现被学到还是采样随机？②门② 的"最后 10% 降幅"与恒 lr 探针读数若背离，该信哪个（口径混杂怎么在报告里表述）？③SFT 后底座的语言能力会保留多少（25% 预训练混入够不够）？——Day 6 概念题池。

**补记（同日 15:30 · SFT v1 收官 + base/SFT 对比评测）**

- 决策：①SFT v1 用预注册配置（lr 1e-4 / warmup 100 / 1 epoch over 250M / bs8×accum8）；②评测分双口径（预训练 val PPL 测语言能力保留、SFT val PPL 测指令跟随）+ 18 题规则判分测试集；③门② 正式判定维持"不加训"（最后 10% 0.0134 + 探针 0.0051 双证据）。
- 现象：SFT 1h19m26s 跑完 3,815 步，`EXIT:0`；val 1.7658@250 → 1.6217@1500 → **1.5515@3815**（末段已平，1 epoch 饱和）。**规则判分 16/18 = 89%（base 6/18 = 33%）**，但人工复读发现问题不少：①`fact-capital-cn` 通过但尾部出现"文化、艺术、交通"复读环；②`fact-months` 编造"春季月数比夏季多"；③`math-mul` 无视"只回答数字"、长篇解释；④`translate-en2zh` 用英文回答（译错方向）；⑤`en-fluency` 触发"我无法提供…"拒答模板却因含关键词被判过——**规则判分会高估质量，报告里要并列质性复核**；⑥`refuse-unknown` 编造 1958 世界杯细节（校准失败）。
- 读数：**base：预训练 PPL 15.350 / SFT PPL 9.818 / 6-18**；**sft：预训练 PPL 16.307（遗忘 +6.2%）/ SFT PPL 4.596（2.1×↓）/ 16-18 (89%)**。证据 = [reports/2026-11-19-day5-eval.md](reports/2026-11-19-day5-eval.md)（含 csv）+ [reports/2026-11-19-day5-sft-v1.log](reports/2026-11-19-day5-sft-v1.log)（SFT run 三分）· sft-v1 last.pt sha `853322df4583bfa2`。
- 疑问：①"文化/艺术/交通"复读环是 SFT 数据风格（minimind 合成数据的罗列癖）还是解码参数（greedy 更易复读）？换 top-p=0.9 会不会好？②预训练 PPL 退化 6.2%——25% 混入是否该提到 30~40%，还是接受这个遗忘换指令能力？③规则判分 89% vs 质性复核 ~60%：Day 10 的最终对比该怎么设计评分（人评 rubric + 固定题池，还是引入 LLM-as-judge）？——Day 6/10 题池。

## Day 6 · 2026-11-19 · 门② 正式判定 + 解码对照

- 决策：①**门② = 不触发，不加训 15 亿**（双证据：预注册量最后 10% 降幅 **0.0134** < 0.02~0.03；恒定 lr 探针 300 步只降 **0.0051** 且逐段衰减）——正式落档 [reports/2026-11-19-day6-gate2.md](reports/2026-11-19-day6-gate2.md)；②SFT v2 方向定为**数据侧**（补校准/拒答样本、补格式约束样本、压罗列癖），**不改解码参数**；③评测协议定档：统一 greedy（可复现）+ 并列 rep-4/distinct-2 退化指标，demo 端另用 T0.7/top-p0.9 并单独声明；④加训重开条件写成三条（SFT v2 后题库<70% 且归因底座 / 事实错误率>50% 与 token 量强相关 / Day 8-9 缓冲兑现后作对照实验）。
- 现象：**"greedy 放大复读"的假设被证伪**——换采样（T0.7/top-p0.9）rep-4 只从 0.131 降到 0.123；repetition penalty 才压得动（rp1.2→0.057、rp1.3→0.032），但 rp1.3 把题库从 16 打到 13（"H2O"被惩罚掉、en-fluency 变拒答）。**复读来自数据风格（minimind 罗列式答案），不是解码**。另有两类失败和解码无关：`refuse-unknown` 五个配置全挂（编造世界杯细节 → 校准缺失）、`math-mul` 三个配置挂（无视"只回答数字" → 格式跟随弱）。
- 读数：解码对照 5 配置（greedy 16/18 · sample 15/18 · rp1.1 15/18 · rp1.2 15/18 · rp1.3 13/18；rep-4 0.131 / 0.123 / 0.087 / 0.057 / 0.032）。证据 = [reports/2026-11-19-day6-decode.md](reports/2026-11-19-day6-decode.md) + `2026-11-19-day6-decode.csv`（90 行）。评测工具已加 `--temperature/--top-k/--top-p/--rep-penalty/--decode-name/--skip-ppl` 与字符级 distinct-2/rep-4。
- 疑问：①罗列癖要压到什么程度（降采样 vs 改写）？改写要 LLM，成本与收益怎么算？②校准样本从哪来（现有数据筛选 vs 手写 200 条）？③rp1.2 的"调参上限"读数要不要进 Day 10 主表（我倾向只作附录，避免用调参掩盖数据问题）？——Day 7 前定。

## Day 7 · 2026-11-19 · SFT 数据 v2/v2b + LoRA + GGUF/Ollama demo

- 决策：①**数据 v2** = 校准注入（1,630 唯一 ×3）+ 格式样本（989×2）+ 列表类保留 1/5（新目录 `data/sft-mix-v2/`，不动 v1；val 直接复用 v1 保证可比）；②**v2b** = 数学/推理样本豁免列表降采样（消融，不部署）；③**部署 = SFT v2 Q4_K_M**（rep-4/校准/翻译综合最佳），v2b 保留为"数学保护 ↔ 复读代价"证据；④**LoRA r=8 / 1.20%**：lr 2e-4 首跑 1000 步欠拟合 → 5e-4 全量 1 epoch；⑤**demo = stdlib 聊天页**（Gradio 镜像下载卡死 31.4MB wheel 5 分钟 0.3% CPU），Ollama 用用户级服务 11435（系统服务无模型目录写权限）。
- 现象：①**供给粗口径修正**：HANDOFF 的"列表 28.5% / 只回答 1,703"是会话级 grep；assistant 侧实测列表 34.2%（前 40 万条 46%）、"只回答"仅 46 条 → 50% 降采样不够，改 1/5；②**v2 压列表误伤数学**（math-add 15、math-mul 72），v2b 保护后修回（8/42）但 rep-4 0.117、translate/capability 回归；③**eval.py CSV 头 5 列 vs 行 8 列** → rubric 静默空表；④**GGUF 漏 q/k permute** → 前几个词正常、随后复读（F16/Q4 同病），补 `LlamaModel.permute` 后恢复；⑤**T0.7 身份采样波动**（通义千问/小玲），greedy 稳定 minimind/jingyaogong（精确 prompt 数据 82.7% MiniMind）；⑥**en-fluency 拒答**三版都在（数据侧过泛化，系统提示未修好）。
- 读数：**v2** val **1.6038**（3,815 步 / 1h19m46s / 52,825 tok/s / peak 12.05GB）· 题库 15/18 关键词（语义 16/18）· **rep-4 0.066**（v1 0.131）· 预训练 PPL 16.185（+5.4%，优于 v1 +6.2%）；**v2b** val 1.5981 · 15/18 · rep-4 0.117 · 数学修回（3+5=8、7×6=42）· 1h19m23s；**LoRA** 1.20% 可训练 · 冒烟 loss 2.7086→2.5235 · peak **9.74GB（-2.3GB）** · 2e-4 1000 步 val 1.8839、5e-4 500 步 1.8974 · ckpt 526MB + adapter 6.5MB（全参 1.65GB）；**GGUF** F16 326MB / Q4_K_M 103MB / Q8_0 173MB · raw 与 PyTorch 输出一致；**Q4 demo** identity/ML/2027 正确、math-mul 63（错）、en-fluency 拒答。
- 疑问：①r=8 LoRA 1 epoch 学不稳 chat 模板，主因是容量、步数还是 lr？②en-fluency 拒答需要多少英文正例/通用拒答降采样才能修好？③v2c "选择性数学保护"（只保护短算术/截断长步骤）能否同时保住 rep-4 <0.08？——qa-day-7 与 Day 8 题池。

**补记（同日 23:00 · LoRA 收官 + GPU demo）**

- 读数：LoRA r8 5e-4 1 epoch = **val 1.8253 / 1h17m50s / 54,124 tok/s / peak 9.74GB / ckpt 526MB + adapter 6.5MB**；eval 预训练 PPL **15.690**（比 v2 16.185 更少遗忘）、SFT PPL 6.090、题库 15/18、**rep-4 0.260**；失败 math-mul 28 / translate 英文 / refuse 编造"德国队"。结论 = 1 epoch 欠拟合，不部署；Day 8 试 r=12/2 epochs。
- 现象：LoRA 的显存/磁盘/速度/遗忘优势明确，但 SFT fit/复读/校准落后；**低秩容量在 1 epoch 内不足以同时学会模板+校准+格式**（同 step 1000：全参 1.7005 vs LoRA 1.8574）。
- GPU demo：v2 Q4 **100% GPU / 157MB**，identity 21 token 0.023s ≈ 910 tok/s、ML 23 token 0.016s ≈ 1434 tok/s；identity "MiniMind, jingyaogong"、ML 单句。

## Day 8 · 2026-11-19 晚 → 11-20 晨（提前开工）· v2c 数据 + 六版评测 + 报告开写

- 决策：①三选一按预注册默认 **v2c**（两个遗留缺陷 math/en-fluency 都在数据侧）；②选择性保护口径**先侦察后拍板**：assistant 侧全库统计（905,718 行）→ 数学列表 26,184 条按**等式行**分桶，eqrows≥3 的"练习列表"9,693 条 → 豁免口径定为 `is_math ∧ listy ∧ eqrows≥3`（v2b 全量豁免 23,253 → v2c 6,243 写入）；③英文再平衡 = 拒答保留 1/2 + 正例 1/5 选中上采样 2×；④**拒答分支置于 calib 之前**（EN_REFUSAL_RE 与 CALIB_RE 英文部分重叠——v2 里 "I can't provide…" 模板被当校准保留 1×，是泄漏源之一）；⑤部署裁决按预注册：rep-4 未过 → **保持 v2 部署**，v2c 入档能力最优消融（是否切 v2c 列待拍板）。
- 现象：①侦察三次迭代（"短算术 rows≤4"口径在 listy 池里 = 0——is_listy 本身要求 ≥5 行；改按等式行分桶才分出练习列表 vs 叙述罗列）；②**降采样作用域 = 训练集而非全库**：英文拒答 78% 集中 rows 800k-900k 桶、250M 预算 n_read≈810k 截断 → seen 只有 4,722（分桶扫描对账吻合）；③**修复翻开新伤口**：en-fluency 首次修复但该题 rep-4 0.708（英文长文复读）、translate-en2zh 回归（英答英，v2b 同病）——v2 靠"答案短"压 rep-4，v2c 敢说英文长句后复读暴露；④labels.bin 用 uint16 读出 65,436 虚惊——int16 存的 -100 ignore_index，dtype 要对上；⑤v2c@1000 val 1.7018 vs v2 同 step 1.7005——数据构成变化几乎不扰动 loss 曲线，**缺陷迁移只发生在评测维度**。
- 读数：v2c 数据 = 250,001,408 token / 监督 76.16% / 列表 10.55% / 会话 587,344 / mask 0 违规 / 构建 4.8 min；训练 = **EXIT:0 / 3,815 步 / val 1.6018 / 1h19m40s / 52,925 tok/s / peak 12.05GB**；评测 = **题库 17/18（历史最高）/ rubric 5/8（并列最高）/ rep-4 0.135 / 预训练 PPL 16.184（+5.4%）**；math-add 8 ✓ / math-mul 42 ✓（非纯数字 ⚠️）；判据 5 项过 4（rep-4 未达）。证据 = [reports/2026-11-20-day8-v2c.md](reports/2026-11-20-day8-v2c.md) · `...-day8-eval{,-rubric}.md` · `...-day8-sft-v2c.{log,csv}`；ckpt sha `6c12947bb3a56dd5`。报告开写 = [REPORT.md](REPORT.md)（11 章骨架 + §4.4 回填，Day 10 定稿）。
- 疑问：①eqrows≥3 口径对文字应用题/几何证明（无算式行）会失效——这类样本在 v2c 走 1/5 降采样，损失了什么、要不要第二轮侦察？②"对 seen 砍 50%"与"对全库砍 50%"在改 --max-tokens 时如何保持等价（规则作用域 = 训练集）？③英文正例上采样挤掉 ~3.3M token 的中文预算——中文能力有没有被稀释（预训练 PPL 持平是好兆头，但需要分语言 val 或 zh tag 分项确认）？④v2d 要同时压长答案复读 + 修 translate 方向——答案长度约束样本与翻译方向样本会不会又打架？——qa-day-8 三题 + Day 9 题池。

## 机动窗口 · 2026-11-20 · v2d（长答案复读压制 + translate 方向 + 格式补强）

- 决策：用户拍板"机动选题 = v2d 数据迭代；部署保持 v2"→ 侦察先行（两轮：池形状 + 预算截断作用域）→ 四规则（长答案 keep-den 2 / translate-upsample 3 / concise-repeat 3 / format-repeat 3），v2c 规则全沿用。**判据 = day8-review §7.1 预注册原文，跑前未改**。
- 现象：①英文长答案（≥1000 字符）在前 810k 行写入 **0 条**——en-fluency 的英文复读是中文长答案先验的跨语言泛化，英文侧砍不到、只能加正例（concise 英文组 20 条）；②translate 上采样池是"英问中答"杂样、无"翻译指令→直接译文"精确对 → 修出"英文原句+中文字词解释"（方向修了、行为没学会）；③**math-mul 退回 72**（v2b/v2c 都是 42，数学豁免量 6,264 不变、仅净增 2.3M 杂样）——组合记忆在容量边缘，小扰动就翻转；④rep-4 0.084 差 0.004 未达判据，按预注册不切换部署。
- 读数：数据 250,001,408 token / 244,142 块 / 监督 75.65% / 列表 10.15% / 会话 613,180 / mask 0 违规 / 构建 5.0 min；训练 **EXIT:0 / val 1.6059 / 1h19m44s / 52,851 tok/s / peak 12.05GB**；七版评测 = **rep-4 0.084（SFT 版最低档，v2c 0.135 砍 38%）+ rubric 6/8（历史最高）**、reason 0.728→**0.088** / en-fluency 0.708→0.371 / zh-fluency 0.516→0.303、math-add 纯数字"8"；未达 = rep-4（差 0.004）/ math-mul（72）/ translate 行为（字词解释）/ 关键词题库 15/18（两题假阴，语义 17/18）。判据 5 项过 2.5 → **不部署，v2 保持部署**。证据 = [reports/2026-11-20-v2d.md](reports/2026-11-20-v2d.md) · `...-v2d-eval{,-rubric}.md` · `...-v2d-sft.{log,csv}`；ckpt sha `fe972eed11aa599b`；图 [loss-curves-day8-v2d.png](reports/figs/loss-curves-day8-v2d.png)。
- 疑问：①"翻译指令→直接译文"精确样本扩容（~30 条×5）能否同时修 translate 行为并把 rep-4 压到 <0.08（该题 rep-4 0.293 是 v2d 最大单项）？②math-mul 组合记忆需要多强的重复才稳定（format-repeat 4~5 / ARITH 乘法表专项）？③en_flu 型在 en_helpful 分支 2× 上采样是否该降为 1×（en-fluency 0.371 顽固）？④v2e 一轮能否把四项同时收口——还是该按失败路径锁定 v2 进 Day 10？——机动窗口决策点（11-22~25 拍板）。

## 机动窗口 · 2026-11-20 · v2e 去污轮（translate 精确对 + math ×2 + en_flu 降采样 + extras 评测去污）

- 决策：用户"继续推进下一步"= 走 HANDOFF §7 默认路径第 2 轮（两轮为限的最后一轮）；预注册开工前落档（rep-4 <0.08 / translate 关键词过 / 题库关键词 ≥16 语义 ≥17 / math 8-42 / PPL ≤10%）。**开工发现评测污染**：extras 与 18 题原句存在系统性同题样本（calibration 2027 世界杯 / ARITH 7×6 / 水的化学式 / 中国的首都 / 学习编程列表 / concise ocean&北京&下雨=refuse/math-mul/fact-water/fact-capital-cn/list-3/en-flu/zh-flu/reason 原句；v2 起就有、v2d 又加 3 条）→ 本轮新增"去污"为第 1 改动面（12 处换同型变体 + `assert_no_eval_leak` 硬断言，复扫 0 撞车）。
- 现象：①去污后 calibration 1,630→1,628 / format 989→979（ARITH 排除 (3,5)/(7,6)）、extras 指纹全变——历史读数含记忆成分，**v1 的 16/18 反而是干净版**；②数学豁免 ×2（6,250→12,500 写入）把 math-mul 从 v2d 的 72 修回 42（**Day 11 修正：是窄查表，不是真泛化；且 math-add 8 仍来自残留 brevity 记忆**）；③translate 精确对 180 条（30 unique×6）修出"我热爱机器学习。"（v2d 的"字词解释"消失）；④en_flu 型 770 条降 1× 后 en-fluency rep4 0.371→0.208；⑤长答案压制延续，reason 0.095 / zh-flu 0.224 无复读。
- 读数：数据 250,001,408 token / 244,142 块 / 监督 75.99% / 列表 11.47% / 会话 595,348 / mask 0 违规 / 构建 4.8 min；训练 **EXIT:0 / val 1.6065 / 1h19m19s / 53,098 tok/s / peak 12.05GB**；八版评测 = **rep-4 0.055（全系最低）+ 题库 17/18（去污后）+ rubric 6/8 + distinct-2 0.860（最高）+ translate 真译文 + math 8/42 + PPL +5.5%** → **五项判据全过**（首个全过版本）；格式瑕疵同历史（math-mul 加粗算式 / list-3 段落式编号）。证据 = [reports/2026-11-20-v2e.md](reports/2026-11-20-v2e.md) · `...-v2e-eval{,-rubric}.md` · `...-v2e-sft.{log,csv}`；ckpt sha `984a25c4d59e36a4`；图 [loss-curves-day8-v2e.png](reports/figs/loss-curves-day8-v2e.png)。
- 疑问：①部署是否切 v2e（五项全过且全面优于 v2——rep-4/题库/math/en-fluency 全胜、PPL 持平；切换需重导 GGUF + Ollama/demo/模型卡联动，待用户拍板）；②list-3 段落式编号与 math-mul 加粗格式是否值得再做一轮（两轮为限已用完，默认不做了，留 Day 10 材料）；③评测污染的比例贡献能否量化（v2 含记忆 vs v2e 去污的差值 = 下界估计，可作报告亮点）；④qa-day-8 题 3 的"中文稀释"视角可补：去污后 zh 题全过 = 无稀释证据。——Day 9/10 题池。

## 最终阶段 · 2026-11-20 · spec 推进（部署切 v2e-q8 + 报告定稿准备）

- 决策：用户"按 spec coding 最佳实践存档计划然后推进"→ 立 `specs/2026-11-20-final-phase.md`（AC1~AC11 可验证 + T1~T4 勾选 + 回滚方案），归档后按 spec 执行。**部署从 v2-q4 切到 v2e-q8**（v2e 五项判据全过且全面优于 v2）；旧 v2 tag 全保留（回滚 <1min）。
- 现象：①**对拍方法坑**：第一轮用裸 prompt（无 chat 模板）对拍，出现"你是谁空输出 / 7×6 答成 5×6 / translate 复读"的全量表观漂移，差点误判导出链路坏——换回与 eval.py 相同的 chat 模板 + greedy 后 F16 立即 5/5 逐字一致（**对拍三同原则**入 lessons/skill）；②**Q4_K_M 量化吃掉弱记忆**：math 42→72（基座 6×12 强先验反扑）、translate "我热爱机器学习"→英文原句；Q8_0 全保住、F16 逐字保真 → 部署默认 Q8_0 + 新增"量化保真度抽检（新学能力）"验收红线；③报告 §5.1 评测污染独立成章（这是全报告最有普适价值的方法学节）。
- 读数：GGUF F16 326MB / 147 tensors（sha `eee10822`）；Ollama 三 tag（F16/Q8/Q4）；demo 切 v2e-q8 后 /health {"ok":true}、translate 返回"我喜爱机器学习。"（T0.7 采样）；AC2~AC8 命令级验收全过；commit `d0c973d`（spec）+ `5fc4d2c`（部署+报告）。
- 疑问：①LoRA r=12 一轮（~1.5h）值不值得在 Day 10 前补（G3 容量-效果曲线完整度 vs 时间）；②八版终表要不要把"含记忆/干净"做成显式列（建议做，评测污染是核心叙事）；③qa-day-2~5/7 回填的优先级（学习项，可与 Day 10 并行）。——Day 10 题池。

## Day 10 · 2026-11-20（提前 7 天）· 终检 + 收官（八版终表 / 复现走查 / LoRA r12 / REPORT 定稿）

- 决策：用户持卡"执行 §7 Day 10 终检清单（T4）"——按 §0-4 先把 §5 实际日期改为 **Day 10 = 11-20**（原定 11-27，提前 7 天），再执行 T4 五项；可选 LoRA r=12 按 HANDOFF 默认**做一轮**（补齐 G3 容量-效果曲线）；"含记忆/干净"标注列**保留**进对外版 REPORT（诚实读数解释优先于高分）。
- 现象：①**v2e 数据重建 bit-for-bit 一致**——§10 原命令重跑到 `/tmp`，4/4 sha256 与生产数据逐条相同、meta 除时间戳外全字段相同（5.0 min）→ 数据流水线确定性可复现；②**eval 逐题可复现**——§10 评测命令重跑，v2e 18/18 行**逐字节相同**（含 answer 全文）；③**部署链复验**：F16 与 PyTorch **5/5 逐字一致**、Q8_0 **4/5 逐字 + 1 同义变体**且 math 42 / translate 中文全保住；④**终检新发现**：demo 端 T0.7 下 translate 方向漂移偏高（11 次 3 次英文）→ 量化对照 T0.7 **16/20** vs T0.3 **20/20** → demo 默认温度下调 **0.7→0.3**（重启后 5/5 中文方向）；⑤**LoRA r=12**（1.79%）val **1.8054**（r8 1.8253）、rubric 4→**5/8**、rep-4 0.260→**0.249**，但距全参 1.6038 仍差 0.20——**rank↑ 不是瓶颈主因，1 epoch 内低秩适配器学不会"模板+校准+格式"**；⑥文档校准：MODEL_CARD 主体从 v2 口径全面转 v2e（架构/限制/复现段）+ README 首屏收官态 + PLAN G3~G6 全绿 + PROVENANCE 补 lora-r12 指纹；⑦**holdout 复核（30 题未见题）推翻了一个 dev 结论**：v2e 与 v2 人工复核同为 **23/30**（v2 修订版），dev 的 17 vs 15 优势不复现；`13 乘以 5` 全错（56/40/35）、`17 加 6` 答 19、`100 减 37` 答 37——**math 42 不是 extras 记忆，但也不是算术，是窄查表**；translate 只认精确句式（Knowledge is power 回英文）；**calibration 是唯一稳定泛化项**；关键词判分在 holdout 上假阳/假阴明显（moon-count 7 个假阳 / weather 2 个假阴）。
- 读数：LoRA r12 = EXIT:0 / 3,815 步 / **val 1.8054** / 1h18m49s / 53,472 tok/s / peak 9.76GB / ckpt 551MB + adapter 10MB / 预训练 PPL 15.730 / SFT PPL 5.969 / 题库 15-18 / rubric 5-8 / rep-4 0.249；终检 = 八版表 8×7+标注（对账 v2e-eval）/ 60 份 md 173 链接 **0 断链** / 证据三分齐 / REPORT FINAL + spec COMPLETED；**holdout 30 题（v2 修订版，人工复核）= base 12 / v1 21 / v2 23 / v2b 21 / v2c 21 / v2d 22 / v2e 23 / lora8 19 / lora12 19**，`13×5`/`17+6`/`100−37` 全错、translate 只认精确句式、calibration 稳定泛化；**dev 残留 2 题（`一年有几个月`/`3 加 5`），干净子集 v2e 15/16**；GPU 累计重算 **≈30.3h**、磁盘 **~145GB**。证据 = [reports/2026-11-20-day10-repro-check.md](reports/2026-11-20-day10-repro-check.md) · `...-deploy-v2e-recheck.log` · `...-lora-r12-eval{,-rubric}.md` · `...-holdout-{eval-v2,audit}.md` · `...-eval-leak-recheck.md`；ckpt sha lora-r12 `4d57b10cb7bcf169`。
- 疑问：①LoRA 2 epochs 能否把 val 从 1.80 压到 1.70 档（当前只差 0.20，值得一轮验证"epochs vs rank"谁是主因）？②demo 端 T0.3 仍带"（注：…）"尾巴——是否该在 demo 层加"只输出译文"的 system 提示，还是这属于数据/指令行为问题？③**holdout 已证 30 题能把 dev 排名打平**——要不要扩到 60~100 题、并给数学/翻译各建"多 operand/多句式"的能力型测试（不再用单题代表能力）？——qa-day-10 三题。

## Day 11 · 2026-11-20（收官后复核）· 去重假阴性修复 + holdout 双向复检

- 决策：收官后把"评测去重"沉淀成硬门时，先写独立检查器 `tools/check_eval_leak.py` 复扫历史数据；发现问题即修（断言 + 题库），**不重建 v2f、不重训**（两轮为限；残留不改变部署结论）。
- 现象：①**dev 仍残留 2 题**——`一年有几个月`（6 字）/`3 加 5 等于多少`（7 字）藏在 format brevity extras；旧 `assert_no_eval_leak` 的 `len(prompt)>=8` 守卫 + 只去空白的 norm 造成**假阴性**，v2e 的"0 撞车"是假的；②**holdout 初版 3 题近重复**——2030 世界杯/光合作用/人工智能（训练样本是评测题前缀，单向检查漏掉）+ 上海（concise「介绍一下上海」）；③数字嵌套假阳（3×3 ⊂ 13×3、3+8 ⊂ 13+8）需换题消除；④按 16 题干净子集重算：v1 14 / v2 14 / v2c 15 / **v2e 15**；⑤holdout 换题重跑 v2 后 **v2e 与 v2 人工复核同为 23/30**，dev 的 17 vs 15 优势仍不复现。
- 读数：干净子集 v2e **15/16**（原 17/18 中 2 题残留）；holdout v2 人工 = base 12 / v1 21 / v2 23 / v2b 21 / v2c 21 / v2d 22 / v2e 23 / lora8 19 / lora12 19；修复后检查器：holdout vs dev/extras/SFT 源 **0 撞车**（EXIT 0），dev vs extras **4 条命中**（EXIT 1，残留已知）；断言自测通过（已知撞车必被抓）。证据 = [reports/2026-11-20-eval-leak-recheck.md](reports/2026-11-20-eval-leak-recheck.md) · `...-holdout-eval-v2.md` · `...-holdout-audit.md` §7。
- 疑问：①要不要重建 v2f（去掉 brevity 残留 + 重训 1h20m + 重跑八版）换一个真正干净的部署模型？②holdout 扩到 60~100 题、并给数学/翻译建"多 operand/多句式"能力型测试，是否值得？③关键词表能否半自动生成（同义改写 + 人工审核），降低假阳/假阴？——后续可选方向（需新 spec）。

## Day 12 · 2026-11-21（收官后深化）· holdout 扩容 90 题 + LoRA 2ep + 分语言 val

- 决策：用户拍板"按建议执行"（HANDOFF §7 顺序 1→2→3）→ 立 spec `specs/2026-11-21-post-final-deepening.md`（预注册判据跑前冻结：数学/翻译块 ≥70%、calibration ≥5/6、v2e vs v2 差 ≥5/90、LoRA 2ep val<1.75、langval ≤1%）。执行顺序 = LoRA 先占 GPU（2.6h 长杆），出题/去重并行，评测排队。
- 现象：①出题避让靠 extras 侦察：ARITH 覆盖 2~12 全对（新题 operand ≥13 或多步/应用题）、calibration 年份 2027~2042 全占（用 2044+）、concise 50 题面清单——首轮检查器仍抓 23 处撞车（fact-mountain ×8 / identity-intro ×4 在 SFT 源高频；translate 2 条与 extras 同句），换 8 题后 EXIT 0；②数学换序探针只能用"13×3 假阳教训"的镜像（3×13=39）——两位数×个位数乘法都会触发数字嵌套假阳（16×3 ⊃ 6×3），可用对极窄；③langval 首跑 off-by-one 崩（末块 y 切片越界），按 eval.py 同款 (len−1)//block 修；④**90 题人工校准把 30 题时代的"无显著差异"翻了案**：v2e 53 vs v2 47（+6 达预注册阈值），关键词原始分持平（59=59）纯属 v2 假阳多 9 个（复读碰词）——30 题 CI ±4 掩盖了真实差距；⑤lora12-2ep val 1.7921（1ep→2ep 只买 −0.013，与 rank 的 −0.020 同量级）——两个维度单独加码边际收益都枯竭，但能力维度 42→48 有实效；⑥lightspeed 题 **9/10 版本答对 299,792** 而关键词全灭（expect 表缺数字写法收口）——最大一处系统性假阴，"知识其实掌握了、分数说没有"。
- 读数：题库 `tests-holdout-v3.json` 90 题（sha `2539aa2b`，v3↔dev 0 撞车）；三块判据 = **数学 ✗（0~3/14）· 翻译 ✗（0~5/14）· calibration ✓（v2/v2d/v2e 6/6，v2b 5/6）**；v2e vs v2 = +6 ✓（贴阈值）；LoRA 2ep = EXIT:0 / val 1.7921 / holdout 人工 48（+6 vs 1ep）/ rep-4 0.176 / 2h37m / peak 9.76GB；langval = 英文上采样对 zh sup ±0.15% **无稀释**（zh all v2e 反而 −8.8%）。校准分总表：base 12 / v1 47 / v2 47 / v2b 44 / v2c 45 / v2d 48 / **v2e 53** / lora8 43 / lora12 42 / lora12-2ep 48。证据 = [reports/2026-11-21-holdout-audit-v3.md](reports/2026-11-21-holdout-audit-v3.md) · `...-holdout-eval-v3.{md,csv}` · [2026-11-21-lora-r12-2ep.md](reports/2026-11-21-lora-r12-2ep.md) · [2026-11-21-langval.md](reports/2026-11-21-langval.md)。
- 疑问：①v2e 的校准优势能否在 150~200 题 + 独立复核者（非同一 agent）下复现（+6 贴阈值 + 同 style 偏差）；②翻译的 zh2en 简单句泛化（hometown/learning/book/music 9/10）与 en2zh 全灭的不对称——是 extras 双向配比（15+15）问题还是语言先验问题；③关键词 expect 表的"数字写法收口"（299,792 vs 30万）能否半自动生成（同义改写 + 人工审核）——后续可选（需新 spec）。

## Release Phase 1 · 2026-11-21 · 公开发布准备（License/README/模型导出/CI）

- 决策：用户拍板"对外发布"→ 立 spec [`specs/2026-11-21-public-release.md`](specs/2026-11-21-public-release.md)（Phase 1 发布阻断项 / Phase 2 可信度 / Phase 3 打包；**本阶段不做任何公网推送/上传**）。发布定位 = "完整可复现的案例研究 + 诚实的评测方法学"，不是"140M 挑战开源大模型"。
- 现象：①体检四类阻断：无 LICENSE、README 是内部日志式、模型无下载入口、900 格人工分未落盘；②HF 导出加 `--dtype fp16 --tie-embeddings` → 137,847,552 参数 / 262.9 MiB，config 含 chat_template，**PyTorch vs HF greedy 30/30 逐 token 一致**（fp32 对照版也一致）；③Q8_0 独立 GGUF 从 Ollama blob 复制（`sha256-8b64…`），`GGUFReader` 确认 `file_type=7` / 147 tensors（114 Q8_0 + 33 F32），Ollama 从独立文件建模型输出与部署 tag **逐字一致**（`I love machine learning.`）；④轻量 CI：题库 schema、去重检查器阳性对照（6 字短 prompt 必被抓）、holdout v3 0 撞车、11 份读者面文档 0 断链、`compileall` 全过；⑤旧 README 归档到 `docs/internal/status-log-2026-11-21.md`，HANDOFF/PLAN/LAB_NOTEBOOK/SKILL 加"过程记录"banner；⑥时间口径统一为"2026-11-18 08:08 → 11-20 20:10 约 60 小时"（"实际 8 天"与 3 个日历日矛盾，公开稿不再用）。
- 读数：HF fp16 `model.safetensors` sha `7d1c2f0c…` / 262.9 MiB；Q8 GGUF sha `8b64b668…` / 174 MB；F16 GGUF sha `eee10822…` / 326 MB；`RELEASE_SHA256SUMS` 入库。CI 四项 EXIT 0。
- 疑问：①McNemar/CI 与 900 格标签（Phase 2）会把"+6"的措辞改到哪一档（p>0.05 时只能写"达到预注册阈值"）？②独立复核 30~50 题的 kappa 会落在哪档？③v2f 是否值得在 v1.0 后做（重训会动 +6，不能阻塞首发）？——Phase 2 输入。

<!-- 模板（复制使用）：
## Day N · YYYY-MM-DD · <主题>
- 决策：…（含 D-xx 编号引用）
- 现象：…（报错原文贴 reports/，笔记里写链接）
- 读数：…（吞吐 / loss / 评测分）
- 疑问：…（当晚三道概念检验题的来源池）
-->
