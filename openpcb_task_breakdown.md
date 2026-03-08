# OpenPCB CLI v0.1 详细任务分解表

> 目标：构建一个 **类似 opencode 风格的 AI-native PCB CLI 工具**，先完成 **MVP（v0.1）**：  
> 用户输入自然语言需求，系统能够输出结构化设计计划，并生成最小可用的原理图工程骨架。

---

## 1. 项目范围与阶段目标

### 1.1 v0.1 要解决的问题

v0.1 不追求完整 PCB 自动设计平台，只验证以下核心链路：

1. 自然语言需求解析
2. 结构化项目描述生成
3. 基于模板的模块拼装
4. 输出最小可用的 KiCad 工程骨架
5. 基础规则检查
6. 支持简单自然语言修改

---

### 1.2 v0.1 非目标

以下内容 **不纳入 v0.1**：

- 自动布局
- 自动布线
- 高速信号完整性分析
- 复杂约束求解
- 浏览器图形界面
- 云端协作
- 多用户系统
- 复杂元件库管理平台

---

### 1.3 v0.1 命令集

计划包含以下 CLI 命令：

```bash
openpcb init
openpcb plan "<自然语言需求>"
openpcb generate <project.json>
openpcb check <project_dir 或 project.json>
openpcb edit <project.json> "<修改需求>"
```

可选附加命令：

```bash
openpcb export <project_dir>
openpcb doctor
openpcb version
```

---

### 1.4 当前状态说明（新增）

本任务分解表在原计划基础上新增状态标记，状态定义如下：

- `已完成`：对应任务的核心验收标准已满足
- `进行中`：命令壳子/部分能力已就绪，但业务逻辑未完整落地
- `未开始`：对应实现尚未落地

状态基于当前仓库实际代码，而非仅按规划目标文件名判断。

---

## 2. 推荐仓库目录结构

```text
openpcb/
├─ README.md
├─ LICENSE
├─ .gitignore
├─ pyproject.toml
├─ docs/
│  ├─ roadmap.md
│  ├─ architecture.md
│  ├─ cli-spec.md
│  └─ task-breakdown.md
├─ examples/
│  ├─ stm32_minimum/
│  ├─ esp32_dev/
│  └─ usb_uart/
├─ openpcb/
│  ├─ __init__.py
│  ├─ cli/
│  │  ├─ main.py
│  │  └─ commands/
│  │     ├─ init.py
│  │     ├─ plan.py
│  │     ├─ generate.py
│  │     ├─ check.py
│  │     └─ edit.py
│  ├─ agent/
│  │  ├─ parser.py
│  │  ├─ planner.py
│  │  ├─ executor.py
│  │  ├─ prompts/
│  │  │  ├─ plan_system.txt
│  │  │  └─ edit_system.txt
│  │  └─ tools/
│  │     └─ normalizer.py
│  ├─ schema/
│  │  ├─ project.py
│  │  ├─ module.py
│  │  ├─ component.py
│  │  ├─ net.py
│  │  └─ enums.py
│  ├─ pcb/
│  │  ├─ generators/
│  │  │  ├─ project_builder.py
│  │  │  ├─ schematic_generator.py
│  │  │  └─ kicad_writer.py
│  │  ├─ templates/
│  │  │  ├─ power/
│  │  │  ├─ mcu/
│  │  │  ├─ interface/
│  │  │  └─ misc/
│  │  └─ rules/
│  │     ├─ design_checks.py
│  │     └─ electrical_rules.py
│  ├─ io/
│  │  ├─ loader.py
│  │  ├─ saver.py
│  │  └─ exporters.py
│  ├─ config/
│  │  └─ settings.py
│  └─ utils/
│     ├─ logging.py
│     ├─ paths.py
│     └─ errors.py
└─ tests/
   ├─ cli/
   ├─ agent/
   ├─ pcb/
   ├─ schema/
   └─ fixtures/
```

---

## 3. 技术选型建议

- **语言**：Python 3.11+
- **CLI 框架**：Typer
- **数据模型**：Pydantic
- **模板系统**：Jinja2（可选）
- **测试**：Pytest
- **日志**：标准 logging
- **格式化**：Ruff + Black
- **包管理**：uv 或 poetry 或 pip + pyproject.toml
- **后续 LLM 接口封装**：统一抽象在 `agent/`

