# 2026-03-10 TODO 文档重写与重命名（architecture-aligned）

## 1. 变更前问题

- 项目管理主文档仍为 `docs/project/TODO_LIST.md`，名称与当前目录规则中的 `TODO` 表述不一致。
- 原 TODO 结构更偏向早期 Agent-first 任务拆分，对 `mode-action-policy` 与 `IR -> Build -> Export -> Check` 新架构主轴对齐不足。
- 文档索引中仍引用 `docs/project/TODO_LIST.md`，后续维护容易产生路径不一致。

## 2. 变更内容

- 将 `docs/project/TODO_LIST.md` 重写并重命名为 `docs/project/TODO.md`。
- 新 TODO 文档按当前架构重构为以下板块：
  - 架构基线（已落地/关键缺口）
  - 架构对齐任务（Conversation、Mode-Action、PCB Pipeline、Plan/Edit、质量发布）
  - 近阶段优先级（P0-P2）
  - Definition of Done（架构版本）
- 同步更新主文档索引中的引用路径：
  - `docs/README.md`
  - `docs/project/README.md`
  - `docs/architecture/README.md`

## 3. 影响范围

- 删除文件：`docs/project/TODO_LIST.md`
- 新增文件：`docs/project/TODO.md`
- 修改文件：
  - `docs/README.md`
  - `docs/project/README.md`
  - `docs/architecture/README.md`
- 历史 `docs/changes/` 记录中的 `TODO_LIST.md` 引用保持不变，作为历史上下文保留。

## 4. 验证结果

- 已确认新文件存在且内容为架构对齐版本：`docs/project/TODO.md`。
- 已确认旧文件移除：`docs/project/TODO_LIST.md`。
- 已通过文本检索确认索引文档中的路径引用已切换到 `docs/project/TODO.md`。
- 工作区变更集合与预期一致，可直接进入提交流程。

## 5. 下一步建议

- 后续涉及项目里程碑、状态或优先级调整时，统一维护 `docs/project/TODO.md`。
- 当 `mode-action` 或 `pipeline` 实现发生实质落地时，同步更新：
  - `docs/architecture/*`
  - `docs/project/TODO.md`
  - 当日 `docs/changes/<YYYY-MM-DD>/` 记录
- 如需进一步减少历史路径歧义，可在后续一次专门清理任务中批量补充历史文档注释（不改动原始结论）。
