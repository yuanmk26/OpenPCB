# Directory tree

从与chatgpt聊天中获取的信息：

```
openpcb/
├─ README.md
├─ LICENSE
├─ .gitignore
├─ .env.example
├─ pyproject.toml
├─ Makefile
├─ pytest.ini
│
├─ docs/
│  ├─ architecture.md
│  ├─ schema.md
│  ├─ workflows.md
│  ├─ prompting.md
│  ├─ tool_integration.md
│  └─ roadmap.md
│
├─ examples/
│  ├─ stm32_minimum_system.md
│  ├─ esp32_sensor_board.md
│  └─ buck_converter_board.md
│
├─ data/
│  ├─ templates/
│  │  ├─ boards/
│  │  │  └─ mcu_minimum_system.yaml
│  │  ├─ circuits/
│  │  │  ├─ usb_power_input.yaml
│  │  │  ├─ ldo_3v3.yaml
│  │  │  ├─ mcu_reset.yaml
│  │  │  └─ swd_interface.yaml
│  │  └─ prompts/
│  │     └─ requirement_examples.yaml
│  │
│  ├─ parts/
│  │  ├─ mcu_catalog.yaml
│  │  ├─ regulator_catalog.yaml
│  │  ├─ connector_catalog.yaml
│  │  └─ passive_defaults.yaml
│  │
│  └─ design_rules/
│     ├─ default_rules.yaml
│     ├─ mcu_board_rules.yaml
│     └─ power_board_rules.yaml
│
├─ scripts/
│  ├─ dev_run.py
│  ├─ export_schema.py
│  ├─ seed_data.py
│  └─ eval_cases.py
│
├─ tests/
│  ├─ unit/
│  │  ├─ test_requirement_schema.py
│  │  ├─ test_requirement_service.py
│  │  ├─ test_planner.py
│  │  └─ test_state_machine.py
│  │
│  ├─ integration/
│  │  ├─ test_requirement_flow.py
│  │  ├─ test_architecture_flow.py
│  │  └─ test_tool_registry.py
│  │
│  ├─ e2e/
│  │  └─ test_stm32_minimum_system_e2e.py
│  │
│  └─ fixtures/
│     ├─ user_inputs/
│     │  └─ stm32_minimum_system.json
│     ├─ llm_outputs/
│     │  └─ requirement_extract_response.json
│     └─ states/
│        └─ initial_project_state.json
│
└─ src/
   └─ openpcb/
      ├─ __init__.py
      │
      ├─ app/
      │  ├─ __init__.py
      │  ├─ cli.py
      │  ├─ bootstrap.py
      │  └─ container.py
      │
      ├─ config/
      │  ├─ __init__.py
      │  ├─ settings.py
      │  └─ constants.py
      │
      ├─ agent/
      │  ├─ __init__.py
      │  ├─ orchestrator.py
      │  ├─ runtime.py
      │  ├─ session.py
      │  ├─ context.py
      │  ├─ messages.py
      │  └─ state_machine.py
      │
      ├─ planner/
      │  ├─ __init__.py
      │  ├─ planner.py
      │  ├─ decision.py
      │  ├─ task_graph.py
      │  └─ recovery.py
      │
      ├─ workflows/
      │  ├─ __init__.py
      │  ├─ base.py
      │  ├─ registry.py
      │  ├─ requirement_flow.py
      │  ├─ architecture_flow.py
      │  ├─ schematic_flow.py
      │  ├─ review_flow.py
      │  └─ board_types/
      │     ├─ __init__.py
      │     └─ mcu_minimum_system.py
      │
      ├─ domain/
      │  ├─ __init__.py
      │  │
      │  ├─ common/
      │  │  ├─ __init__.py
      │  │  ├─ enums.py
      │  │  ├─ types.py
      │  │  ├─ errors.py
      │  │  └─ value_objects.py
      │  │
      │  ├─ project/
      │  │  ├─ __init__.py
      │  │  ├─ models.py
      │  │  ├─ state.py
      │  │  └─ schema.py
      │  │
      │  ├─ requirements/
      │  │  ├─ __init__.py
      │  │  ├─ models.py
      │  │  ├─ schema.py
      │  │  ├─ validators.py
      │  │  └─ normalizers.py
      │  │
      │  ├─ board/
      │  │  ├─ __init__.py
      │  │  ├─ models.py
      │  │  ├─ architecture.py
      │  │  ├─ constraints.py
      │  │  └─ interfaces.py
      │  │
      │  ├─ components/
      │  │  ├─ __init__.py
      │  │  ├─ models.py
      │  │  ├─ selection.py
      │  │  ├─ matching.py
      │  │  └─ footprints.py
      │  │
      │  ├─ schematic/
      │  │  ├─ __init__.py
      │  │  ├─ models.py
      │  │  ├─ nets.py
      │  │  ├─ symbols.py
      │  │  └─ rules.py
      │  │
      │  └─ layout/
      │     ├─ __init__.py
      │     ├─ models.py
      │     ├─ placement.py
      │     ├─ routing.py
      │     └─ rules.py
      │
      ├─ services/
      │  ├─ __init__.py
      │  ├─ requirement_service.py
      │  ├─ architecture_service.py
      │  ├─ component_service.py
      │  ├─ schematic_service.py
      │  ├─ validation_service.py
      │  └─ project_service.py
      │
      ├─ prompts/
      │  ├─ __init__.py
      │  ├─ loader.py
      │  ├─ renderer.py
      │  ├─ shared/
      │  │  ├─ system.md
      │  │  ├─ output_rules.md
      │  │  └─ tool_calling.md
      │  ├─ requirement/
      │  │  ├─ extract.md
      │  │  ├─ clarify.md
      │  │  └─ normalize.md
      │  ├─ architecture/
      │  │  ├─ propose.md
      │  │  ├─ refine.md
      │  │  └─ review.md
      │  └─ schematic/
      │     ├─ plan.md
      │     └─ validate.md
      │
      ├─ tools/
      │  ├─ __init__.py
      │  ├─ base.py
      │  ├─ registry.py
      │  ├─ result.py
      │  ├─ kicad/
      │  │  ├─ __init__.py
      │  │  ├─ schematic_tool.py
      │  │  ├─ pcb_tool.py
      │  │  ├─ library_tool.py
      │  │  └─ export_tool.py
      │  ├─ parts/
      │  │  ├─ __init__.py
      │  │  ├─ search_tool.py
      │  │  └─ substitute_tool.py
      │  └─ rulecheck/
      │     ├─ __init__.py
      │     ├─ erc_tool.py
      │     ├─ drc_tool.py
      │     └─ constraint_check_tool.py
      │
      ├─ memory/
      │  ├─ __init__.py
      │  ├─ conversation_memory.py
      │  ├─ design_memory.py
      │  ├─ summary_memory.py
      │  └─ compression.py
      │
      ├─ execution/
      │  ├─ __init__.py
      │  ├─ executor.py
      │  ├─ dispatcher.py
      │  ├─ action_models.py
      │  └─ guards.py
      │
      ├─ infra/
      │  ├─ __init__.py
      │  ├─ llm/
      │  │  ├─ __init__.py
      │  │  ├─ client.py
      │  │  ├─ structured_output.py
      │  │  └─ retries.py
      │  ├─ storage/
      │  │  ├─ __init__.py
      │  │  ├─ project_repo.py
      │  │  ├─ session_repo.py
      │  │  └─ artifact_repo.py
      │  ├─ logging/
      │  │  ├─ __init__.py
      │  │  └─ logger.py
      │  └─ serialization/
      │     ├─ __init__.py
      │     ├─ json_codec.py
      │     └─ yaml_codec.py
      │
      ├─ evaluation/
      │  ├─ __init__.py
      │  ├─ cases.py
      │  ├─ scorers.py
      │  └─ regression.py
      │
      └─ utils/
         ├─ __init__.py
         ├─ ids.py
         ├─ time.py
         └─ text.py
```