# SPEC · 公开发布准备（Public Release Readiness）

- **Status**: **IN PROGRESS — Phase 1 COMPLETED; Phase 2 PARTIAL**（2026-11-21；900 格标签 + McNemar/CI 已完成，独立复核/v2f 待执行；Phase 3 待用户确认）
- **Owner**: 用户拍板（2026-11-21："同意建议，执行"）· agent 执行
- **Scope 一句话**：把当前"内部收官态"仓库整理成可对外发布的 **代码 + 文档 + 模型 + 证据** 四件套：Phase 1 清发布阻断项（许可证/README/依赖/模型导出/CI），Phase 2 加固可信度（900 格人工标签落盘 + McNemar/CI + 独立复核），Phase 3 打包发布（HF Hub + GitHub Release + 长文）。**本 spec 不包含任何未经用户确认的公网推送/上传。**

## 1. Context（现状，事实源）

- 项目已收官（Day 0~12），部署 = `pretrain-lab-sft-v2e-q8`（Q8_0 173MB）；REPORT 定稿、两份 spec COMPLETED。
- 发布就绪度体检（2026-11-21）发现四类阻断项：
  1. **无 LICENSE/NOTICE/CITATION/CHANGELOG**——法律上默认保留所有权利，陌生人不能合法使用。
  2. **README 是内部日志式**（53 行巨段）——30 秒内看不出"是什么/为什么值得看/怎么跑"。
  3. **模型没有下载入口**——权重只在本地；Q8 只在 Ollama blob；`out/gguf/` 只有 F16；v2e 未导出 HF 格式。
  4. **+6 的人工分未落盘**——900 格判定只在报告里，无法复核；且 "+6 显著" 只是"达到预注册阈值"，未做 McNemar/CI。
- 已有优势：数据/ckpt 指纹齐全；证据三分；去重硬门；`transformers 5.23.0` + `huggingface-hub 2.4.0` 已在 `.venv-pre`；现有 HF 导出（v1）已验证可被 `LlamaForCausalLM` 加载并生成通顺中文。
- 时间口径勘误：HANDOFF 的"实际 8 天"与 LAB_NOTEBOOK 的 3 个日历日（11-18 ~ 11-20）矛盾；公开稿统一用时间戳"2026-11-18 08:08 → 11-20 20:10，约 60 小时"。

## 2. Objective

1. **Phase 1（发布阻断项，本次执行）**：许可证与归属、依赖与入口脚本、英文/中文 README、docs 分层、v2e HF + Q8 GGUF 模型产物、轻量 CI、当前文档脱敏。
2. **Phase 2（可信度加固，下一步）**：900 格人工标签 CSV + 复算脚本、McNemar 精确检验 + bootstrap CI、独立复核 30~50 题、90 题按"旧 30/新 60"与 tag 分拆；v2f 视时间决定。
3. **Phase 3（打包发布，需用户确认）**：HF Hub 仓库、GitHub Release v1.0.0、长文/图、可选 Zenodo/Ollama registry/公开 demo。

## 3. Non-goals（明确不做）

- **不做任何公网推送/上传**（HF/GitHub Release/模型 registry/社交平台）——Phase 3 需用户明确确认并提供凭据。
- 不重训全参 SFT、不做 DPO、不建 v2f（v2f 是 Phase 2 的可选项，另行勾选）。
- 不修改 `reports/` 历史证据（只增不改）；不覆盖 dev/holdout 题库；不改部署 tag。
- 不发布 `data/raw`（37.9GB）或 73GB checkpoint 谱系；不发布全部 8 个 SFT 变体（base + 部署版 + GGUF 足够）。
- 不重写 git 历史（报告里有 commit 引用）；只清理当前读者面文档。

## 4. Acceptance Criteria（可验证，逐条带验证命令）

### Phase 1（本次）

