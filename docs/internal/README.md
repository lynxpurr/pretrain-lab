# 内部过程记录（非读者入口）

本目录保存项目开发过程中的内部文档与状态快照。它们有上下文价值，但**不是公开读者的入口**：

- `HANDOFF.md`（仓库根）：会话交接、复现检查、波次队列、当前状态。
- `PLAN.md`（仓库根）：10 天计划、决策记录 D-01~D-10、风险与纪律。
- `LAB_NOTEBOOK.md`（仓库根）：逐日记账（决策/现象/读数/疑问）。
- `.zcode/skills/pretrain-lab/SKILL.md`：agent 操作规程（训练/评测/部署/故障排查/红线）。
- `status-log-2026-11-21.md`：旧版 README（内部状态长文），2026-11-21 归档。

这些文件保留当时的本地路径（如 `/home/zenz/...`）、私有上游仓引用（NoteFlow / nl2fem / finetune-lab）
和内部判据口径。公开读者请从 [`../../README.md`](../../README.md) 或 [`../quickstart.md`](../quickstart.md) 进入。

## 发布状态

- **Phase 1（发布阻断项）**：本目录整理时执行——许可证、README、依赖、脚本、docs、模型导出、CI。
- **Phase 2（可信度加固）**：待执行——900 格人工标签落盘、McNemar/CI、独立复核、v2f 决策。
- **Phase 3（打包发布）**：**待用户确认**——HF Hub / GitHub Release / 长文。
  本仓库目前**没有**执行任何公网推送或上传；README 中的 HF 仓库名是发布目标，尚未创建。

## 证据纪律

- `reports/` 只增不改；改错走勘误追加。
- 每份数据/ckpt 落位即录 SHA256（`data/PROVENANCE.md` + `SHA256SUMS`）。
- 历史 reports 可能含本地路径与内部引用，保留原样以维持证据链；不在公开读者面文档中重复这些路径。