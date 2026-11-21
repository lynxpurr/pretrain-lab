# SPEC · 最终阶段（Day 9~10 收尾）— 部署切换 v2e + 报告定稿

- **Status**: **COMPLETED**（2026-11-20 立；同日 T1/T2/T3 + T4 Day 10 终检全部完成，提前 7 天收官——终检记录见 §9）
- **Owner**: 用户拍板方向（2026-11-20："按 spec 存档计划并推进"）· agent 执行
- **Scope 一句话**：把已完成的实验成果交付出去——部署切到能力最优的 v2e，报告把 10 天工作写清楚。**不再做新实验。**

## 1. Context（现状，事实源）

- G1~G5 全闭环：底座 val 2.7709 / SFT 八版（v1/v2/v2b/v2c/v2d/v2e + LoRA + base）/ GGUF+Ollama+demo 在跑。
- **v2e 五项预注册判据全过**（去污后干净读数）：rep-4 **0.055** / 题库 **17-18** / translate 真译文 / math **8+42** / PPL +5.5%——全面优于部署版 v2（rep-4 0.066 / 题库 15 / math 15+72 / en-fluency 拒答）。证据：`reports/2026-11-20-v2e.md`。
- **评测污染已识别并修复**：v2 起 extras 与 18 题原句撞车 → v2~v2d 题库分含记忆成分，v1/v2e 是干净读数。证据：`reports/2026-11-20-v2e.md` §1。
- G6 唯一未完成：`REPORT.md` 素材齐（八版表 + loss 图 + §4.6），待扩写与定稿。
- 两轮为限已用完（v2d/v2e），**不再迭代数据版本**。

## 2. Objective

1. 部署从 v2 切到 **v2e**（demo/Ollama 展示能力最优模型；旧 v2 保留可回滚）。
2. `REPORT.md` 达到可发布状态：评测污染方法学成独立章节，复现命令对齐 v2e，Day 10 只做终检。

## 3. Non-goals（明确不做）

- 不做 v2f 及任何新一轮数据迭代（两轮为限已用完）。
- 不做 DPO（新方向风险挤占 Day 10）；LoRA r=12 降为余力项（可选，不阻塞本 spec）。
- 不改 tokenizer / 预训练底座 / 评测题库（评测集变动会破坏八版可比性）。
- 不删旧模型/旧数据层/旧报告（只增不改纪律）。

## 4. Acceptance Criteria（可验证，逐条带验证命令）

| # | 验收标准 | 验证命令/判据 |
|---|---|---|
| AC1 | v2e GGUF 三件导出（F16/Q4_K_M/Q8_0） | `ls out/gguf/pretrain-lab-140m-sft-v2e-*.gguf` 3 个文件 |
| AC2 | Ollama 三个新 tag 可列 | `OLLAMA_HOST=127.0.0.1:11435 ollama list \| grep v2e` 含 v2e / -q4 / -q8 |
| AC3 | GGUF↔PyTorch greedy 对拍：**F16 5/5 逐字一致**；Q8_0 3/5 逐字 + 2 同义变体（新学能力保住）；Q4 4/5 偏离（42→72、translate 回退）→ 部署档 = Q8_0 | 见 `reports/2026-11-20-deploy-v2e.md` §2 三档对拍表 |
| AC4 | demo 指向 v2e 且健康 | `curl -s http://127.0.0.1:7860/health` → `{"ok":true}`；页面问 translate-en2zh 命中"机器学习" |
| AC5 | 旧 v2 tag 保留（可回滚） | `ollama list` 仍含 pretrain-lab-sft-v2-q4 |
| AC6 | MODEL_CARD/README/HANDOFF/REPORT 部署行 = v2e（默认 **q8**） | `grep -rn "sft-v2e-q8" MODEL_CARD.md README.md REPORT.md HANDOFF.md` 均有 |
| AC7 | REPORT 独立小节"评测污染"（撞车清单 + 12 处去污 + 断言 + v1/v2e 干净读数结论） | `grep -n "评测污染" REPORT.md` 且小节含 `assert_no_eval_leak` |
| AC8 | REPORT §10 复现命令含 v2e 参数与 v2e 数据目录 | `sed -n '/## 10/,/## 11/p' REPORT.md \| grep v2e` |
| AC9 | REPORT §0 成绩单为 v2e 口径 + 八版表 | 人工核对（SFT 行、评测表行） |
| AC10 | 证据链完整入库 | `git add -n .` 含 reports/2026-11-20-v2e* + 部署证据；`git status` clean |
| AC11 | **量化保真度条款**：部署量化档必须通过"新学能力抽检"（本轮 = math-mul 42 / translate 中文）；Q4_K_M 未通过 → 不入部署 | `reports/2026-11-20-deploy-v2e.md` §2/§3；Ollama tag 抽检 |