| # | 验收标准 | 验证命令/判据 |
|---|---|---|
| AC1 | `LICENSE`（Apache-2.0）+ `NOTICE`（FineWeb-Edu ODC-BY / CommonCrawl ToU / minimind Apache-2.0 / nanoGPT MIT / llama.cpp 借鉴）+ `CITATION.cff` + `CHANGELOG.md` 落位，四处许可表述一致 | `ls LICENSE NOTICE CITATION.cff CHANGELOG.md`；`head -3 LICENSE` 含 "Apache License"；`grep -r "Apache-2.0" README.md MODEL_CARD.md` 均命中 |
| AC2 | 英文 `README.md` + 中文 `README.zh.md`：Hero / 30 秒跑模型 / 结果表 / 项目地图 / 复现 / 限制 / 许可；首屏可读 | 人工走查；`wc -l README.md` ≤ 200；两文互相链接 |
| AC3 | `docs/{quickstart,reproduction,evaluation,architecture,faq}.md` + `docs/internal/README.md`；HANDOFF/PLAN/LAB_NOTEBOOK/SKILL 顶部加"过程记录，非读者入口"banner | `ls docs/*.md docs/internal/*.md`；`grep -l "过程记录" HANDOFF.md PLAN.md LAB_NOTEBOOK.md .zcode/skills/pretrain-lab/SKILL.md` = 4 |
| AC4 | `requirements.txt` + `scripts/{setup,download_data,download_model,run_demo,reproduce_eval}.sh`；`bash -n` 全过；setup 写明 CUDA/CPU 两条路 | `for f in scripts/*.sh; do bash -n "$f"; done` EXIT 0；`head -20 requirements.txt` 含 torch/tokenizers/numpy |
| AC5 | v2e HF 导出（fp16）+ `tokenizer_config.json` 含 chat_template；`transformers` 能加载并生成中文 | `out/hf-sft-v2e/model.safetensors` 存在且 ≤400MB；Python 加载 + `generate` 输出非空；config 含 `tie_word_embeddings`/`rope_theta` |
| AC6 | Q8 GGUF 独立文件（从 Ollama blob 复制）+ `gguf` reader 校验 + Ollama 可加载生成；sha256 记录 | `out/gguf/pretrain-lab-140m-sft-v2e-Q8_0.gguf` 存在；`GGUFReader` 可读；`ollama create` + 生成非空；sha 写入 `docs/reproduction.md`/模型卡 |
| AC7 | 轻量 CI：eval schema（三份题库）+ leak checker 已知撞车 fixture + 本地链接检查 + `compileall tools/` | `python -I tests/test_eval_schema.py`、`python -I tests/test_leak_checker.py`、`python -I tests/check_links.py`、`python -m compileall -q tools/` 全 EXIT 0 |
| AC8 | 当前读者面文档 0 断链；无密钥/私网 IP；历史 reports 不动（内部路径保留但 README 声明） | `tests/check_links.py` 0 broken；secrets scan 空；`git diff --stat reports/` 为空 |
| AC9 | 收波：LAB_NOTEBOOK 段 + PROVENANCE/模型指纹 + `git commit -m "release: phase 1 …"`；**不 push** | `git status` clean；`git log -1` 含 `release: phase 1`；`git remote -v` 不变 |

### Phase 2（下一步，未执行）

| # | 验收标准 | 验证命令/判据 |
|---|---|---|
| AC10 ⚠️ | 900 格人工标签落盘 + `tools/score_manual.py` 复算；**原判定未落盘，重判总分与 audit §2 不完全一致（v2e 52 vs 53 等），已披露** | CSV 900 行 + 表头；audit 对比表见 `reports/2026-11-21-manual-labels-audit.md` §1 |
| AC11 ✅ | McNemar 精确检验 + bootstrap 95% CI（v2e vs v2 配对）；按结果更新措辞 | **p=0.0923**；CI [0.000, 0.156]；全文已改"达到预注册阈值，统计上不显著" |
| AC12 ⏳ | 独立复核 30~50 题（冻结 rubric、盲评）；报 Cohen's kappa/一致率 | 复核记录 + kappa 写入 audit（待执行） |
| AC13 ✅ | 90 题按"旧 30/新 60"与 tag 分拆的 v2e−v2 差值表 | `reports/2026-11-21-manual-labels-audit.md` §3/§4 |
| AC14 ⏳ | （可选）v2f：改 2 条 brevity extras → 严格断言重建 → 重训 → 评测；若不执行，记录决策 | 待决策 |

### Phase 3（需用户确认）

| # | 验收标准 | 验证命令/判据 |
|---|---|---|
| AC15 | HF Hub 仓库（base / sft-v2e / GGUF）+ 英文 model card + license 元数据 | 用户提供 HF 凭据后执行；repo URL 可访问 |
| AC16 | GitHub Release `v1.0.0` + release notes + 资产 | 用户确认公开后执行 |
| AC17 | 长文 + 3 张图（loss / 八版对比 / 90 题能力块）+ 可选 Zenodo DOI | 文章发布链接 |

## 5. 预注册的对外措辞（跑前冻结，避免发布时漂移）

