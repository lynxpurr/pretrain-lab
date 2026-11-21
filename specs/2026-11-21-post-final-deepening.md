# SPEC · 收官后深化 — holdout 扩容 + LoRA 2 epochs + 分语言 val

- **Status**: **COMPLETED**（2026-11-21 立，同日 T1~T6 全部完成——验收记录见 §11）
- **Owner**: 用户拍板（2026-11-21："按照建议执行，启动"——按 HANDOFF §7 建议顺序 1→2→3）· agent 执行
- **Scope 一句话**：在不动部署（v2e-q8）与不动八版可比性的前提下，做三项可选深化：①holdout 扩到 90 题并给数学/翻译建能力型块（检验"单题修复"假设）；②LoRA r=12 2 epochs（归因 epochs vs rank）；③分语言 val（收口"英文上采样稀释中文"疑问）。**全部为证据补强，不触发部署切换。**

## 1. Context（现状，事实源）

- 项目收官（Day 10 提前 7 天）+ Day 11 收官后复核完成；部署 = `pretrain-lab-sft-v2e-q8`（不动）。
- holdout v2（30 题，sha `e6e31aaa`）人工复核：v2e 与 v2 同 23/30，dev 排名不复现；math 未见组合全错（13×5 答 56/40/35、17+6 答 19）、translate 只认精确句式、calibration 稳定泛化。**30 题样本小（95% CI ≈ ±4 题），数学/翻译只有单题或 3 题，不足以代表能力**。
- LoRA r=8/r12 均 1 epoch 欠拟合（val 1.8253 / 1.8054，距全参 1.6038 差 0.20）；rank↑ 只补 0.02——**2 epochs 未验证**。
- "英文正例上采样挤掉中文预算"的疑问（Day 8 qa-day-8 题 3）只有"预训练 PPL 持平"的间接证据，无分语言读数。
- 工具已就绪：`tools/check_eval_leak.py`（双向三层 + 自测）、`tools/eval.py --tests`（自动出 md+csv）、`tools/sft.py --lora-*`（数据 = 随机偏移采样，`--target-tokens 500e6` 即等期望 2× 覆盖）。

## 2. Objective

1. **holdout v3 = 90 题**（v2 的 30 题 + 60 新题），数学块 14 题 / 翻译块 14 题 / calibration 块 6 题，其余 tag 同型变体扩容；十版（base/v1/v2/v2b/v2c/v2d/v2e/lora8/lora12/lora12-2ep）greedy 重跑 + 人工复核，判定三块预注册判据。
2. **LoRA r=12 2 epochs**（v2 数据、lr 5e-4、唯一变量 = epochs），归因"epochs vs rank 谁是 1 epoch 欠拟合主因"。
3. **分语言 val**：SFT val（v1 val，各版共用）按中/英分块，算 {base, v1, v2, v2c, v2d, v2e} 的 zh/en PPL 分项。

## 3. Non-goals（明确不做）

- 不重建 v2f、不重训全参 SFT、不做 DPO（两轮为限纪律 + HANDOFF §7 不建议）。
- 不切换部署（v2e-q8 保持；若新证据支持切换，另行立 spec 拍板）。
- 不修改 dev 18 题 / holdout v2 30 题 / 八版任何历史读数（只增不改：新题库 = 新文件）。
- 不改 tokenizer / 预训练底座 / 评测协议口径（greedy + 关键词 + 人工复核）。

## 4. Acceptance Criteria（可验证，逐条带验证命令）