## 5. Task Breakdown

- [x] **T1 部署切换 v2e**（完成 2026-11-20；证据 `reports/2026-11-20-deploy-v2e.md`）
  - T1.1 [x] `tools/export_gguf.py --ckpt out/sft-v2e/last.pt --out out/gguf/pretrain-lab-140m-sft-v2e-f16.gguf --name pretrain-lab-140m-sft-v2e`
  - T1.2 [x] Modelfile 复制为 `out/Modelfile-sft-v2e`（TEMPLATE/参数沿用 sft-v2 版）
  - T1.3 [x] `ollama create pretrain-lab-sft-v2e` / `-q4` / `-q8`（GGUF 源，**勿走 safetensors experimental**）
  - T1.4 [x] GGUF↔PyTorch 对拍 4 条 prompt（AC3）
  - T1.5 [x] 重启 demo 指向 `pretrain-lab-sft-v2e-q4`（tmux demo 会话：kill 旧 → 起新）
  - T1.6 [x] 部署证据落 reports（`2026-11-20-deploy-v2e.md` + 对拍表）
- [x] **T2 报告定稿推进**（完成 2026-11-20；§5.1 评测污染章 + §10→v2e + §0 v2e 口径 + 八版终表/§4.7）
  - T2.1 [x] 新增"评测污染"小节（§5.1 独立成章）
  - T2.2 [x] §10 复现命令 v2c → v2e（build/sft/eval/deploy 四段）
  - T2.3 [x] §0 成绩单 v2e 口径 + 八版表核对；§11 限制更新
  - T2.4 [x] 图引用确认 day8-v2e + day8-v2d
- [x] **T3 状态同步与收波**（完成 2026-11-20）
  - T3.1 [x] HANDOFF §1/§2/§7（部署行 = v2e；§7 切 Day 10 终检卡）
  - T3.2 [x] README/MODEL_CARD 部署节 = v2e；PROVENANCE 补 GGUF 指纹
  - T3.3 [x] `git commit -m "day-8: 部署切 v2e + 报告扩写（评测污染章）"` + push（`5fc4d2c`）
- [x] **T4 Day 10（2026-11-20 提前执行）终检**
  - T4.1 [x] 八版最终对比表定稿（§0 八版表 + §4.7 裁决表，含"含记忆/干净"标注列；与 v2e-eval 对账）
  - T4.2 [x] repo 整理（README 首屏收官态、MODEL_CARD v2e 口径、证据三分核对、54 份 md/152 链接 0 断链）
  - T4.3 [x] REPORT 状态置 FINAL；本 spec 置 COMPLETED
  - T4.4 [x] §10 复现走查（v2e build bit-for-bit 4/4 sha + eval 18/18 行逐字 + deploy F16 5/5）——[reports/2026-11-20-day10-repro-check.md](../reports/2026-11-20-day10-repro-check.md)
  - T4.5 [x] 收波（LAB_NOTEBOOK Day 10 段 + commit + push）

## 6. Rollback Plan

- 部署回滚：`ollama create` 前旧 tag 不动 → demo 指回 `pretrain-lab-sft-v2-q4` 即恢复（<1min）。
- 报告改动：git 可回滚；`reports/` 只增不改（新文件不覆盖旧证据）。
- 数据/模型：v2e 产物已入库指纹；v2 资产不删除。

## 7. Timeline

| 日期 | 动作 |
|---|---|
| 11-20（今） | spec 入库 → T1 部署切换 + T2 报告扩写 |
| 11-22~25 | T2 收尾；LoRA r=12 一轮（可选项，不阻塞）；qa 回填 |
| 11-26 | 硬缓冲（终检或休息） |
| 11-27 | T4 Day 10 终检 + 发布 |

## 8. References

- 判据与结果：`reports/2026-11-20-v2e.md` · `...-v2e-eval{,-rubric}.md`
- 部署链路：`reports/2026-11-19-day7-deploy.md`（GGUF 导出 / Ollama 用户级 / 对拍方法）
- 状态卡：`HANDOFF.md` §7 · 决策与纪律：`PLAN.md` §6 · 操作规程：`.zcode/skills/pretrain-lab/SKILL.md` §3.2/§5
## 9. 终检记录（Day 10，2026-11-20 提前执行）