1. **+6/+7**：audit +6（53 vs 47）/ 重判 +7（52 vs 45），达到预注册阈值（≥5/90）；但 **McNemar p=0.0923 > 0.05**，只能写"达到预注册阈值、方向一致、统计上不显著"，**不得写"显著优于"**。
2. **时间**：统一写"2026-11-18 08:08 → 11-20 20:10，约 60 小时（含过夜训练）"，不写"实际 8 天"。
3. **能力**：数学 = "窄查表，不是算术"；翻译 = "句式级，不是通用翻译"；calibration = "唯一稳定泛化项"。不得用单题修复代表能力。
4. **版本读数**：必须标"完全干净 / 部分干净 / 含记忆"，v2e = 部分干净（2 题残留，干净子集 15/16）。
5. **模型定位**：学习/本地 demo，不是生产模型；不对标开源大模型；知识止于语料（2024 前后）。
6. **许可**：代码/模型 Apache-2.0；文档 CC-BY-4.0；数据沿用上游（FineWeb-Edu ODC-BY、minimind Apache-2.0）；再分发需保留 NOTICE。

## 6. Task Breakdown

### Phase 1（本次）

- [x] **T1 spec 落档 + commit**（本文件）
- [x] **T2 许可证与归属**：`LICENSE` / `NOTICE` / `CITATION.cff` / `CHANGELOG.md`
- [x] **T3 依赖与脚本**：`requirements.txt` + `scripts/{setup,download_data,download_model,run_demo,reproduce_eval}.sh`
- [x] **T4 README + docs**：`README.md`（EN）/`README.zh.md` / `docs/*` / 内部文档 banner
- [x] **T5 模型产物**：
  - T5.1 `tools/export_hf.py` 加 `--dtype {fp32,fp16,bf16}`；导出 v2e fp16
  - T5.2 `transformers` 加载 + 生成验证；config/tokenizer/chat_template 检查
  - T5.3 Q8 GGUF 从 Ollama blob 复制 → `out/gguf/...-Q8_0.gguf`；`GGUFReader` + `ollama create` 验证；sha 记录
- [x] **T6 测试/CI**：`tests/{test_eval_schema,test_leak_checker,check_links}.py` + `tests/fixtures/` + `.github/workflows/ci.yml`
- [x] **T7 脱敏与检查**：当前读者面文档替换 `/home/zenz`、私有仓引用；link check；secrets scan
- [x] **T8 收波**：LAB_NOTEBOOK 段 · PROVENANCE/模型指纹补 · `git commit -m "release: phase 1 …"`（**不 push**）

### Phase 2（下一步）

- [x] T9 900 格标签 CSV + `tools/score_manual.py`
- [x] T10 McNemar + bootstrap CI + 措辞更新
- [ ] T11 独立复核 30~50 题 + kappa
- [x] T12 旧 30/新 60 + per-tag 分拆
- [ ] T13 （可选）v2f 决策与执行

### Phase 3（需用户确认）

- [ ] T14 HF Hub 仓库与 model card
- [ ] T15 GitHub Release v1.0.0
- [ ] T16 长文 + 图 + 可选 Zenodo/Ollama registry/公开 demo

## 7. Rollback Plan

- Phase 1 全部为新增文件或读者面文档改写；旧证据/模型/部署 tag 不动。回滚 = `git revert <release-phase-1-commit>` + 删除 `out/hf-sft-v2e` / `out/gguf/*Q8*`（均在 gitignore）。
- 模型导出失败（transformers 加载失败/生成乱码）→ 保留旧 v1 导出，v2e 导出标记 failed，不删原始 ckpt；先排查 RoPE/q-k 布局与 config 字段。
- Q8 GGUF 校验失败（blob 不是有效 GGUF）→ 不发布 Q8 文件，改用 F16 + 文档说明 `ollama create -q q8_0`；sha 不录。
- 链接检查发现内部引用无法清理 → 在 `docs/internal/README.md` 声明"历史过程记录保留内部引用"，并把该链接排除出读者面检查。

## 8. Timeline

| 阶段 | 动作 | 预计 |
|---|---|---|
| 11-21 下午 | T1~T4（spec/许可证/脚本/README/docs） | 3~4h |
| 11-21 晚 | T5（模型导出 + Q8 GGUF）、T6（CI）、T7（脱敏） | 2~3h |
| 11-21 晚 | T8 收波 + commit（不 push） | 0.5h |
| 下一会话 | Phase 2（标签/McNemar/独立复核） | 1~1.5 天 |
| 用户确认后 | Phase 3（HF/GitHub/长文） | 0.5 天 |

## 9. References

