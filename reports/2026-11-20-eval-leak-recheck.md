# 评测去重复核 — 假阴性修复与残留披露（2026-11-20 收官后复核）

> 触发：收官后沉淀"去重硬门"时，用新检查器 `tools/check_eval_leak.py` 复扫历史数据。结论：**v2e 的"12 处去污后复扫 0 撞车"是假阴性**——dev 仍有 2 题、holdout 初版有 3 题近重复。本文件 = 勘误与影响评估（reports/ 只增不改；旧读数保留为历史）。

## 1. 发现：dev 集残留 2 题（4 条）

`--eval data/eval/tests.json --extra-dir data/sft-extra-v2`（双向）命中：

| 评测题 | extras 命中 | 条数 |
|---|---|---|
| `fact-months`「一年有几个月？」 | format brevity：`简短回答：一年有几个月？` / `一年有几个月？不超过 10 个字。` | 2 |
| `math-add`「3 加 5 等于多少？」 | format ARITH/brevity：`简短回答：3 加 5 等于多少？` / `3 加 5 等于多少？不超过 10 个字。` | 2 |

**根因（`tools/build_sft_v2.py` 旧 `assert_no_eval_leak`）**：

```python
def norm(x): return re.sub(r"\s+", "", x).lower().strip("。？?！!")  # 只去空白
...
if len(nu) < 8: continue          # 短 extras 跳过
for tp in prompts:
    if len(tp) >= 8 and (...):    # ← 短 prompt 被整体跳过：一年有几个月=6 字、3加5等于多少=7 字
```

`len(tp) >= 8` 守卫本意是压假阳性，实际制造了**假阴性**：v2e 构建时断言通过、复扫报"0 撞车"，但这 2 题的 brevity 变体在 v2/v2b/v2c/v2d/v2e 的训练集里一直存在。

## 2. 影响：v2e 的"干净 17/18"降级为"17/18，2 题残留"

按去掉这 2 题的 **16 题干净子集**重算 dev 读数（`reports/2026-11-20-v2e-eval.csv`）：

| 模型 | 全 18 题 | 干净 16 题 | 残留题命中 |
|---|---|---|---|
| base | 6 | 6 | — |
| v1 | 16 | **14** | （v1 无 extras，2 题是干净通过） |
| v2 | 15 | 14 | fact-months |
| v2b | 15 | 13 | fact-months / math-add |
| v2c | 17 | **15** | fact-months / math-add |
| v2d | 15 | 13 | fact-months / math-add |
| v2e | **17** | **15** | fact-months / math-add |
| LoRA r8 | 15 | 13 | fact-months / math-add |

- v2e 仍是干净子集最高（15/16，并列 v2c；v1/v2 14/16），但"干净"应改为"**部分干净**"。
- **五项判据的解读修正**：rep-4 / rubric / calibration 不受影响；题库 17/18 仍 ≥16（干净子集 15/16），但 `math-add 8` 正是残留记忆，`math-mul 42` 在 holdout 未见组合全错（§5.2）——**数学判据"字面过、实质未过"**。
- **部署不变**：v2e-q8 仍是最优部署（rep-4 最低、holdout 不劣、calibration 稳）；依据改为"rep-4 + 校准 + holdout"，不是"数学修好"。

## 3. 发现：holdout 初版 3 题近重复 → 换题重跑 v2

`--eval data/eval/tests-holdout.json`（双向）命中 4 题：

| 题 | 撞车 | 处置 |
|---|---|---|
| calib-2030 世界杯 | calibration「请告诉我 2030 年世界杯的冠军。」= 评测题前缀 | → 2034 年冬奥会举办城市 |
| explain-光合作用 | format「用一句话解释什么是光合作用。」（少"请"） | → 细胞呼吸 |
| explain-人工智能 | format「用一句话解释什么是人工智能。」（少"请"） | → 引力 |
| zhflu-上海 | concise「介绍一下上海。」（少"请"） | → 成都 |

另消除 2 条数字嵌套假阳（3×3 ⊂ 13×3、3+8 ⊂ 13+8）：数学题换 `13 乘以 5` / `17 加 6`。复扫（双向 + SFT 源）**0 撞车**（EXIT 0）。重跑 v2（`reports/2026-11-20-holdout-eval-v2.md`）：

| 模型 | base | v1 | v2 | v2b | v2c | v2d | v2e | lora8 | lora12 |
|---|---|---|---|---|---|---|---|---|---|
| 关键词 | 12 | 23 | 23 | 22 | 22 | 22 | 22 | 21 | 21 |
| **人工复核** | 12 | 21 | **23** | 21 | 21 | 22 | **23** | 19 | 19 |

**结论不变**：v2e 与 v2 同 23/30，dev 排名不复现；数学未见组合全错（13×3 曾答 42、13×5 答 56/40/35、17+6 答 19）；translate 只认精确句式；calibration 稳定泛化。

## 4. 修复（已入库）

1. `tools/build_sft_v2.py` `assert_no_eval_leak`：norm 改为去掉所有非单词字符；**取消 `len>=8` 守卫**；内置自测（`简短回答：一年有几个月？` 必须包含 `一年有几个月？`）；同时检查 dev + holdout 两个题库。
2. 新增 `tools/check_eval_leak.py`：独立、双向、三层（eval↔eval / eval↔extras / eval↔SFT 源），`EXIT 1` = 撞车。命令：
   ```bash
   .venv-pre/bin/python -I tools/check_eval_leak.py \
     --eval data/eval/tests-holdout.json --eval data/eval/tests.json \
     --extra-dir data/sft-extra-v2 \
     --sft-source data/raw/minimind_dataset/sft_t2t_mini.jsonl
   ```
3. 保留历史：旧 `...-holdout-eval.md` / `...-holdout-audit.md` §2~§3 为 v1 读数，v2 以 §7 与 `...-holdout-eval-v2.md` 为准。

## 5. 决策：不重建、不重训

- 两轮数据迭代为限已用完；残留 2 题不改变部署结论（v2e 仍最优/并列），重建 v2f 需 ~1h20m 且会打乱八版可比性。
- 对外表述改为：**"v2e 17/18，其中 2 题残留；干净子集 15/16；数学/翻译的 dev 修复不泛化（holdout）"**。
- 若未来重训：先跑 §4 命令确认 0 撞车，再构建；断言自测会拦截同类假阴性。

## 6. 教训（入 lessons / skill）

- **检查器本身会假阴性**：报"0 撞车"前，先喂一个已知撞车证明它抓得到；长度守卫/归一化差异是常见静默跳过源。
- **去重必须双向**：训练样本可能是评测题的前缀（"请告诉我 2030 年世界杯的冠军。" vs "……冠军是谁"），单向 `eval in train` 会漏。
- **"干净"要分级**：完全干净（v1）/ 部分干净（v2e，2 题残留）/ 含记忆（v2~v2d）；报告表格必须标，不能二值化。