---

## 4. 开发原则

1. **先通链路，再做复杂度**
2. **所有中间结果都落盘**
3. **所有命令尽量可重跑**
4. **先支持少量高频模块**
5. **先用结构化 JSON 作为中间表示**
6. **命令输出要清晰、可读、可调试**
7. **保持“可被 Codex 连续实现”的小任务粒度**

---

# 5. 里程碑拆解

---

## Milestone 0：项目初始化

### 目标
搭建可运行的 Python CLI 工程骨架。

### 任务列表

#### M0-T1 创建仓库基础文件
**状态**：`已完成`

**文件：**
- `README.md`
- `LICENSE`
- `.gitignore`
- `pyproject.toml`

**任务：**
- 初始化仓库
- 写基础项目描述
- 配置 Python 包元信息
- 配置入口脚本 `openpcb`

**验收标准：**
- 本地可安装 `pip install -e .`
- 执行 `openpcb --help` 不报错

---

#### M0-T2 搭建 CLI 框架
**状态**：`已完成`

**文件：**
- `openpcb/cli/main.py`
- `openpcb/__init__.py`

**任务：**
- 使用 Typer 创建主 app
- 注册子命令组
- 添加 `version` 命令

**验收标准：**
- `openpcb --help`
- `openpcb version`

---

#### M0-T3 搭建基础配置系统
**状态**：`未开始`

**文件：**
- `openpcb/config/settings.py`

**任务：**
- 定义基础配置项：
  - 输出目录
  - 默认模型名
  - 日志等级
  - 是否启用 mock planner
- 支持环境变量读取

**验收标准：**
- CLI 内可加载配置
- 缺省情况下使用默认值

---

#### M0-T4 搭建日志与异常系统
**状态**：`进行中`

**文件：**
- `openpcb/utils/logging.py`
- `openpcb/utils/errors.py`

**任务：**
- 封装 logger
- 定义自定义异常：
  - `OpenPCBError`
  - `ValidationError`
  - `GenerationError`
  - `TemplateNotFoundError`

**验收标准：**
- 出错时 CLI 输出清晰
- 非调试模式下不打印大段 traceback

---

#### M0-T5 搭建测试框架
**状态**：`已完成`

**文件：**
- `tests/`
- `tests/cli/test_version.py`

**任务：**
- 配置 pytest
- 添加最小命令测试

**验收标准：**
- `pytest` 能通过最小测试

---

## Milestone 1：定义统一数据结构

### 目标
建立整个系统的中间表示（IR），避免直接操作 KiCad 文件。

### 任务列表

#### M1-T1 定义基础枚举
**状态**：`未开始`

**文件：**
- `openpcb/schema/enums.py`

**任务：**
定义枚举：
- `ModuleType`
- `PinType`
- `NetType`
- `InterfaceType`
- `PowerRailType`

**验收标准：**
- 枚举被其他 schema 正常引用

---

#### M1-T2 定义模块数据模型
**状态**：`未开始`

**文件：**
- `openpcb/schema/module.py`

**任务：**
定义 `ModuleSpec`：
- `id`
- `type`
- `name`
- `description`
- `parameters`
- `interfaces`
- `constraints`

**验收标准：**
- 能序列化/反序列化 JSON

---

#### M1-T3 定义元件/引脚/网络模型
**状态**：`未开始`

**文件：**
- `openpcb/schema/component.py`
- `openpcb/schema/net.py`

**任务：**
定义：
- `ComponentSpec`
- `PinSpec`
- `NetSpec`

最少字段建议：
- component: ref, value, footprint, pins, properties
- pin: name, number, type
- net: name, nodes, attributes

**验收标准：**
- 能表达一个 LED + 电阻 + 电源网络的小电路

---

#### M1-T4 定义项目级模型
**状态**：`未开始`

**文件：**
- `openpcb/schema/project.py`

**任务：**
定义 `ProjectSpec`：
- `name`
- `description`
- `requirements`
- `modules`
- `components`
- `nets`
- `constraints`
- `artifacts`
- `metadata`

**验收标准：**
- 能保存为 `project.json`
- 能作为 generate/check/edit 的统一输入

---

## Milestone 2：实现 init 命令

### 目标
快速初始化一个 OpenPCB 项目目录。

