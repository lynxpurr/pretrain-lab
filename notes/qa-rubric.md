# qa 评分要点（qa-day-2 / 3 / 4 / 5 / 7 / 10 · 18 题 + 加餐）

> **用法**：先在自己的 `qa-day-N.md` 里**自答**（不看本文件），写完再逐题对照本文件的"判分要点"与"常见错误"，给自己打 ✅/⚠️/❌。⚠️/❌ 回出处补课。
> **本文件只给评分要点，不给完整范文**——学习价值在"先自己组织答案"。若只想快速收口，可让 agent 按 `qa-day-8.md` 模式代写预答卡（需明确授权）。
> 判分口径：**要点覆盖 ≥3/4 且无事实错误 = ✅**；覆盖 2/4 或有小错 = ⚠️；<2/4 或方向错 = ❌。

## qa-day-2 · tokenizer / 锚 / 数据划分

### 题 1 · 32k BPE 压缩率账
**判分要点**
- `chars/token` = 每 token 覆盖的字符数（语言内压缩率）；`bytes/token` = 每 token 覆盖的字节数（跨语言可比）。
- 词表 5× 但 token 只降 ~28~30%：BPE merge 边际收益递减（高频词在 6.4k 已基本成词，新增词表吃的是低频子词/英文碎片）。
- en 的 bytes/token ≈ chars/token（ASCII 1 字节/字符）；zh 的 bytes/token 4.974 ≫ chars/token 1.841（UTF-8 CJK 3 字节/字符 + 混排标点/英文）。
**常见错误**：把 chars/token 当"字节压缩率"；解释成"词表越大越好"而忽略边际递减。
**出处**：`reports/2026-11-18-day2-tokenizer.md` §2 · `data/tokenizer-32k/meta.json`

### 题 2 · ln(V) 锚的换轨
**判分要点**
- 随机初始化 logits≈0 → softmax 均匀 → CE = ln(V)；32k → 10.3734。
- 明显**偏低**：先查"见过答案"——labels 右移/配对错位、重复数据、mask 泄漏。
- 明显**偏高**：先查 id 与 vocab 不一致——值域越界、special token id、取批错位；容差随规模放宽（22M +0.06 → 140M +0.17）。
**常见错误**：把偏低归因于"学习率高"；忘记 anchor 要在微步 1 且同数据分布下测。
**出处**：`notes/lessons.md` Day 0~1 第三条 · `reports/2026-11-18-day2-smoke.md`

### 题 3 · 混配比与 val 划分
**判分要点**
- 按 token 计数：压缩率随语言/内容变，按字节/文档数会偏。
- 累计缺口调度：每步取"当前占比低于目标"的语言，使 en:zh 收敛 6:4（偏差 <0.01%）。
- `hash%500` 文档级 val：防泄漏、可复现、不依赖读取顺序；头部切分有分布偏差，随机行切分破坏文档完整性。
- 多余 val 候选丢弃：val 必须固定、留出；塞回 train = 泄漏，扩 val = 改变评测口径。
**常见错误**：说"按文件大小 6:4 就行"；把 val 候选回收进训练。
**出处**：`tools/build_shards.py` 注释 · `reports/2026-11-18-day2-shards.md` §1~2

### 加餐 · decode 自检坑
**要点**：`decode()` 默认 `skip_special_tokens=True` → 特殊 token 被吞；往返自检要显式 `False`；文本里字面量 `<|endoftext|>` 可能被编码成 special id 再被吞 → 断言失败；探针拆"普通文本 + specials"两段。

## qa-day-3 · 显存 / 续训 / 吞吐