| # | 验收标准 | 验证命令/判据 |
|---|---|---|
| AC1 | 新题库 `data/eval/tests-holdout-v3.json`：90 题（30 旧 + 60 新）/ 13 tag 全覆盖 / math ≥14 / translate ≥14 / calibration ≥6；v2 原件 `tests-holdout.json` 不动 | `python3 -c "import json;print(len(json.load(open('data/eval/tests-holdout-v3.json'))))"` = 90；`sha256sum data/eval/tests-holdout.json` 仍为 `e6e31aaa` 前缀 |
| AC2 | v3 双向三层去重 0 撞车（含 SFT 源 905,718 行） | `.venv-pre/bin/python -I tools/check_eval_leak.py --eval data/eval/tests-holdout-v3.json --extra-dir data/sft-extra-v2 --sft-source data/raw/minimind_dataset/sft_t2t_mini.jsonl` → EXIT 0 |
| AC3 | v3 指纹入 `data/eval/SHA256SUMS`（追加，不改旧行） | `cd data/eval && sha256sum -c SHA256SUMS` 全 OK 且含 v3 行 |
| AC4 | LoRA 2ep 训练 EXIT:0，val 读数 + dev 评测 + holdout3 行落档 | `tail logs/sft-lora-r12-5e4-2ep.log`（或 reports 快照）含 `EXIT:0`；`reports/2026-11-21-lora-r12-2ep*.md` 存在 |
| AC5 | holdout v3 评测覆盖 10 ckpt（base/v1/v2/v2b/v2c/v2d/v2e/lora8/lora12/lora12-2ep），greedy + `--skip-ppl`，md+csv 三分入库 | `reports/2026-11-21-holdout-eval-v3.{md,csv}`；CSV 行数 = 10 × 90 + 表头 |
| AC6 | 人工复核判别项 + 三块预注册判据判定落档（math/translate/calibration + v2e vs v2 显著性） | `reports/2026-11-21-holdout-audit-v3.md` 含判定表 |
| AC7 | 分语言 val：工具 `tools/eval_lang.py` + 6 ckpt × {zh,en} PPL 分项落档，按预注册判读 | `reports/2026-11-21-langval.md` 含 6×2 表 |
| AC8 | 收波全套：LAB_NOTEBOOK 段 + lessons（若有新教训）+ HANDOFF/PLAN 更新 + PROVENANCE/指纹 + `git commit -m "day-12: …"` + push | `git status` clean；`git log -1` 含 day-12 |

## 5. 预注册判据（跑前落档，跑后不改）

1. **数学块（14 题，人工复核分）**：≥70%（≥10/14）→ "数学修复泛化成立"；<70% → 维持"窄查表"结论。**子判据**：`3 乘以 13`（39）与 v1 holdout `13 乘以 3`（曾答 42）对照读换序泛化；`9 加 6`（英文）读跨语言迁移。
2. **翻译块（14 题，人工复核分）**：≥70%（≥10/14）→ "翻译行为泛化成立"；<70% → 维持"句式级"结论。**子判据**：zh2en 方向单独读数（v2e 精确对为双向 15+15，此前只考过 en2zh 主题）。
3. **calibration 块（6 题）**：≥5/6 拒绝编造 → 维持"唯一稳定泛化项"结论；<5/6 → 降级表述。
4. **v2e vs v2 全卷（90 题）**：差 ≥5 题才称"显著优于"（n=90，二项 95% CI ≈ ±3~4 题）；<5 题差异表述为"持平"。
5. **LoRA 2ep**：主判据 = SFT val < 1.75（对全参 1.6038 的 0.20 差距收敛过半 → epochs 是 1 epoch 欠拟合的主因之一）；val ≥1.80 → 维持"容量/低秩主因"结论；1.75~1.80 之间 → "epochs 有贡献但未收敛过半"。辅读数（dev 题库/rubric/rep-4）只记录不设阈值。
6. **分语言 val**：以 v1（无英文上采样）为基线，比较 v2c/v2d/v2e 的 zh-PPL 退化幅度：≤1% = "无稀释证据"；>3% = "有稀释信号"；1~3% = "弱信号，不结论"。en 侧同表记录。

## 6. Task Breakdown