### 任务列表

#### M2-T1 实现项目脚手架生成
**状态**：`已完成`

**文件：**
- `openpcb/cli/commands/init.py`
- `openpcb/io/saver.py`
- `openpcb/utils/paths.py`

**任务：**
`openpcb init <project_name>` 生成：

```text
<project_name>/
├─ project.json
├─ plan.md
├─ output/
└─ logs/
```

**验收标准：**
- 命令执行后生成目录
- 初始 `project.json` 合法

---

#### M2-T2 生成默认 project.json
**状态**：`已完成`

**文件：**
- `openpcb/io/saver.py`

**任务：**
创建一个空白但合法的 `project.json`

**验收标准：**
- 能被后续命令读取
- 字段完整，有默认值

---

## Milestone 3：实现 plan 命令

### 目标
把自然语言需求解析成结构化项目计划。

### 任务列表

#### M3-T1 设计 plan 输出格式
**状态**：`未开始`

**文件：**
- `docs/cli-spec.md`

**任务：**
定义 `openpcb plan` 输出：
- 需求摘要
- 模块划分
- 推荐器件
- 电源结构
- 风险点
- 待确认项

**验收标准：**
- 文档中有明确规范
- 与 `plan.md` 和 `project.json` 字段对应

---

#### M3-T2 实现需求预处理
**状态**：`未开始`

**文件：**
- `openpcb/agent/parser.py`
- `openpcb/agent/tools/normalizer.py`

**任务：**
把自然语言需求做标准化处理：
- 提取板子类型
- 提取核心芯片
- 提取接口关键字
- 提取供电方式
- 提取附加模块（LED、button、sensor 等）

**验收标准：**
- 对常见输入可抽出关键意图

---

#### M3-T3 实现 planner（先支持 mock 模式）
**状态**：`未开始`

**文件：**
- `openpcb/agent/planner.py`

**任务：**
先实现一个不依赖真实 LLM 的 mock planner：
- 基于关键词规则生成初版计划
- 输出 `ProjectSpec`

后续再抽象真实 LLM planner 接口。

**验收标准：**
- 输入一句自然语言
- 返回合法 `ProjectSpec`

---

#### M3-T4 生成 plan.md
**状态**：`进行中`

**文件：**
- `openpcb/cli/commands/plan.py`
- `openpcb/io/saver.py`

**任务：**
把结构化结果落盘到：
- `project.json`
- `plan.md`

`plan.md` 应包含：
- 项目名称
- 需求描述
- 模块列表
- 器件建议
- 风险提示

**验收标准：**
- 用户执行 `openpcb plan "..."` 后得到可读文档

---

#### M3-T5 添加 plan 测试
**状态**：`未开始`

**文件：**
- `tests/agent/test_planner.py`
- `tests/cli/test_plan.py`

**任务：**
测试：
- 空输入报错
- STM32 最小系统需求可生成模块列表
- LED/Button/USB 等关键词识别正确

**验收标准：**
- plan 的关键路径有单测覆盖

---

## Milestone 4：建立模板系统

### 目标
让系统能够用“模块模板”拼出初步电路结构。

### 任务列表

#### M4-T1 定义模板描述格式
**状态**：`未开始`

**文件：**
- `openpcb/pcb/templates/README.md`（可选）
- 模板目录中的 JSON/YAML/Python 文件

**任务：**
决定模板表达形式。建议初期用 Python 或 JSON 表示。
模板至少包括：
- 模块名称
- 元件清单
- 默认参数
- 引脚接口
- 默认网络连接规则

**验收标准：**
- 模板能被程序读取

---

#### M4-T2 实现基础模板加载器
**状态**：`未开始`

**文件：**
- `openpcb/pcb/generators/project_builder.py`

**任务：**
实现：
- 根据 `ModuleType` 找模板
- 加载模板
- 实例化模块

**验收标准：**
- 可实例化一个 LED 模块
- 可实例化一个 LDO 模块

---

#### M4-T3 编写首批模板
**状态**：`未开始`

**建议首批模板：**
- `power/usb_input`
- `power/ldo_3v3`
- `mcu/stm32_minimum`
- `interface/swd`
- `interface/uart_header`
- `misc/status_led`
- `misc/reset_button`
- `misc/crystal_8mhz`

