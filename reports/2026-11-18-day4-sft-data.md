# Day 4 · SFT 数据构建 + `tools/sft.py` 自检

> 2026-11-18 · 证据 = 本件 + `2026-11-18-day4-sft-build.csv`（构建进度）+ `2026-11-18-day4-sft-build.log`（原始 stdout）
> 关联：主训练起跑读数见 [2026-11-18-day3-140m-probe.md](2026-11-18-day3-140m-probe.md) §6（定档命令）；数据指纹 `data/sft-mix/SHA256SUMS` + PROVENANCE

## 1. SFT 数据集 `data/sft-mix/`（`tools/build_sft.py`）

| 项 | 值 |
|---|---|
| 源 | `data/raw/minimind_dataset/sft_t2t_mini.jsonl`（905,718 条 conversations） |
| 模板 | `<\|im_start\|>{role}\n{content}<\|im_end\|>\n`（对齐 minimind 原格式；本仓 tokenizer specials：endoftext=0 / im_start=1 / im_end=2） |
| 规模 | **250,001,408 token** = 244,142 块 × 1024 · 404,210 条对话 · 监督 token 195,371,224（**78.15%**） |
| 混入 | **25% 预训练块**（每 4 块 1 块，从 `data/shards` 随机窗口，mask 全 1）——PLAN 风险表防幻觉要求 |
| val | **2,001,920 token**（4,281 条对话；`blake2b64(line) % 100 == 0` 文档级留出，纯 SFT、无预训练混入） |
| 构建 | **4.0 min**（CPU 单进程）· 长会话截断 1,012 条（0.11%，>1024 token）· 采样自检 30 例：分段编码 == 整段编码 |
| 文件 | `train.bin`(uint16) + `train.labels.bin`(int16, -100=mask) + `val.bin` + `val.labels.bin` + `meta.json` + `SHA256SUMS` |

**mask 语义（label 是"该位置应预测的 token"，不是该位置本身的 token）**：

- `user` / `system` 段：label 全 `-100`（模型不学复述提问）；
- `assistant` 段：从 header 末 token（`"\n"`）到正文末 token 参与——右移后恰好训练 `content[0] … <|im_end|>`；
- 块尾：label 恒 `-100`（跨块不预测）；块内填充 EOS 不参与 loss；
- **验收断言（已跑）**：150 段（75 assistant）逐段枚举 0 违规——user 段全 -100 / assistant 段 `label[i]==token[i+1]` / assistant 段末 `label==2`。

**打包策略**：会话不跨块——装不下就补 EOS 收块、下块重开（填充 ~13%）。第一版按流硬切 1024 会把对话切断（后半段缺 `<|im_start|>` 头），已改。

## 2. `tools/sft.py`（与 `train.py` 同源）

| 项 | 实现 |
|---|---|
| 底座 | `--init-from out/main140m/last.pt`：读 ckpt 的 config 建模型 → `load_state_dict`（**只载 model，不载 optimizer**，SFT 重开优化器）；`--init-from none` = 随机小模型（管线自检） |
| 数据 | `SFTPairedData`：同偏移读 tokens + labels；`FixedSFTVal`：块编号固定种子、非重叠（跨 step 可比） |
| 损失 | `F.cross_entropy(..., ignore_index=-100)`——`model.py` forward 新增 `ignore_index` 参数（默认 -100，预训练行为不变） |
| 采样 | chat 模板 prompt → 生成 → 在 `<|im_end|>` 截断；`decode(skip_special_tokens=False)` |
| 纪律 | 复用 `train.py` 的 `lr_at` / `make_optimizer` / `fmt_dur`；`EXIT:0/1` 标记、csv+log、`--resume auto`、`--max-minutes` |

**自检结果**：

| 检查 | 结果 |
|---|---|
| CPU 随机小模型（d128/L2）3 步 | `EXIT:0` · anchor **10.3615** ≈ ln(32000)=10.3735（随机初始化锚定正常）· 首 micro-batch 监督占比 70.51% · 采样链路通（乱码符合随机模型预期） |
| CPU 载入真底座（`out/day3-50m/last.pt`，d576/L8/H9）1 步 | `EXIT:0` · config 校验通过 · **step 1 loss 4.6877 / val 4.3952**（50M 底座在 assistant token 上的真实读数）· 4.9s |
| GPU 冒烟（140M 底座 + bs8） | **待主训练收官后**（现 GPU 仅余 ~2.8GB）；预计 50 步 @ ~52k tok/s = 1 min |

## 3. 复现命令

```bash
cd /home/zenz/projects/pretrain-lab
# 构建（4 min，CPU）
.venv-pre/bin/python -I tools/build_sft.py --max-tokens 250e6 --val-tokens 2e6 --pretrain-ratio 0.25 \
  2>&1 | tee logs/day4-sft-build.log
# 自检（CPU，随机小模型）
.venv-pre/bin/python -I tools/sft.py --init-from none --device cpu --max-steps 3 --batch-size 2
# 正式 SFT v1（主训练收官后）
.venv-pre/bin/python -I tools/sft.py --init-from out/main140m/last.pt --run-name sft-v1 \
  --batch-size 8 --grad-accum 8 --base-lr 1e-4 --warmup 100 --target-tokens 250e6
```

## 4. 已知限制

- SFT 的 `val` 是纯 SFT 分布，train loss 里混了 25% 预训练块——两者不同口径，比较时只看 val。
- 模板不含 system prompt（本数据集无 system 消息；若后续加系统提示，需重跑构建）。
- `reasoning_content` 字段未使用（本仓 140M 不做思维链；数据里该字段只出现在部分 assistant 消息中）。
- 长会话截断会切掉尾部（1,012 条，0.11%）——若 SFT 后出现"答一半"，先查这批样本。