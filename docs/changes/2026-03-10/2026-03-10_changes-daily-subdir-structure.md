# 2026-03-10 changes 按日期子目录重构

## 变更前问题
- `docs/changes/` 下所有变更文档平铺存放，文件数量增长后查找成本变高。
- 现有规范未明确“按天归档”的目录结构。

## 变更内容
- 将历史变更文档按日期迁移到子目录：
  - `docs/changes/2026-03-07/`
  - `docs/changes/2026-03-08/`
  - `docs/changes/2026-03-09/`
  - `docs/changes/2026-03-10/`
- 保留根目录模板文件：`docs/changes/_TEMPLATE.md`。
- 更新 `docs/README.md`：
  - 目录结构示例改为 `docs/changes/<YYYY-MM-DD>/YYYY-MM-DD_<topic>.md`
  - 规则改为每次变更文档写入对应日期子目录。

## 影响范围
- 仅文档目录组织与规范说明变更，不影响运行逻辑与 CLI 行为。
- 后续新增变更记录需写入当天日期子目录。

## 验证结果
- 已确认 `docs/changes` 下存在按日期划分的子目录。
- 已确认 `docs/README.md` 规则与目录示例同步更新。

