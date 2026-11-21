# HANDOFF — 新会话交接（公开发布维护态）

> **过程记录（非读者入口）**：本文件是项目开发过程的内部交接，保留本地路径与内部引用。公开读者请从 [README.md](README.md) / [docs/](docs/) 进入；发布状态见 [docs/internal/README.md](docs/internal/README.md)。
>
> **口径**：对外叙事用日期，不写 day/工期；AI 披露只在 README 底部 "Implementation note" 一处；旧 commit 说法见 [HISTORY.md](HISTORY.md)，不重写历史。
>
> 更新：2026-11-21 · 本件是新会话的启动入口。操作规程：`.zcode/skills/pretrain-lab/SKILL.md`（**本地私有**，已 gitignore，不随仓库发布）；报告：[REPORT.md](REPORT.md)；求职材料在仓外 `~/job-search/pretrain-lab/`。

## 0. 新会话开工序（按序，不跳步）

1. **加载 skill + 读本件**：`SKILL.md` → 本件 §1/§1.1/§2/§5/§6；缺细节回 PLAN/REPORT，不臆造。
2. **跑 §2 复现检查**（约 1 分钟）——红项先修再动；50 系环境坑见 PLAN §5。
3. **读前情**：`REPORT.md`（§0 终表、§5.1 去污/残留、§5.2 holdout、§10 复现、§12 深化、§13 McNemar）+ `docs/evaluation.md` + [HISTORY.md](HISTORY.md) + `LAB_NOTEBOOK.md` Release Phase 1/2 段 + `notes/lessons.md` 14~21。
4. **确认状态**：Phase 1 ✅ / Phase 2 部分 / Phase 3 pending；远端 `origin/develop` 已同步（以 `git log -1 origin/develop` 为准）。
5. **收波**（任何新动作结束前）：`reports/` 证据三分 → LAB_NOTEBOOK 段 → lessons（有新教训才写）→ PLAN 变更记录 → README/CHANGELOG → 指纹补 PROVENANCE → commit + push → **验证远端 README**。
6. **边界**：nl2fem / finetune-lab 是知识上游非资产上游（PLAN §7）——只引用知识不改其档案；本仓数据与代码全自建。

**首次回复向用户汇报四件事**：项目/发布状态 · 最近一次结果 · 今日可做什么 · 待拍板项。

**新会话首条消息（可直接粘贴）**：

> 读 `/home/zenz/projects/pretrain-lab/HANDOFF.md` 持卡：加载 `.zcode/skills/pretrain-lab/SKILL.md`，按 §0 六步执行——§2 复现检查（demo = `pretrain-lab-sft-v2e-q8`）→ 读前情（REPORT §0/§5.1/§5.2/§10/§12/§13 + docs/evaluation + HISTORY + LAB_NOTEBOOK Release Phase 1/2）→ 确认状态（Phase 1 ✅ / Phase 2 部分 / Phase 3 pending；远端已 push）→ 新动作先立 spec。口径：日期、不写 day/工期；AI 披露一处；历史不重写。

## 1. 状态一段话

**项目已完成，当前处于公开发布维护态**：本地 5070 Ti 16GB 上从零训出 **137,847,552** 参数中英小模型（3B token 预训练 → 250M token SFT ×6 → LoRA ×3 → GGUF/Ollama），产出 = 经验 + 模型 + 报告 + demo。**部署 = `pretrain-lab-sft-v2e-q8`**（Q8_0 174MB；F16 326MB 可选；Q4_K_M 不保真）。

- **技术结论**：dev 集 v2e 最优（17/18，2 题残留；干净子集 15/16）；holdout 90 题 audit v2e 53 vs v2 47（+6），逐题重判 52 vs 45（+7）——**达到预注册阈值，但 McNemar p=0.0923 不显著、bootstrap CI [0,0.156]**；增量集中在英文流畅度；数学/翻译不泛化；calibration 是唯一稳定泛化项。
- **发布状态**：Phase 1 ✅（License/README/docs/scripts/HF fp16/Q8 GGUF/CI）；Phase 2 **部分**（900 格标签 + McNemar；独立复核/v2f 待）；Phase 3 **pending**（GitHub 已 push；HF Hub / GitHub Release / 长文未做）。
- **当前口径**：日期，不写 day/工期；AI 披露只 README 底部一处；不称 hand-written/独立；旧 commit 由 [HISTORY.md](HISTORY.md) 解释。

## 1.1 公开发布状态（spec = [`specs/2026-11-21-public-release.md`](specs/2026-11-21-public-release.md)）