- 发布就绪度体检（本会话分析）· HANDOFF §7 候选 4（v2f）· REPORT §12（Day 12 读数）
- 数据许可：`data/PROVENANCE.md`（FineWeb-Edu ODC-BY 1.0 / minimind Apache-2.0）
- 现有 HF 导出链路：`tools/export_hf.py`（v1 已验证 `LlamaForCausalLM` 可加载生成）
- 现有 GGUF 链路：`tools/export_gguf.py`（q/k permute 对齐 llama.cpp）· `reports/2026-11-20-deploy-v2e.md`
- 证据纪律：`reports/` 只增不改 · 指纹 `data/PROVENANCE.md` + `SHA256SUMS`

## 10. 验收记录

### Phase 1（2026-11-21）

| AC | 结果 | 验证/证据 |
|---|---|---|
| AC1 | ✅ | `LICENSE`（Apache-2.0 全文）· `NOTICE`（FineWeb-Edu / CommonCrawl / minimind / nanoGPT / llama.cpp）· `CITATION.cff` · `CHANGELOG.md`；README/MODEL_CARD 均写 Apache-2.0 + CC BY 4.0 |
| AC2 | ✅ | `README.md`（185 行，EN）+ `README.zh.md`（160 行）；Hero / quickstart / results / limits / repo map / license；互链；底部一处 "Implementation note" |
| AC3 | ✅ | `docs/{quickstart,reproduction,evaluation,architecture,faq}.md` + `docs/internal/README.md`；HANDOFF/PLAN/LAB_NOTEBOOK/SKILL 四处 banner |
| AC4 | ✅ | `requirements.txt` + `requirements-hf.txt`；`scripts/{setup,download_data,download_model,run_demo,reproduce_eval}.sh`；`bash -n` 全过 |
| AC5 | ✅ | `out/hf-sft-v2e/model.safetensors` 262.9 MiB / 137,847,552 参数；chat_template 在 `tokenizer_config.json`；PyTorch vs HF greedy **30/30 逐 token 一致** |
| AC6 | ✅ | `out/gguf/pretrain-lab-140m-sft-v2e-Q8_0.gguf` 174 MB / sha `8b64b668…`；`GGUFReader` file_type=7 / 147 tensors（114 Q8_0 + 33 F32）；Ollama 从文件建模型输出与部署 tag 逐字一致 |
| AC7 | ✅ | `tests/test_eval_schema.py` · `tests/test_leak_checker.py`（6 字已知撞车必被抓 + holdout v3 0 撞车）· `tests/check_links.py`（12 docs 0 broken）· `compileall` 全 EXIT 0 |
| AC8 | ✅ | 读者面文档 0 内部引用（NoteFlow/nl2fem/finetune-lab/`/home/zenz`）；secrets scan 无真密钥；`reports/` 无修改（仅新增导出报告） |
| AC9 | ✅ | commit `release: phase 1 …`；**未 push**（待用户确认） |

证据：[reports/2026-11-21-release-model-export.md](../reports/2026-11-21-release-model-export.md) · LAB_NOTEBOOK Release Phase 1 段 · `RELEASE_SHA256SUMS`。

### Phase 2（2026-11-21，部分完成）

| AC | 结果 | 验证/证据 |
|---|---|---|
| AC10 | ⚠️ 部分 | 900 行逐题标签已落盘（`reports/2026-11-21-holdout-v3-manual-labels.csv`）；重判总分 = base 10 / v1 46 / v2 45 / v2b 41 / v2c 41 / v2d 49 / **v2e 52** / lora8 40 / lora12 39 / lora12-2ep 42——与 audit §2（12/47/47/44/45/48/53/43/42/48）不完全一致；原判定未落盘，差异已披露 |
| AC11 | ✅ | v2e vs v2 配对：both 42 / only v2e 10 / only v2 3 / neither 35；**McNemar p=0.0923**；bootstrap 95% CI [0.000,0.156]；对外措辞已改为"达到预注册阈值，统计上不显著" |
| AC12 | ⏳ | 独立复核 30~50 题 + kappa 待执行 |
| AC13 | ✅ | 分 tag：fluency-en +5、reason +2、fact-zh +1、format +1；math −1、fact-en −1；translation/calibration 持平；old30 +2 / new60 +5 |
| AC14 | ⏳ | v2f 决策待定（重训会动 +7，不阻塞 v1.0） |

证据：[reports/2026-11-21-manual-labels-audit.md](../reports/2026-11-21-manual-labels-audit.md) · [labels CSV](../reports/2026-11-21-holdout-v3-manual-labels.csv) · `tools/score_manual.py`。

> **口径（2026-11-21）**：对外统一为 **"AI-assisted implementation, human-verified"**；README 底部 "Implementation note" 为唯一披露点；训练/评测/证据不变。

### Phase 3

（未执行；AC15~AC17 待用户确认）