### 题 1 · 16GB 显存里谁是大头
**判分要点**
- CE 三份同尺寸张量：bf16 logits（B·T·V·2）+ 内部升 fp32（B·T·V·4）+ 反向保留的 log_softmax（B·T·V·4）。
- bs16：16×1024×32000 = 524.3M 元素 → 1.05GB + 2.10GB + 2.10GB ≈ **5.25GB**。
- 梯度累积只在 batch 维重复，**摊不薄单个 micro-batch 内的 logits 峰值**（CE 逐 token 独立，全部位置一次前向就产生）。
**常见错误**：只算"参数+优化器 1.65GB"；以为 accum 能降 CE 峰值。
**出处**：`reports/2026-11-18-day3-framework.md` §3 · `...-memsweep.log`

### 题 2 · 续训恢复什么
**判分要点**
- 三路 RNG 各管一件事：`data` = 下一批取哪条数据；`torch` = dropout/采样等 CPU 侧随机；`cuda` = GPU kernel 随机。
- 少存 data RNG → 数据顺序变 → 训练轨迹/loss 曲线变；val 因固定窗口+eval 模式+同权重仍一致。
- step 40 val 一字不差 = 确定性；step 41 train loss 不同 = "分布相同 ≠ 序列相同"。
**常见错误**：以为"同一份数据、同一 seed"就够了；忽略 `tokens_seen == step × tokens_per_step` 对账。
**出处**：`tools/train.py` 续训段 · `notes/lessons.md` Day 3 第一条

### 题 3 · 140M 为何比折算更快
**判分要点**
- 6N 只算 Transformer 主体，漏掉 **lm_head + softmax 的每 token 成本 ~V·d**（与深度无关）。
- 50M 的 lm_head 占参数 ~37%、140M 只 ~18% → 6N 低估 50M 的实际 FLOPs。
- 另：bs16 vs bs8、SDPA 在 T=1024 的利用率差异；140M 每 FLOP 的 GPU 效率更高。
**常见错误**：把差异全归因于"大模型更吃满 GPU"；忘记词表投影项。
**出处**：`reports/2026-11-18-day3-50m-30min.md` §4 · `...-140m-probe.md` §3

### 加餐 · torch.compile 慢 13×
**要点**：sm_120/Blackwell inductor 后端覆盖不足、attention 融合未命中、动态 shape 重编译、编译时间摊到短跑；证伪实验 = 同配置 ≥40 步、预热 20 步、同 seed 同数据、只计纯训练 tok/s。

## qa-day-4 · SFT 标签 / 块 / 混入

### 题 1 · 配对 labels 与 ignore_index
**判分要点**
- 配对布局（`labels[i]` = 位置 i 该预测的 token）把"哪些位置算 loss"交给数据侧，比预训练右移更可控。
- `ignore_index=-100` 同时跳过 loss 与梯度；分母 = **非 -100 位置数**（不是全部位置）。
- 不 mask user 段 → 学"复述提问"和"从问句末尾直接抄答案开头"，且 loss 被无信息位置稀释。
**常见错误**：说"分母是 B×T"；把 mask 只当"省算力"。
**出处**：`tools/build_sft.py` `_flush`/`conversation_segments` · `reports/2026-11-18-day3-framework.md` §1

### 题 2 · 会话不跨块
**判分要点**
- 跨块后半段缺 `<|im_start|>` 头 → 在无上下文 fragment 上算 loss（学坏分布）。
- 块尾 label 指向下一块 token = 教"块边界任意跳转"，且目标不在本块视野、无法段级断言校验。
- 装不下补 EOS 收块：每块自包含、可验证。
**常见错误**：只算"浪费 13% token"的账，忽略语义/校验代价。
**出处**：`notes/lessons.md` Day 4 第二条 · `BlockWriter.add_conversation`

### 题 3 · 25% 预训练混入
**判分要点**
- 纯 SFT 只最小化问答对 CE → 分布收窄到 SFT 说话方式，OOD 事实更易编。
- 混入 = 多任务目标 `λ·CE_SFT + (1−λ)·CE_LM`，把参数拉向预训练解（正则），保住语言建模。
- 块级 vs 样本级：期望相同、梯度方差不同（块内不混 → 方差更大）。
**常见错误**：说"混入是为了多学知识"（主作用是正则/防遗忘）。
**出处**：PLAN §5 风险表 · `data/sft-mix/meta.json` `pretrain_mix`