**验收标准：**
- 至少 5 个模板可用
- 能组合生成一个 STM32 最小系统

---

#### M4-T4 实现模板参数注入
**状态**：`未开始`

**文件：**
- `openpcb/pcb/generators/project_builder.py`

**任务：**
支持模板参数覆盖：
- 供电电压
- 晶振频率
- 是否带复位键
- 是否带下载接口
- LED 数量

**验收标准：**
- 同一个模板可根据参数生成不同实例

---

## Milestone 5：实现 generate 命令

### 目标
从 `ProjectSpec` 构建可导出的初版原理图工程。

### 任务列表

#### M5-T1 实现项目构建器
**状态**：`未开始`

**文件：**
- `openpcb/pcb/generators/project_builder.py`

**任务：**
根据 `project.modules`：
- 选择模板
- 生成 components
- 生成 nets
- 合并为统一项目结构

**验收标准：**
- 输入 project.json 后得到完整 components/nets

---

#### M5-T2 实现 schematic 级中间表示导出
**状态**：`未开始`

**文件：**
- `openpcb/pcb/generators/schematic_generator.py`

**任务：**
将内部结构整理为更接近原理图层级的表示：
- sheet
- symbol instances
- net labels
- references

**验收标准：**
- 中间表示能被 writer 使用

---

#### M5-T3 实现 KiCad writer（先做最小版本）
**状态**：`未开始`

**文件：**
- `openpcb/pcb/generators/kicad_writer.py`

**任务：**
生成最小可用：
- `.kicad_pro`
- `.kicad_sch`

初期重点：
- 文件合法
- KiCad 可打开
- 基本元件和网络可见

**验收标准：**
- KiCad 能打开输出文件
- 没有致命格式错误

---

#### M5-T4 实现 generate CLI 命令
**状态**：`未开始`

**文件：**
- `openpcb/cli/commands/generate.py`

**任务：**
支持：

```bash
openpcb generate project.json
```

输出到：
```text
output/
├─ kicad/
│  ├─ project.kicad_pro
│  └─ project.kicad_sch
├─ bom.json
└─ netlist.json
```

**验收标准：**
- generate 能完整跑通
- 输出目录结构固定

---

#### M5-T5 实现 BOM / netlist 导出
**状态**：`未开始`

**文件：**
- `openpcb/io/exporters.py`

**任务：**
输出：
- `bom.json`
- `netlist.json`

**验收标准：**
- BOM 包含 ref/value/footprint
- Netlist 包含网络与连接节点

---

#### M5-T6 添加 generate 测试
**状态**：`未开始`

**文件：**
- `tests/pcb/test_project_builder.py`
- `tests/cli/test_generate.py`

**任务：**
测试：
- 输入最小 project.json
- 输出 components/nets
- 输出文件存在
- 输出 JSON 合法

**验收标准：**
- generate 核心链路有测试

---

## Milestone 6：实现 check 命令

### 目标
做一套 MVP 级规则检查，让结果更像“工程工具”。

### 任务列表

#### M6-T1 定义检查规则接口
**状态**：`未开始`

**文件：**
- `openpcb/pcb/rules/design_checks.py`

**任务：**
定义 rule 接口：
- rule 名称
- 级别（info/warn/error）
- 检查逻辑
- 输出 message

**验收标准：**
- 可注册多个规则
- 可统一执行

---

#### M6-T2 实现首批检查规则
**状态**：`未开始`

**建议规则：**
1. MCU 电源脚未连接
2. MCU 缺少去耦电容
3. USB 输入未见保护/滤波提示
4. SWD 接口不完整
5. 复位脚悬空
6. 电源网络命名不规范
7. 未连接的重要引脚
8. LDO 输入输出不全

**验收标准：**
- 至少 5 条规则能运行
- 输出清晰可读

---

#### M6-T3 实现 check CLI 命令
**状态**：`未开始`

**文件：**
- `openpcb/cli/commands/check.py`

**任务：**
支持：

```bash
openpcb check project.json
openpcb check ./demo_project
```

输出：
- 规则报告
- 错误总数
- 警告总数
- 建议项

**验收标准：**
- check 可对生成项目给出反馈

---

#### M6-T4 添加 check 测试
**状态**：`未开始`

