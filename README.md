# OpenPCB

OpenPCB 是一个面向 PCB 设计流程的 AI Agent 框架，目标是将用户的自然语言硬件需求逐步转化为结构化设计规格、板卡架构方案，以及后续的原理图与布局任务。

## 项目目标

PCB 设计并不是一次性生成文件的问题，而是一个分阶段的工程流程，包括：

1. 获取需求
2. 补全约束
3. 生成板卡架构
4. 规划原理图
5. 校验设计合理性
6. 导出设计产物

OpenPCB 希望将这个过程显式建模为一个 AI Agent 系统，而不是把 PCB 设计当成一个大 prompt 一次性完成。

## 当前范围

当前 MVP 主要聚焦于 **需求阶段**，包括：

- 自然语言需求输入
- `RequirementSpec` 结构化提取
- 关键缺失字段识别
- planner 驱动的下一步决策
- orchestrator 驱动的 agent 主循环
- 初步的 `ProjectState` 设计

当前暂不覆盖：

- 完整原理图自动生成
- 自动布局布线
- 完整 KiCad 工程导出
- 完整器件选型闭环

## 核心设计思想

OpenPCB 当前遵循以下原则：

- **Schema-first**：先定义结构化模型，再做生成
- **State-centered**：agent 的本质是持续更新项目状态
- **Workflow-driven**：将设计流程拆解为 requirement / architecture / schematic 等阶段
- **Tool-based execution**：执行动作应通过工具层完成
- **Human-in-the-loop**：用户应始终在设计回路中

## 目录结构

```text
src/openpcb/
  app/          # 应用入口与启动装配
  agent/        # orchestrator、runtime、session
  planner/      # 下一步动作决策
  workflows/    # requirement / architecture / schematic 流程
  domain/       # PCB 领域模型与 schema
  services/     # 业务能力层
  infra/        # LLM、存储、日志、配置
  tools/        # 外部工具执行层
  tests/        # 测试
```
## 当前开发重点

当前优先事项包括：

完善 RequirementSpec

设计清晰的 ProjectState

打通 planner / orchestrator / requirement service 主链路

接入最小可用 LLM 抽取能力

建立 requirement 阶段测试样例

## 快速开始

### 1. 创建虚拟环境

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. 安装依赖

``` bash
pip install -e .
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env`，填写例如：

- `OPENAI_API_KEY`
- `OPENPCB_MODEL`

### 4. 启动 CLI

```
PYTHONPATH=src python -m openpcb.app.cli
```

## 示例目标

当前 MVP 的一个典型流程如下：

用户输入：

- 帮我设计一个 STM32 最小系统板，USB 供电，带 SWD 和串口。

系统会：

- 提取结构化需求
- 识别缺失信息，例如 MCU 型号和系统电压
- 发起补问
- 更新项目状态
- 判断是否可以进入 architecture 阶段

## 路线图
### Phase 1
需求提取与补问闭环

### Phase 2
板卡架构生成

### Phase 3
原理图规划与中间产物生成

### Phase 4
工具接入、规则校验与布局支持

## 设计原则

- 尽量使用显式状态，而不是隐式 prompt 状态

- 尽量使用结构化 schema，而不是大段自由文本

- 尽量使用阶段式 workflow，而不是单体式生成

- 优先实现小而稳定的自动化，而不是大而脆弱的自动化

- 保持系统可理解、可测试、可扩展

## 当前状态

OpenPCB 目前处于早期实验阶段，当前主要围绕：

- requirement extraction
- planner 设计
- workflow 拆解
- state 建模
- 最小 LLM 接入

展开开发。

## License

待定