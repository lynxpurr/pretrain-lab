# SPEC · 私有化仓内 agent 规程（`.zcode/skills/pretrain-lab`）

- **Status**: IN PROGRESS（2026-11-21）
- **Owner**: 用户指示（2026-11-21："将 `.zcode/skills/pretrain-lab` 从公开代码库中移除，变成私有（gitignore）"）
- **Scope 一句话**：把该目录从版本控制中移除并加入 `.gitignore`，本地文件保留；同步修正公开读者面的引用；**不重写 git 历史**。

## 1. Context

- 当前唯一被跟踪的 `.zcode` 文件是 `.zcode/skills/pretrain-lab/SKILL.md`（agent 操作规程：训练/评测/部署/故障排查/红线）。
- 该文件面向 agent、含本地路径与内部判据，不属于公开读者面；继续随仓库发布没有必要。
- 引用点：`HANDOFF.md` §0、`README.md` / `README.zh.md` 项目地图、`docs/internal/README.md`、`CHANGELOG.md`、`docs/internal/status-log-2026-11-21.md`（归档快照）、`specs/*`（历史 spec）。

## 2. Objective

1. `git rm --cached` 移除跟踪，工作区文件保留。
2. `.gitignore` 加入 `.zcode/`（本地 agent 配置整体私有）。
3. 公开读者面引用改为"本地私有/不入库"或移除；历史 spec 与归档快照保留原样（不做历史重写）。
4. commit + push，验证远端树中不再包含该路径。

## 3. Non-goals

- **不删除本地文件**——`.zcode/skills/pretrain-lab/SKILL.md` 继续在本地使用。
- **不重写 git 历史**——该文件在旧 commit 中仍可见；彻底清除需 force push / filter-repo，违反当前"历史不重写"红线，需另行决策。
- 不改 `reports/`、不改证据、不动模型/数据/部署。

## 4. Acceptance Criteria

| # | 验收标准 | 验证命令/判据 |
|---|---|---|
| AC1 | 不再跟踪；本地文件仍在；gitignore 命中 | `git ls-files .zcode` 输出为空；`test -f .zcode/skills/pretrain-lab/SKILL.md`；`git check-ignore -v .zcode/skills/pretrain-lab/SKILL.md` 命中 `.gitignore` |
| AC2 | 公开读者面无指向该路径的 markdown 链接 | `git grep -n '](.*\.zcode'` 为空（历史 spec/归档快照仅保留纯文本路径） |
| AC3 | 文档与代码检查不回归 | `tests/check_links.py` EXIT 0；`python -m compileall -q tools tests` EXIT 0 |
| AC4 | 远端已生效 | push 后 `git show origin/develop:.zcode/skills/pretrain-lab/SKILL.md` 报路径不存在；`git show origin/develop:README.md \| head -1` = `# pretrain-lab` |
| AC5 | 过程留痕 | `LAB_NOTEBOOK.md` 新增一段（决策/现象/读数/疑问） |

## 5. Rollback

`git revert <commit>` 即可恢复跟踪；本地文件全程未删除，无内容丢失。