### 加餐 · eval bs16 峰值不降
**要点**：eval 无梯度/优化器态，但常驻 = 参数 fp32 2.2GB + CE 三份副本（bs16 ≈5.25GB）；forward-only 激活在 `no_grad` 下逐层释放；训练 bs8 的激活 ~3GB + CE ~2.6GB + 参数 2.2GB ≈ 同量级 → **峰值由与 batch 线性的 CE 副本决定，不由激活决定**。

## qa-day-5 · 评测 / 解码 / 遗忘

### 题 1 · 关键词判分骗人
**判分要点**
- 只测"是否提到"，不测正确性/格式/是否复读。
- 三种情形：拒答模板里含关键词、复读环里含关键词、无视格式但内容含关键词。
- 补法：distinct-2/rep-4、最长重复片段、格式断言、人工 rubric 抽样、（可选）LLM-as-judge 校准。
**常见错误**：只加更多关键词；用总分替代质性复核。
**出处**：`reports/2026-11-19-day5-eval.md` · `notes/lessons.md` Day 5 第一条

### 题 2 · greedy vs 采样
**判分要点**
- greedy 每步 argmax，一旦进入高概率循环永不逃出；采样随机性可"跳出来"。
- T 缩放 logits（高温 flatten/低温 sharpen）、top-k 截断候选、top-p 核采样、rep penalty 压已出现 token（用事实换多样性）。
- 公平协议：三版用**同一套解码参数**（本项目 = greedy T0/top-k0/top-p1/rep1），参数写进报告；demo 参数单独声明。
**常见错误**：给不同版本用不同解码；把 demo 的 T0.3 混进对比表。
**出处**：`tools/eval.py` `chat()` · `tools/model.py` `generate()` · lessons Day 5 第二条

### 题 3 · 遗忘度量与权衡
**判分要点**
- SFT 把参数拉向 SFT 分布 → 指令↑、预训练 PPL↑；25% 混入 = 多任务正则。
- 三条路：提高混入比例（SFT 收敛慢/指令可能降）、降 lr/减步数（欠拟合）、LoRA 只动低秩（容量受限，val 1.8253）。
- 判据：预训练 PPL 退化 ≤10%（v1 +6.2% 可接受）。
**常见错误**：只看 SFT val 判断遗忘；把"遗忘"与"过拟合"混为一谈。
**出处**：`reports/2026-11-19-day5-eval.md` 汇总表 · PLAN §5

### 加餐 · 探针外推
**要点**：探针加载模型但**重置 Adam 动量** → 前几百步有效步长偏大且衰减；data RNG 也换了；不能线性外推。正确用法 = 当"上界"，与主训练同 lr 区间实测降幅并列（0.0134 vs 0.0051）。

## qa-day-7 · 数据保护 / GGUF / 判分

### 题 1 · 列表降采样误伤数学
**判分要点**
- 长数学题解天然是编号步骤 → "列表"表面格式与"数学能力"高度重合。
- 按文本形状分类 ≠ 按能力分类；能力域保护要问"这条样本靠什么特征教这个能力"。
- v2b：用户句含数学关键词+数字、或答案含公式/等式 → 豁免；v2c 进一步收窄为 assistant 等式行 ≥3 的练习列表（豁免 6,243）。
- 验证：math-add/math-mul 读数 + 列表占比 ≤15% + 复读指标不被抬回。
**常见错误**：用"数学关键词"一刀切（v2b rep-4 0.117 的代价）；忘记验证相邻能力域。
**出处**：`notes/lessons.md` Day 7 第一条 · `tools/build_sft_v2.py` `is_math()`/`EQ_ROW_RE`

