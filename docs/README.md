# OpenPCB Docs 规范

本目录用于管理项目文档与每次变更解释记录。

## 目录结构

```text
docs/
  README.md
  changes/
    _TEMPLATE.md
    YYYY-MM-DD_<kebab-topic>.md
```

## 变更解释文档规则

每次代码变更任务结束后，必须新增 1 份变更解释文档，存放在 `docs/changes/`。

- 文件命名规则：`YYYY-MM-DD_<kebab-topic>.md`
- 示例：`2026-03-07_cli-bootstrap.md`
- 默认语言：中文
- 默认粒度：每次请求一份总文档（不按模块拆分）

## 固定章节要求

每份变更解释文档必须包含以下五段：

1. 变更前问题
2. 变更内容
3. 影响范围
4. 验证结果
5. 下一步建议

## 无代码变更任务

如果当次请求没有代码改动，也需要新增一份文档并在标题或摘要中标记 `no-code-change`。

## 协作契约（Process Contract）

- 输入：一次变更请求（用户任务）
- 输出：代码结果 + 一份变更解释文档（基于 `docs/changes/_TEMPLATE.md`）

