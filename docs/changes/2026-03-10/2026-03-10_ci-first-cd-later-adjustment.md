# 2026-03-10 调整为 CI 优先，CD 后置

## 变更前问题
- 仓库已同时引入 CI 与 CD workflow，但当前阶段更需要先稳定 CI 质量门禁。
- 你要求先实现 CI 管理项目，CD 在后续阶段再落地。

## 变更内容
- 保留并继续使用 CI 工作流：`.github/workflows/ci.yml`。
- 移除 CD 发布工作流：`.github/workflows/release.yml`。
- 更新项目管理文档：
  - `docs/project/CI_CD.md` 改为“CI 已实施，CD 规划中”。
  - `docs/project/TODO_LIST.md` 中 Milestone I 状态更新为：
    - I1（CI）=`已完成`
    - I2（CD）=`未开始`

## 影响范围
- 影响 GitHub Actions 自动化范围：当前仅保留 CI 自动校验。
- 不影响代码运行时行为，仅影响工程流程与项目管理状态。

## 验证结果
- 已确认 `.github/workflows/` 下仅保留 `ci.yml`。
- 已确认 `docs/project/CI_CD.md` 与 `docs/project/TODO_LIST.md` 状态一致。