**文件：**
- `tests/pcb/test_design_checks.py`
- `tests/cli/test_check.py`

**任务：**
测试典型问题场景：
- 缺去耦
- 缺电源连接
- 接口不完整

**验收标准：**
- 规则系统有基本可靠性

---

## Milestone 7：实现 edit 命令

### 目标
支持通过自然语言对 `project.json` 做增量修改。

### 任务列表

#### M7-T1 设计 edit 输入输出格式
**状态**：`未开始`

**文件：**
- `docs/cli-spec.md`

**任务：**
定义：
- 修改前后 diff
- 支持的修改类型
  - 增加模块
  - 删除模块
  - 替换模块
  - 修改参数

**验收标准：**
- 文档中给出明确示例

---

#### M7-T2 实现 edit parser
**状态**：`未开始`

**文件：**
- `openpcb/agent/parser.py`
- `openpcb/agent/planner.py`

**任务：**
解析类似：
- “增加一个3.3V LDO”
- “把 Type-C 改成 Micro-USB”
- “增加两个 LED”
- “去掉晶振”

**验收标准：**
- 可将自然语言映射为结构化 edit action

---

#### M7-T3 实现 ProjectSpec 修改器
**状态**：`未开始`

**文件：**
- `openpcb/agent/executor.py`

**任务：**
对 `ProjectSpec` 应用修改：
- add_module
- remove_module
- replace_module
- update_parameter

**验收标准：**
- 修改后 schema 仍合法

---

#### M7-T4 实现 edit CLI 命令
**状态**：`未开始`

**文件：**
- `openpcb/cli/commands/edit.py`

**任务：**
支持：

```bash
openpcb edit project.json "增加一个3.3V LDO，并添加状态LED"
```

输出：
- 更新后的 `project.json`
- `edit-report.md`

**验收标准：**
- edit 可重跑 generate
- 修改记录清晰

---

#### M7-T5 添加 edit 测试
**状态**：`未开始`

**文件：**
- `tests/agent/test_executor.py`
- `tests/cli/test_edit.py`

**任务：**
测试：
- 增加模块
- 删除模块
- 替换模块
- 非法修改报错

**验收标准：**
- edit 主路径有测试

---

## Milestone 8：示例与发布准备

### 目标
把项目整理到“别人可以跑起来”的程度。

### 任务列表

#### M8-T1 编写示例项目
**状态**：`未开始`

**目录：**
- `examples/stm32_minimum/`
- `examples/esp32_dev/`
- `examples/usb_uart/`

**任务：**
每个示例包含：
- 原始需求文本
- project.json
- plan.md
- 生成输出样例

**验收标准：**
- 至少 3 个示例完整可复现

---

#### M8-T2 编写 README
**状态**：`未开始`

**文件：**
- `README.md`

**内容建议：**
- 项目简介
- 为什么做 OpenPCB
- 当前功能
- 安装方式
- 命令示例
- Demo 展示
- 路线图

**验收标准：**
- 第一次打开仓库的人知道这是什么、怎么跑

---

#### M8-T3 编写架构文档
**状态**：`未开始`

**文件：**
- `docs/architecture.md`

**内容建议：**
- CLI 层
- agent 层
- schema 层
- pcb generator 层
- writer 层

**验收标准：**
- 后续自己或 Codex 能按架构持续开发

---

#### M8-T4 做 v0.1 发布检查
**状态**：`未开始`

**任务：**
- 测试命令是否可运行
- 测试 examples 是否可复现
- 检查输出目录结构
- 检查日志信息
- 打 tag 准备发布

**验收标准：**
- 形成可用的 v0.1 版本

---

# 6. 文件级任务清单

下面给出更细的“文件 → 任务”列表，适合直接分配给 Codex。

**命名偏差说明（新增）**：原计划中的 `openpcb/io/loader.py` 与 `openpcb/io/saver.py`，当前实现命名为 `openpcb/io/project_loader.py` 与 `openpcb/io/project_saver.py`。

---

## 6.1 `openpcb/cli/main.py`
**当前状态**：`已完成`

**任务：**
- 创建 Typer app
- 注册 `init / plan / generate / check / edit / version`
- 统一错误捕获
- 添加全局 `--verbose`

**完成标准：**
- CLI 可正常路由命令

---