- [x] **T1 spec 落档 + commit**（commit `4679501`，2026-11-21；判据 §5 随 spec 冻结）
- [x] **T2 LoRA r=12 2ep 启动**（完成 2026-11-21：EXIT:0 · val 1.7921 · 2h37m · peak 9.76GB）
  - T2.1 [x] 命令按 §6 T2.1 执行（tmux 会话 sft-lora-r12-2ep；唯一变量 = target-tokens 500e6）
  - T2.2 [x] 起跑确认：`[anchor] 2.7706` / total_steps=7,630 / GPU 96% / 无 stale exit 标记
- [x] **T3 holdout v3 出题 + 去重**（T2 训练期间并行完成）
  - T3.1 [x] 60 新题 → `data/eval/tests-holdout-v3.json`（90 题；数学换序探针受数字嵌套限制改为 3×13）
  - T3.2 [x] 首轮 23 处撞车（translate 2 + SFT 源 21）→ 换 8 题同型变体 → **EXIT 0**；v3↔dev 交叉 0 撞车
  - T3.3 [x] 指纹 `2539aa2b…` 入 `data/eval/SHA256SUMS`
- [x] **T4 holdout v3 评测 + 人工复核**（T2 完成后执行）
  - T4.1 [x] 10 ckpt greedy 评测 → [reports/2026-11-21-holdout-eval-v3.md](../reports/2026-11-21-holdout-eval-v3.md)（md+csv；lora12-2ep 另补 dev 15/18 · rep-4 0.176）
  - T4.2 [x] 90 题 × 10 版人工校准（900 格全量编码）→ [reports/2026-11-21-holdout-audit-v3.md](../reports/2026-11-21-holdout-audit-v3.md)：数学 ✗（0~3/14）· 翻译 ✗（0~5/14）· calibration ✓（v2 系 5~6/6）· **v2e 53 vs v2 47（+6 达阈值）**
- [x] **T5 分语言 val**（T2 完成后执行）
  - T5.1 [x] `tools/eval_lang.py`（zh/en 分块 + 双口径 CE；首跑 off-by-one 已修）
  - T5.2 [x] 6 ckpt 跑分 → [reports/2026-11-21-langval.md](../reports/2026-11-21-langval.md)：英文上采样对 zh sup ±0.15%，**无稀释**（预注册 vs v1 口径有混杂，判读按因果口径 vs v2 并披露）
- [x] **T6 收波**（2026-11-21）：LAB_NOTEBOOK Day 12 段 · lessons 5 条 · HANDOFF §1/§2/§3/§4/§5/§7 · PLAN 变更记录 · PROVENANCE（v3 题库 + lora12-2ep ckpt）· commit + push

## 7. 出题避让规则（从 extras 侦察得出，2026-11-21）

1. **数学**：ARITH extras 覆盖 2~12 全对（乘/加/减）→ 新题 operand 至少一个 ≥13；多步运算（"再乘以/再加"）与应用题（苹果应用题）不受 ARITH 覆盖；英文数学为新增方向。**数字嵌套自检**：新题字符串不得包含任何 `a 乘/加/减 b 等于多少`（a,b∈2..12）子串（13×3 曾因 `3×3 ⊂ 13×3` 被检查器判假阳，换 3×13/13×5 避让）。
2. **calibration**：extras 年份覆盖 2027~2042 → 新题用 **2044+**（2046 世界杯 / 2044 夏奥 / 2045 诺奖）；句式沿用「请告诉我 X 年……」同型变体。
3. **concise 题面避让**：介绍一下{春天,太阳,地球,海洋,图书馆,茶叶,高铁,博物馆,互联网,长城,春节,中秋节,上海,广州,猫,狗,大熊猫}等 50 题已占 → 新 fluency-zh 用 {端午节,夏天,西安}；en 用 {birds, sunny morning, horses}。
4. **dev/holdout v2 同型不重题**：新题 = 换知识点/数字/场景的变体，不得与 dev 18 题或 holdout v2 30 题原句互含（检查器兜底）。
5. **SFT 源避让**：`你叫什么名字` 等 SFT 源高频题不用；identity 用「请介绍一下你自己/你是一个机器人吗/你懂哪些语言」候选，撞车即换。
6. 最终裁判 = `check_eval_leak.py`（双向 + 自测），EXIT 0 才算题库冻结。