| 阶段 | 状态 | 证据 |
|---|---|---|
| Phase 1 发布阻断项 | ✅ | `LICENSE`/`NOTICE`/`CITATION`/`CHANGELOG`；README EN/ZH + docs 五件 + scripts + CI；HF fp16 + Q8 GGUF；[`reports/2026-11-21-release-model-export.md`](reports/2026-11-21-release-model-export.md) |
| Phase 2 可信度 | ⚠️ 部分 | 900 格标签 + McNemar/CI；[`reports/2026-11-21-manual-labels-audit.md`](reports/2026-11-21-manual-labels-audit.md)；独立复核/v2f 待 |
| Phase 3 打包发布 | ⏳ pending | **GitHub `develop` 已 push，远端 README 已更新**；HF Hub / GitHub Release / 长文/视频未做 |

**发布件坐标**：
- HF fp16：`out/hf-sft-v2e/`（262.9 MiB / 137,847,552 参数 / sha `7d1c2f0c…`）
- Q8_0 GGUF：`out/gguf/pretrain-lab-140m-sft-v2e-Q8_0.gguf`（174 MB / sha `8b64b668…`）
- F16 GGUF：`out/gguf/pretrain-lab-140m-sft-v2e-f16.gguf`（326 MB / sha `eee10822…`）
- 校验：`sha256sum -c RELEASE_SHA256SUMS`（4/4 OK）

## 2. 复现检查（约 1 分钟，按序）

```bash
cd /home/zenz/projects/pretrain-lab
git branch --show-current && git fetch -q && git status -sb       # develop；干净、与 origin 同步
git show origin/develop:README.md | head -1                      # 应为 "# pretrain-lab"
nvidia-smi --query-gpu=memory.free --format=csv,noheader         # ~14GB 空闲
df -h /home | tail -1                                            # 余量 ≥100GB
.venv-pre/bin/python -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
(cd data/shards && sha256sum -c SHA256SUMS | tail -1)             # 全 OK
ls data/eval/tests.json data/eval/tests-holdout.json data/eval/tests-holdout-v3.json data/eval/SHA256SUMS
ls out/main140m/last.pt out/sft-v2e/last.pt out/sft-lora-r12-5e4-2ep/last.pt
curl -s --max-time 3 http://127.0.0.1:11435/api/tags >/dev/null && echo ollama-user-ok || echo ollama-user-missing
OLLAMA_HOST=127.0.0.1:11435 ollama list | grep -c v2e             # 应 ≥3（v2e / v2e-q8 / v2e-q4）
curl -s --max-time 3 http://127.0.0.1:7860/health && echo demo-ok
.venv-pre/bin/python -I tools/check_eval_leak.py --eval data/eval/tests-holdout-v3.json \
  --extra-dir data/sft-extra-v2 --skip-sft-source                 # 应 EXIT 0
.venv-pre/bin/python -I tests/test_eval_schema.py                 # EXIT 0
.venv-pre/bin/python -I tests/test_leak_checker.py                # 阳性对照 + holdout 0 撞车
.venv-pre/bin/python -I tests/check_links.py                      # 12 docs 0 broken
.venv-pre/bin/python -m compileall -q tools tests                 # EXIT 0
sha256sum -c RELEASE_SHA256SUMS                                  # 4/4 OK
```

- **注意**：全量去重（含 dev）会 EXIT 1（dev 仍有 2 题残留，已知；见 §4）——这是**预期**，不是环境坏。
- `bad interpreter` = venv 断链（D-07 uv 托管解释器免疫）。
- `ollama-user-missing` / `demo-missing`：`OLLAMA_MODELS=$HOME/.ollama/models OLLAMA_HOST=127.0.0.1:11435 ollama serve`；demo `.venv-pre/bin/python -I tools/app_stdlib.py --model pretrain-lab-sft-v2e-q8 --port 7860`（默认 T0.3）。
- 分片 `sha256sum -c` 失败 = 数据被动过——**先查再训**（PROVENANCE 纪律）。
- **远端旧标题 = 未 push 或浏览器缓存**：先 `git status -sb`，再 `git show origin/develop:README.md | head -1`；仍旧则检查 push。

## 3. 里程碑（日期；详细证据在 reports/）