## 6.2 `openpcb/cli/commands/init.py`
**当前状态**：`已完成`

**任务：**
- 接收项目名和目录参数
- 创建项目结构
- 输出初始化结果

**完成标准：**
- 初始化命令可用

---

## 6.3 `openpcb/cli/commands/plan.py`
**当前状态**：`进行中`

**任务：**
- 接收自然语言需求
- 调用 parser/planner
- 保存 `project.json` 与 `plan.md`

**完成标准：**
- plan 命令跑通

---

## 6.4 `openpcb/cli/commands/generate.py`
**当前状态**：`进行中`

**任务：**
- 读取 project.json
- 调用 builder/generator/writer
- 写出 output 文件夹

**完成标准：**
- generate 命令跑通

---

## 6.5 `openpcb/cli/commands/check.py`
**当前状态**：`进行中`

**任务：**
- 读取 project.json 或项目目录
- 运行规则检查
- 输出检查报告

**完成标准：**
- check 命令可输出诊断结果

---

## 6.6 `openpcb/cli/commands/edit.py`
**当前状态**：`进行中`

**任务：**
- 接收 project.json 路径与编辑指令
- 解析 edit action
- 应用修改并保存

**完成标准：**
- edit 命令可更新项目

---

## 6.7 `openpcb/agent/parser.py`
**当前状态**：`未开始`

**任务：**
- 关键词抽取
- 需求标准化
- 修改指令标准化

**完成标准：**
- 返回可供 planner/executor 使用的结构化对象

---

## 6.8 `openpcb/agent/planner.py`
**当前状态**：`未开始`

**任务：**
- mock planner
- 规则映射模块
- 生成 `ProjectSpec`

**完成标准：**
- 常见 demo 输入有稳定输出

---

## 6.9 `openpcb/agent/executor.py`
**当前状态**：`未开始`

**任务：**
- 对 ProjectSpec 应用修改
- 生成修改报告

**完成标准：**
- 增删改查逻辑清晰

---

## 6.10 `openpcb/schema/project.py`
**当前状态**：`未开始`

**任务：**
- 定义 ProjectSpec
- 校验字段合法性
- 提供默认工厂方法

**完成标准：**
- 能作为全系统统一对象

---

## 6.11 `openpcb/pcb/generators/project_builder.py`
**当前状态**：`未开始`

**任务：**
- 根据模块挑模板
- 实例化组件
- 构造网络连接
- 合并多个模块

**完成标准：**
- 能把 modules 转成 components + nets

---

## 6.12 `openpcb/pcb/generators/schematic_generator.py`
**当前状态**：`未开始`

**任务：**
- 将逻辑结构整理为原理图表示
- 为 writer 提供中间对象

**完成标准：**
- 能支持最小 schematic 输出

---

## 6.13 `openpcb/pcb/generators/kicad_writer.py`
**当前状态**：`未开始`

**任务：**
- 输出合法 KiCad 文件
- 封装文件写入逻辑

**完成标准：**
- KiCad 能打开

---

## 6.14 `openpcb/pcb/rules/design_checks.py`
**当前状态**：`未开始`

**任务：**
- 规则抽象
- 检查执行器
- 诊断报告格式化

**完成标准：**
- check 命令能复用

---

## 6.15 `openpcb/io/loader.py`
**当前状态**：`已完成（当前实现文件为 `openpcb/io/project_loader.py`）`

**任务：**
- 从 JSON 加载 ProjectSpec
- 自动检测路径类型

**完成标准：**
- 项目加载稳定

---

## 6.16 `openpcb/io/saver.py`
**当前状态**：`已完成（当前实现文件为 `openpcb/io/project_saver.py`）`

**任务：**
- 保存 project.json
- 保存 plan.md
- 保存 edit-report.md

**完成标准：**
- 所有中间结果可落盘

---

## 6.17 `openpcb/io/exporters.py`
**当前状态**：`未开始`

**任务：**
- 导出 BOM
- 导出 netlist
- 后续可扩展 report

**完成标准：**
- generate 产物完整

---

# 7. 开发顺序建议（给 Codex 的执行顺序）

建议严格按下面顺序推进：

