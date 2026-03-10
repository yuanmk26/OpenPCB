# 2026-03-10 项目管理文档重构与 CI/CD 基线落地

## 变更前问题
- `TODO_LIST.md` 位于仓库根目录，项目管理文档与架构/变更文档未分层。
- 缺少统一的项目管理目录与 CI/CD 规则文档。
- 仓库未配置 GitHub Actions 的 CI/CD 基础流程。

## 变更内容
- 文档结构重构：
  - `TODO_LIST.md` 迁移至 `docs/project/TODO_LIST.md`。
  - 新增 `docs/project/README.md` 与 `docs/project/CI_CD.md`。
  - 更新 `docs/README.md`，新增 `project/` 分区与维护规则。
- 引用修复：
  - 文档中对 `TODO_LIST.md` 的旧路径统一改为 `docs/project/TODO_LIST.md`。
- CI/CD 落地：
  - 新增 `.github/workflows/ci.yml`（PR/main，执行 `ruff + pytest + build`）。
  - 新增 `.github/workflows/release.yml`（tag `v*`，自动构建并发布 GitHub Release）。
  - `pyproject.toml` 增加 `build`、`ruff` 开发依赖并补充最小 Ruff 配置。

## 影响范围
- 影响文档管理路径与项目管理约定：
  - 根目录不再保留 `TODO_LIST.md`。
  - 后续项目计划与 CI/CD 规则统一维护在 `docs/project/`。
- 影响工程流程：
  - 新增 GitHub Actions 自动质量门禁与发布流水线。

## 验证结果
- 已执行路径与引用检查：`rg -n "TODO_LIST\\.md"`。
- 已执行本地验证命令：`python -m pytest`、`python -m build`、`ruff check .`。
- 已确认 `.github/workflows` 下包含 `ci.yml` 与 `release.yml`。

