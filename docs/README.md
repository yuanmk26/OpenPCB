# OpenPCB 文档规范

本目录用于管理项目文档，并将文档分为两类：
- `changes/`：每次任务的变更解释记录
- `architecture/`：系统与 Agent 架构说明

## 目录结构

```text
docs/
  README.md
  architecture/
    README.md
    agent-architecture.md
    system-architecture.md
  changes/
    _TEMPLATE.md
    YYYY-MM-DD_<kebab-topic>.md
```

## changes 目录规则

每次代码变更任务结束后，必须新增 1 份变更说明文档到 `docs/changes/`。
- 文件命名：`YYYY-MM-DD_<kebab-topic>.md`
- 默认语言：中文
- 每次请求只生成 1 份总文档（不按模块拆分）

每份变更文档必须包含五段：
1. 变更前问题
2. 变更内容
3. 影响范围
4. 验证结果
5. 下一步建议

若当次没有代码改动，也要生成说明文档，并标记 `no-code-change`。

## architecture 目录规则

`architecture/` 用于描述“当前已实现架构”，避免与目标设计混淆。
- 文档内容必须基于仓库当前代码，不写未实现能力。
- 建议在关键流程处标注状态：`已实现` / `进行中` / `未开始`。
- 新增或重构架构时，同步更新 `architecture/` 文档与本次 `changes/` 记录。