1. 搭 CLI 主框架
2. 实现配置、日志、异常
3. 定义 schema
4. 实现 `init`
5. 实现 mock `plan`
6. 实现 `project.json` / `plan.md` 落盘
7. 实现模板加载器
8. 实现 5 个基础模板
9. 实现 `generate`
10. 导出 BOM / netlist
11. 实现 `check`
12. 实现 `edit`
13. 补 tests
14. 补 examples
15. 补 README / docs

---

# 8. 6 周迭代排期

## 第 1 周：基础骨架
- 初始化仓库
- CLI 主入口
- 配置系统
- 日志与错误处理
- 初始测试

## 第 2 周：数据结构 + plan
- schema
- parser
- mock planner
- plan.md / project.json 输出

## 第 3 周：模板系统
- 模板格式确定
- LED/LDO/USB/SWD/按钮模板
- builder 初版

## 第 4 周：generate
- schematic 中间表示
- KiCad writer
- BOM / netlist 导出

## 第 5 周：check
- 规则系统
- 核心检查规则
- check CLI

## 第 6 周：edit + 整理发布
- edit parser
- executor
- 示例工程
- README
- v0.1 整理

---

# 9. 验收标准（v0.1 Done Definition）

当以下条件全部满足时，可认为 OpenPCB CLI v0.1 完成：

- [x] `openpcb init` 可创建项目
- [ ] `openpcb plan "<需求>"` 可生成 `project.json` 和 `plan.md`
- [ ] `openpcb generate project.json` 可生成最小 KiCad 工程
- [ ] `openpcb check` 可输出规则检查报告
- [ ] `openpcb edit` 可完成简单项目修改
- [ ] 至少 3 个 demo 可复现
- [ ] README 足够让他人上手
- [ ] 关键路径有基础测试覆盖（当前仅 `help/version/init`）

---

# 10. 建议作为首个 Demo 的需求

建议先固定这个基准项目，方便持续迭代：

## Demo 1：STM32 最小系统板

### 输入需求
```text
设计一个 STM32 最小系统板，带 USB-C 供电、SWD 下载接口、一个状态 LED、一个复位按键，并预留 UART 调试排针。
```

### v0.1 期望输出
- 模块：
  - STM32 MCU
  - USB-C 电源输入
  - 3.3V 稳压
  - SWD 接口
  - 状态 LED
  - 复位按键
  - UART Header
- project.json
- plan.md
- 最小 KiCad 工程
- BOM
- netlist
- check 报告

---

# 11. 给 Codex 的执行提示建议

你可以把下面这段加到任务说明里，方便 Codex 更稳定地按计划实现：

```text
请严格按照 docs/task-breakdown.md 的顺序推进，不要一次性实现所有功能。
每次只完成一个小里程碑，并确保：
1. 代码可以运行；
2. 新增文件有基本注释；
3. 命令行接口可测试；
4. 优先保证 schema、CLI 和中间表示稳定；
5. 先使用 mock/planned 逻辑，不要过早引入复杂外部依赖；
6. 每完成一个模块，就补一个最小 pytest 测试。
```

---

# 12. 下一步最先执行的任务

如果现在立刻开工，建议按下面顺序开始：

### Step 1
创建：
- `pyproject.toml`
- `openpcb/cli/main.py`
- `openpcb/__init__.py`

目标：跑通 `openpcb --help`

### Step 2
创建：
- `openpcb/schema/project.py`
- `openpcb/schema/module.py`
- `openpcb/schema/component.py`
- `openpcb/schema/net.py`

目标：先让 schema 稳定

### Step 3
创建：
- `openpcb/cli/commands/init.py`
- `openpcb/cli/commands/plan.py`
- `openpcb/agent/parser.py`
- `openpcb/agent/planner.py`

目标：先跑通 `plan`

---

# 13. 版本建议

建议先使用以下版本标记：

- `v0.1.0-alpha`：CLI + plan + generate 原型
- `v0.1.0-beta`：加入 check / edit
- `v0.1.0`：examples + docs + 基础测试完善

---

# 14. 总结

OpenPCB v0.1 最重要的不是功能多，而是要完成这条最核心的闭环：

**自然语言需求 → 结构化项目 → 模板化电路生成 → 可导出工程 → 规则检查 → 修改迭代**

只要这条链路能跑通，这个项目就已经具备继续扩展的基础。

后续所有 GUI、Web、插件化、KiCad 集成，都是建立在这条链路之上的。