| AC | 结果 | 验证/证据 |
|---|---|---|
| AC1 | ⚠️ **口径勘误** | 实际机制 = **1 个 F16 GGUF**（`out/gguf/pretrain-lab-140m-sft-v2e-f16.gguf`）+ Ollama `-q` 生成 Q8_0/Q4_K_M 两档（在 Ollama 模型库内，不落 .gguf 文件）——不是 3 个 .gguf。三档均可用由 AC2/AC3 验证。 |
| AC2 | ✅ | `ollama list` 含 `pretrain-lab-sft-v2e`（F16）/ `-q8`（173MB）/ `-q4`（103MB） |
| AC3 | ✅ | F16 与 PyTorch **5/5 逐字一致**；Q8_0 **4/5 逐字 + 1 同义变体**且新学能力保住（math 42 / translate 中文）；Q4 不保真（42→72 / translate 英文）→ 部署 = Q8_0——[reports/2026-11-20-deploy-v2e-recheck.log](../reports/2026-11-20-deploy-v2e-recheck.log) |
| AC4 | ✅ | `/health` `{"ok":true}`；translate 抽检方向正确（demo 温度终检下调 0.7→0.3：T0.7 16/20 → T0.3 20/20） |
| AC5 | ✅ | `ollama list` 仍含 `pretrain-lab-sft-v2-q4`（回滚 <1min） |
| AC6 | ✅ | `grep -l sft-v2e-q8 MODEL_CARD.md README.md REPORT.md HANDOFF.md` = 4/4 |
| AC7 | ✅ | REPORT §5.1 评测污染章（撞车清单/12 处去污/`assert_no_eval_leak`/干净读数结论） |
| AC8 | ✅ | `sed -n '/## 10/,/## 11/p' REPORT.md \| grep -c v2e` = 6 |
| AC9 | ✅ | §0 成绩单 v2e 口径 + 八版终表（8 行 × 7 列 + 读数性质列，与 v2e-eval 对账一致） |
| AC10 | ✅ | 证据链入库（reports/ 只增不改；本次终检新增 repro-check/deploy-recheck/lora-r12 证据三件） |
| AC11 | ✅ | 量化保真度条款落档（skill §5 红线 + deploy 报告 §2/§3 + 本轮复验） |

**终检补充**：§10 四段命令与产物一致且关键路径可复现——v2e build **bit-for-bit**（4/4 sha256 + meta 全字段）、eval **18/18 行逐字**、deploy **F16 5/5**、demo 温度修正。证据 [reports/2026-11-20-day10-repro-check.md](../reports/2026-11-20-day10-repro-check.md)。

## 10. 收官后复核（Day 11，2026-11-20）

> 本 spec 已于 §9 置 COMPLETED；本节记录收官后发现的**证据质量问题**与处置，不改变 T1~T4 的完成状态。

- **dev 去重残留**：`assert_no_eval_leak` 的 `len(prompt)>=8` 守卫 + 只去空白的 norm 造成假阴性——`fact-months`（一年有几个月）/ `math-add`（3 加 5）仍以 format brevity 变体留在 v2e 训练集（4 条）；v2e 的 17/18 改为"17/18，2 题残留；干净子集 15/16"。
- **holdout 初版近重复**：3 题（2030 世界杯/光合作用/人工智能）+ 1 条 concise（上海）在双向检查下暴露 → 换题重跑 v2（sha `e6e31aaa`）：v2e 与 v2 人工复核同为 **23/30**，结论不变。
- **修复**：`assert_no_eval_leak` 去所有非单词字符、取消长度守卫、内置已知撞车自测、同时查 dev+holdout；新增 `tools/check_eval_leak.py`（双向三层）。
- **AC 影响**：AC7（评测污染章）已按残留更新；AC9（§0 成绩单）已把 v2e 标为"部分干净（2 题残留）"；AC11（量化抽检）不受影响。**部署不变**（v2e-q8 在 holdout 不劣、rep-4 最低）。
- 证据：[reports/2026-11-20-eval-leak-recheck.md](../reports/2026-11-20-eval-leak-recheck.md) · `...-holdout-eval-v2.md` · `...-holdout-audit.md` §7。

## 11. 后续（2026-11-21）

Day 12 收官后深化已另立 spec [`2026-11-21-post-final-deepening.md`](2026-11-21-post-final-deepening.md) 并 **COMPLETED**（holdout 90 题 + LoRA r12 2ep + 分语言 val）：结论 = **v2e 90 题人工校准 53 vs v2 47（+6 达预注册阈值；30 题"持平"系欠功效）**；数学/翻译能力块判据不通过（窄查表/句式级维持）；LoRA rank 与 epochs 单独加码都不够；英文上采样无稀释。**本 spec 的 AC1~AC11 与 §10 Day 11 复核结论不受影响；部署仍为 v2e-q8。**