| 日期 | 内容 | 结果 |
|---|---|---|
| 2026-11-18 | 环境 + 自包含 `model.py` + 字符级 20M + 32k BPE + 3B 分片 + 140M 探针 | 门① PASS 52,250 tok/s |
| 2026-11-18 → 11-19 | 140M × 3B 主训练 | 16h07m41s · val 2.7709 · 46 ckpt |
| 2026-11-19 | SFT v1 + 评测框架 + 门② | val 1.5515 · 门② 不触发（0.0134 / 0.0051） |
| 2026-11-19 | v2/v2b + LoRA r8 + GGUF/Ollama | v2 val 1.6038 / rep-4 0.066 |
| 2026-11-19 → 11-20 | v2c/v2d/v2e 数据迭代 + 八版评测 | v2e rep-4 0.055 / dev 17/18（2 残留） |
| 2026-11-20 | 部署切 v2e-q8 + 终检 + 30 题 holdout | Q4 不保真 → Q8；F16 5/5 |
| 2026-11-20 | 去重假阴性修复 + holdout v2 | 干净子集 15/16；v2e=v2=23/30 |
| 2026-11-21 | 90 题 holdout + LoRA 2ep + 分语言 val | audit +6 / 重判 +7；McNemar p=0.0923；val 1.7921 |
| 2026-11-21 | 公开发布 Phase 1/2 | License/README/docs/模型导出/CI；900 标签 + McNemar |
| 2026-11-21 | 文档口径收敛 + HISTORY + push | 日期化、无工期卖点、AI 披露一处；远端 README 更新 |

## 4. 锚点速查（对账用已知答案）

**环境与数据**

| 锚 | 值 |
|---|---|
| 机器 | .118 · RTX 5070 Ti 16GB · 96GB RAM · 磁盘余 ~2.1T |
| `.venv-pre` | torch 2.11.0+cu128 · CUDA True · sm_120 · uv CPython 3.12.13 |
| 32k BPE | 词表 32,000 · specials 0/1/2 · zh 1.841 / en 4.226 chars/token · sha `05e9ef17…` |
| 3B 训练集 | 3,000,000,000 token · en 60%/zh 40% · 6×1GB + val 4M · max_id 31999 |
| SFT 集 | 250,001,408 token · 244,142 块 · 25% 预训练混入 · val 2,001,920 token |
| 评测集 | dev 18 题 / 13 tag（sha `6c5bd1e9`）+ holdout 30 题（sha `e6e31aaa`）+ holdout v3 90 题（sha `2539aa2b`） |
| dev 残留 | 2 题（`fact-months` / `math-add`，format brevity extras）；干净子集 v2e 15/16 |

**训练与评测**

| 锚 | 值 |
|---|---|
| 主模型 | d768/L16/H12 · **137,847,552** · 50M = d576/L8/H9 50,292,288 |
| 门① / 门② | **PASS 52,250 tok/s**（≥35k）· **不触发**（0.0134 / 0.0051） |
| 主训练 | bs8×accum8×T1024 · 45,777 步 · lr 6e-4 · 16h07m41s · peak 10.51GB · **val 2.7709** |
| SFT v2e（部署） | val 1.6065 / **rep-4 0.055** / dev 17/18（2 残留；干净 15/16）/ rubric 6/8 |
| LoRA r8 / r12 / r12-2ep | val 1.8253 / 1.8054 / **1.7921**；rep-4 0.260 / 0.249 / 0.176；均不部署 |
| holdout v3（90 题人工） | base 12 / v1 47 / v2 47 / v2b 44 / v2c 45 / v2d 48 / **v2e 53** / lora8 43 / lora12 42 / lora12-2ep 48 |
| 能力块 | 数学 0~3/14 ✗ · 翻译 0~5/14 ✗ · calibration v2 系 5~6/6 ✓ |
| v2e vs v2 | audit +6；重判 +7；**McNemar p=0.0923 不显著**、CI [0,0.156]；增量在英文流畅度 |
| 部署 | Q8_0 174MB（默认）/ F16 326MB；**Q4_K_M 不保真**（math 42→72 / translate 回退）；demo T0.3 |

**指纹与发布**

| 项 | 值 |
|---|---|
| 数据指纹 | raw 17 · 字符级 3 · tokenizer 3 · 分片 7 · SFT v1/v2/v2b/v2c/v2d/v2e 各 4 · 补充样本 5 · 评测 2 |
| ckpt 指纹 | main140m `0c0096cc172e8a58` · sft-v1 `853322df4583bfa2` · sft-v2 `a81c3480f4b63366` · v2b `44856617008a1e10` · v2c `6c12947bb3a56dd5` · v2d `fe972eed11aa599b` · **v2e `984a25c4d59e36a4`** · lora-r8 `81fbbf0840ed56c1` · lora-r12 `4d57b10cb7bcf169` · lora-r12-2ep `6eb9a7e6018276a2` |
| 发布指纹 | HF `7d1c2f0c…` · Q8 `8b64b668…` · F16 `eee10822…`；`RELEASE_SHA256SUMS` |
| 待回填 | **无**；剩余可选项见 §7 |