### 题 2 · GGUF q/k permute
**判分要点**
- llama.cpp 的 `LlamaModel.permute` 按 head 把 `[n_head, 2, head_dim/2, in]` `swapaxes(1,2)`，对齐 half-split RoPE 的 q/k 维度顺序。
- 只重排 q/k 权重行的 head 内顺序；embedding/FFN 无关 → 症状只在注意力（前几词正常、随后复读）。
**常见错误**：以为 permute 是"量化"的一部分；忘记 tokenizer/模板也要同源。
**出处**：`tools/export_gguf.py` `permute_qk` · llama.cpp `conversion/llama.py` L177-191 · `reports/2026-11-19-day7-deploy.md`

### 题 3 · 关键词同时假阳/假阴
**判分要点**
- 关键词只测"提到"，不测"正确/编造/格式"。
- 假阴：正确答案缺 `expect_any` 里的词（"没有冠军"）；假阳：编造答案里含关键词（"没有官方…1958"）。
- rubric 断言：**承认不知道/纠正前提** 且 **无编造年份**；关键词分与 rubric 分并列报告，不互相替代。
**常见错误**：用 rubric 分覆盖关键词分（或反之）；只修 `expect_any` 不查编造。
**出处**：`tools/eval_format.py` · `reports/2026-11-19-day7-eval-rubric-v2.md` · lessons Day 7 第四/五条

### 加餐 · CSV schema 静默错列
**要点**：`DictReader` 按表头映射，多出的列进 `None` 键；不会报错、只会"看起来没数据"。自检 = `head -1` + 每行字段数断言 + 关键列取值域检查（如 `pass ∈ {0,1}`）。

## qa-day-10 · 终检方法学

### 题 1 · bit-for-bit 证明什么、不证明什么
**判分要点**
- 证明**流水线确定性**：同输入 + 固定 seed/遍历顺序/hash 函数 → 同输出（4/4 sha256 + meta 全字段）。
- **不证明跨环境可移植**：换 tokenizer 文件、Python/依赖版本、机器仍可能变；所以要对账"输入指纹"。
- 三样确定项：随机种子、文件遍历顺序、hash 函数（`blake2b` 而非 Python 内置 `hash()`——后者受 `PYTHONHASHSEED` 随机化）。
**常见错误**：把"重建 sha 相同"当成"任何机器都能复现"；用 Python `hash()` 做数据划分。
**出处**：`reports/2026-11-20-day10-repro-check.md` §1 · `tools/build_sft_v2.py` `blake2b64`

### 题 2 · 量化抽检"新学能力"
**判分要点**
- 量化噪声会冲掉**弱记忆**（新学、与基座强先验冲突）：42→72、中文翻译→英文原句。
- v2 的 Q4"忠实"是假象：它的错误答案 72 本身就是强先验，量化冲不掉。
- 验收 = F16 逐字对拍（链路）+ 目标量化档的**新学能力抽检**（math 42 / translate 中文）；"能加载/能对话/identity 对"不够。
**常见错误**：只对拍强先验题；用 Q4 体积小作为选档理由。
**出处**：`reports/2026-11-20-deploy-v2e.md` §2/§3 · `reports/2026-11-20-deploy-v2e-recheck.log`

### 题 3 · "含记忆/干净"标注
**判分要点**
- 去掉标注会得出两个错误结论：①"v2c 17/18 = v2e 17/18，所以 v2c 一样好"（v2c 含记忆）；②"v2 15/18 < v1 16/18，所以数据迭代退步"（v2 的 15 也含记忆，且 v1 无 extras 才是干净基线）。
- 保留标注不是"贬低 v2c"：它说明该分数**不可与干净读数横比**；v2c 的价值在"能力域保护"的机制验证。
- 去污前后差值只是记忆贡献的**下界**（v2 vs v2e 同时改了多件事，不能把差值全归给记忆）。
**常见错误**：把不同"读数性质"的分数直接排序；把去污差值当精确的记忆占比。
**出处**：`REPORT.md` §5.1/§4.7 · `reports/2026-11-20-v2e.md` §1