## 8. Rollback Plan

- 全部为**新增件**：新题库新文件、新 out 目录、新 reports——不动任何旧证据/旧模型/部署 tag，无需回滚。
- LoRA 2ep 失败（OOM/超时/EXIT:1）→ `tmux kill-session` + 保留现场 + 记录现象，不自动重试（§5 判据只对成功 run 判定；失败本身是信息）。
- 出题撞车无法清零（>5 轮）→ 降级为 60~80 题收卷并在报告披露。

## 9. Timeline

| 时刻 | 动作 |
|---|---|
| 11-21 上午 | T1 spec + T2 LoRA 启动 → T3 出题/去重（并行） |
| 11-21 午后 | T2 收官（~2.6h）→ T4 holdout3 评测 + T5 分语言 val（GPU 排队） |
| 11-21 晚 | 人工复核 + 三份报告 + T6 收波 + commit/push |

## 10. References

- HANDOFF §7（本 spec 的三项来源与建议顺序）· holdout-audit §5（"若继续投入"方向）· eval-leak-recheck（检查器用法）
- SKILL §3.4（holdout 建设规则 + 去重硬门）· §3.2（LoRA/SFT 标准动作）· §6（收波清单）
- 判据基线：r12-1ep val 1.8054 · 全参 1.6038~1.6065 · holdout v2 人工 23/30（v2e/v2）

## 11. 验收记录（2026-11-21 收波核验）

| AC | 结果 | 验证/证据 |
|---|---|---|
| AC1 | ✅ | 90 题（30+60）/ 13 tag / math 14 / translate 14 / calibration 6；`tests-holdout.json` sha 仍 `e6e31aaa…` 未动 |
| AC2 | ✅ | `check_eval_leak.py --eval tests-holdout-v3.json --extra-dir --sft-source` → **EXIT 0**（首轮 23 处撞车换 8 题后）；v3↔dev 交叉 eval-vs-eval 0 hits |
| AC3 | ✅ | `data/eval/SHA256SUMS` 追加 `2539aa2ba2a41263677a03499693d591010a0485e853b420267a9b28f914c967  tests-holdout-v3.json`；`sha256sum -c` 全 OK |
| AC4 | ✅ | `EXIT:0 step=7630 val=1.7921`（exit 标记）；训练 log/csv 快照 + dev 补测（15/18 · rep-4 0.176）+ holdout3 行（人工 48）入 reports |
| AC5 | ✅ | `reports/2026-11-21-holdout-eval-v3.{md,csv}`：10 ckpt × 90 题，CSV = 901 行（含表头），greedy + `--skip-ppl` |
| AC6 | ✅ | `reports/2026-11-21-holdout-audit-v3.md` §3 判定表：数学 ✗ / 翻译 ✗ / calibration ✓ / v2e vs v2 +6 ✓ |
| AC7 | ✅ | `tools/eval_lang.py` + `reports/2026-11-21-langval.{md,csv}`：6 ckpt × {zh,en} 双口径；判读 = 无稀释（±0.15% sup），预注册基线缺陷披露 |
| AC8 | ✅ | LAB_NOTEBOOK Day 12 · lessons 5 条 · HANDOFF §1~§7 · PLAN 变更记录 · PROVENANCE 2 行 · commit + push |

**判据复核（§5 预注册 vs 实测）**：数学块最高 3/14 <10 ✗；翻译块最高 5/14 <10 ✗；calibration v2/v2d/v2e 6/6、v2b 5/6 ≥5 ✓；v2e−v2 = 53−47 = +6 ≥5 ✓（贴阈值，标注保留意见）；LoRA 2ep val 1.7921 ∈ [1.75, 1.80) → "epochs 有贡献但未收敛过半"；langval 按因果口径 ≤1% ✓（预注册 vs v1 口径缺陷披露于 audit §6）。
