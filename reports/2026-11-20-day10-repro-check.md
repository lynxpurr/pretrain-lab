# Day 10 终检 · 复现走查与部署复验（2026-11-20）

> 触发：T4.4「§10 复现命令与实际产物一致（v2e build/sft/eval/deploy 四段），至少 dry-run 关键路径」。本文件 = 终检的复现证据（只增不改）；命令原文 = [REPORT.md](../REPORT.md) §10。

## 1. 数据构建段（v2e）— bit-for-bit 复现 ✅

**命令**（与 REPORT §10 逐字相同，仅把输出改到 `/tmp` 以免动生产数据）：

```bash
.venv-pre/bin/python -I tools/build_sft_v2.py --listy-keep-den 5 --protect-math-short \
  --en-refusal-keep-den 2 --en-helpful-upsample 5 --concise-repeat 3 --translate-upsample 3 \
  --long-answer-keep-den 2 --format-repeat 3 --translate-ex-repeat 6 --math-upsample 2 \
  --en-flu-no-upsample --out-dir /tmp/sft-mix-v2e-rebuild
```

- 结果：`EXIT:0` / **5.0 min** / 250,001,408 token / 244,142 blocks / 监督 75.99% / 列表 11.47% / 会话 595,348 / mask 自检 300 块 2,959 段 **0 违规**。
- **4/4 sha256 与生产数据逐条相同**：

| 文件 | sha256 | 一致 |
|---|---|---|
| train.bin | `d78139af58cdd2a36a8b0d3a0188923c1c7f6ca55cb4a5cf94a3077d448db013` | ✅ |
| train.labels.bin | `50bf76e58dbab665ff1901746af06c6396471d36d5bebf431b855dfa630cfda5` | ✅ |
| val.bin | `8287b49028dd2f584146c01c0bd899228ef6d6970e54daa4c41e91b4feac2b3a` | ✅ |
| val.labels.bin | `1a5184449637176ba858e6ae295b328d035dd0ce356577d550f11de6e484162b` | ✅ |

- `meta.json` 除 `elapsed_s`/`created`（时间戳）外**全字段相同**（含所有 mined 计数与 listy_ratio_after=0.1147）。
- 判定：v2e 流水线**确定性可复现**（随机种子/文件遍历/hash 函数均为脚本内固定项）；`assert_no_eval_leak` 本次构建 0 触发。

## 2. SFT 训练段（v2e）

- 生产命令已留完整证据：`data/sft-mix-v2e` + `--init-from out/main140m/last.pt` → **EXIT:0 / 3,815 步 / val 1.6065 / 1h19m19s / 53,098 tok/s / peak 12.05GB**（`reports/2026-11-20-v2e-sft.{log,csv}`）。
- 今日 LoRA r=12（同工具同数据，`--lora-rank 12 --lora-alpha 24`）再次走通该路径：`EXIT:0`，且 `[anchor] micro-step 1 loss 2.7706` 与 r=8（Day 7）**逐字相同**——底座载入 + 数据取批 + 初始 loss 三项可复现。

## 3. 评测段（v2e）— 逐题逐字复现 ✅

**命令**（REPORT §10 原文）：

```bash
.venv-pre/bin/python -I tools/eval.py --ckpt base=out/main140m/last.pt \
  --ckpt v2e=out/sft-v2e/last.pt --out reports/2026-11-20-day10-eval-recheck.md
```

- 汇总：base `15.350 / 9.818 / 6-18 / d2 0.232 / rep4 0.727`；v2e `16.192 / 4.847 / 17-18 / d2 0.860 / rep4 0.055`。
- 与 `reports/2026-11-20-v2e-eval.csv` 对账：**v2e 18/18 行逐字节相同**（pass/distinct2/rep4/answer 全字段）→ greedy + 固定 seed 的评测可复现。
- rubric 复跑：`tools/eval_format.py` 对 v2e = **6/8**（与 `2026-11-20-v2e-eval-rubric.md` 一致）。

## 4. 部署段（v2e-q8）— 三同对拍 + 新学能力抽检 ✅

证据全文 = [2026-11-20-deploy-v2e-recheck.log](2026-11-20-deploy-v2e-recheck.log)：

| 项 | 读数 |
|---|---|
| GGUF F16 | 326,240,864 bytes · sha256[16] `eee108223b9c0278`（与 PROVENANCE 一致） |
| Ollama tags | `pretrain-lab-sft-v2e`（326MB）/ `-q8`（173MB，部署默认）/ `-q4`（103MB，不保真） |
| PyTorch vs **F16** | **5/5 逐字一致**（链路忠实） |
| PyTorch vs **Q8_0** | **4/5 逐字**，1 条同义变体（def-ml）；**新学能力全保住**：math-mul = **42**、translate = **我热爱机器学习。** |
| demo `/health` | `{"ok":true}` |

## 5. 终检新发现与修正（demo 采样温度）

- 复验发现 **demo 端 T0.7 的 translate 方向漂移偏高**：11 次抽检 3 次输出英文原句（≈27%）；量化对照（同 prompt / top_p0.9 / 各 20 次）：**T0.7 = 16/20 中文方向，T0.3 = 20/20**。
- 修正：`tools/app_stdlib.py` 默认温度 **0.7 → 0.3**（已重启 demo，抽检 5/5 中文方向）。
- 判定：这是**解码方差**而非部署链问题——验收口径仍是三同 greedy（F16 5/5、Q8 4/5）；demo 端 T0.3 作为展示参数单独声明（REPORT §4.0/HANDOFF §4 已同步）。

## 6. 结论

**§10 四段命令全部与实际产物一致，且关键路径可复现**：数据构建 bit-for-bit（4/4 sha256）、评测逐题逐字（18/18 行）、部署链路忠实（F16 5/5）且新学能力在 Q8 下保住。唯一修正 = demo 展示温度 T0.7→0.3。**T4.4 ✅**