## 5. 波次队列与下一步

| 波次 | 状态 |
|---|---|
| 2026-11-18 ~ 11-20（环境 → 主训练 → SFT v1 → 门② → v2/v2b/LoRA/部署 → v2c/v2d/v2e） | ✅ 完成 |
| 2026-11-20（部署 v2e-q8 + 终检 + holdout v2 + 去重修复） | ✅ 完成 |
| 2026-11-21（90 题 holdout + LoRA 2ep + 分语言 val） | ✅ 完成 |
| 2026-11-21（公开发布 Phase 1/2） | ✅ Phase 1；⚠️ Phase 2 部分 |
| 2026-11-21（文档口径 + HISTORY + push） | ✅ 完成；远端 README 已新版 |
| 公开发布 Phase 3 | ⏳ pending（HF Hub / GitHub Release / 长文） |

**下一步优先级**：
1. **Phase 3**（需用户确认）：HF Hub 仓库（base / v2e / GGUF）、GitHub Release v1.0.0、长文 + 3 分钟视频；可选 Zenodo/Ollama registry。
2. **Phase 2 剩余**：独立复核 30~50 题 + kappa；v2f 决策（重训会动 +7，不阻塞 v1.0）。
3. **qa 复核**（学习项）：`notes/qa-day-*.md` 先自答再对照 `notes/qa-rubric.md`。
4. **求职叙事（仓外）**：`~/job-search/pretrain-lab/` 的 7 天 B 路径计划 + 9 题答案；判据 7/9 脱稿再发布；三个真实 JD 到手后再裁 bullet。

## 6. 惯例与红线

- **对外叙事**：日期，不写 day/工期；不把"10 天/60 小时"当卖点；AI 披露只 README 底部一处；不称 hand-written/独立；旧 commit 由 HISTORY.md 解释，不重写历史。
- **评测**：dev 只用于迭代，验收看 holdout；关键词分 + 人工复核并列；版本读数标"完全干净/部分干净/含记忆" + 干净子集；去重检查器先自测（已知撞车必须被抓）；判"持平"前算功效；**阈值 ≠ 显著**（McNemar p=0.0923）。
- **发布**：License/NOTICE/CITATION/CHANGELOG；HF/GGUF 三同对拍 + 新学能力抽检；`RELEASE_SHA256SUMS`；链接/schema/leak/compile；**push 后验证远端 README**。
- **证据/指纹**：`reports/` 只增不改；每次 run 三分 md + csv + log；数据/ckpt 落位即录 SHA256。
- **git**：develop 直提；模型/checkpoint/语料/原始 logs 不入库；commit message 是历史，不改写。
- **边界**：nl2fem / finetune-lab 是知识上游非资产上游；只引用知识不改其档案。

## 7. 可选工作（均需新 spec；不阻塞交付）

| 优先级 | 事项 | 成本 | 收益/判据 |
|---|---|---|---|
| 1 | **Phase 3：HF Hub + GitHub Release + 长文** | 0.5 天 | 对外可访问的模型/发布页/文章；需用户确认仓库名与凭据 |
| 2 | **独立复核 30~50 题 + kappa** | 0.5 天 | 缓解"同 agent 出题/判分"的保留意见；公开 900 标签已可审 |
| 3 | **v2f：去 brevity 残留重建 + 重训** | ~1h20m + 重跑八版 | 换完全干净 dev 读数；会动 +7，发布后做 |
| 4 | qa 复核（学习项） | 自定 | 先自答再对照 qa-rubric |
| — | DPO | — | **不建议**（新方向 + 翻新伤口风险） |

**Phase 3 建议结构**：
- HF：`pretrain-lab-140m-base` / `pretrain-lab-140m-sft-v2e` / `...-GGUF`；英文 model card + license + eval 集。
- GitHub Release `v1.0.0`：release notes + GGUF 资产（或 HF 链接）。
- 长文：标题围绕"评测污染 + 90 题 holdout + McNemar 降级"，不是"140M 模型"。
- 视频：3 分钟 demo（本地 Ollama + 3 个工作流 + 限制）。

## 8. 参考实现与出处

- minimind @ `233d00f` · nanoGPT @ `3adf61e`（`~/projects/`，只读借鉴）
- 全部证据：`reports/2026-11-18-*` ~ `reports/2026-11-21-*`（含 holdout / eval-leak-recheck / release-model-export / manual-labels-audit）
- 历史 commit 说明：[HISTORY.md](HISTORY.md)
- 求职材料（仓外）：`~/job-search/pretrain-lab/`