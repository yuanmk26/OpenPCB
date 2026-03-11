from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

FieldPriority = Literal["P0", "P1", "P2"]
FieldSource = Literal["user_confirmed", "system_inferred", "unknown"]


@dataclass(frozen=True)
class FieldSpec:
    key: str
    label: str
    priority: FieldPriority
    question: str
    options: list[str]
    custom_hint: str
    key_p1: bool = False


@dataclass
class QuestionItem:
    key: str
    label: str
    priority: FieldPriority
    question: str
    options: list[str]


@dataclass
class ArchitectureCollectResult:
    updated_values: dict[str, str]
    updated_sources: dict[str, FieldSource]
    answered_field: str | None
    retry_reason: str | None
    active_field: str | None
    active_options: list[str]
    next_questions: list[QuestionItem]
    assumptions: list[str]
    stage_status: dict[str, object]


class ArchitectureSchemaCollector:
    """Schema-gap-driven collector for architecture interaction."""

    def __init__(self) -> None:
        self._priority_rank = {"P0": 0, "P1": 1, "P2": 2}

    def specs_for(self, board_class: str) -> list[FieldSpec]:
        if board_class == "mcu_core":
            return [
                FieldSpec(
                    key="board_type",
                    label="板卡类型",
                    priority="P0",
                    question="这块板的类型是什么？",
                    options=["MCU 核心板", "MCU 最小系统板", "MCU 控制主板"],
                    custom_hint="请写明板卡定位，例如“STM32 控制核心板”。",
                ),
                FieldSpec(
                    key="use_case",
                    label="使用场景",
                    priority="P0",
                    question="主要使用场景是什么？",
                    options=["通用控制", "电机/运动控制", "采集与通信"],
                    custom_hint="请描述核心业务场景，例如“机器人底盘控制”。",
                ),
                FieldSpec(
                    key="main_controller_type",
                    label="主控系列",
                    priority="P0",
                    question="主控系列选择是什么？",
                    options=["STM32", "ESP32", "NXP LPC"],
                    custom_hint="请填写主控系列，例如“STM32”。",
                ),
                FieldSpec(
                    key="main_controller_part",
                    label="主控型号",
                    priority="P0",
                    question="主控具体型号是什么？",
                    options=["STM32F103", "STM32F407", "STM32H743"],
                    custom_hint="请填写完整主控型号，例如“STM32F103C8T6”。",
                ),
                FieldSpec(
                    key="power.input_sources",
                    label="输入电源",
                    priority="P0",
                    question="输入电源来源是什么？",
                    options=["USB 5V", "12V 适配器", "电池供电"],
                    custom_hint="请写明电压与来源，例如“USB 5V + 12V 适配器”。",
                ),
                FieldSpec(
                    key="interfaces",
                    label="关键接口",
                    priority="P0",
                    question="需要哪些关键接口？",
                    options=["USB + UART", "CAN + UART", "SPI + I2C"],
                    custom_hint="请列出关键接口组合，例如“USB, UART, CAN, I2C”。",
                ),
                FieldSpec(
                    key="clock",
                    label="时钟方案",
                    priority="P1",
                    question="时钟方案是什么？",
                    options=["外部 8MHz 晶振", "内部 RC", "外部有源时钟"],
                    custom_hint="请描述时钟来源和频率配置。",
                    key_p1=True,
                ),
                FieldSpec(
                    key="reset_boot",
                    label="复位与启动",
                    priority="P1",
                    question="复位和 Boot 方案是什么？",
                    options=["独立 RESET + BOOT0", "仅 RESET", "自动下载电路"],
                    custom_hint="请描述 Reset/Boot 电路策略。",
                    key_p1=True,
                ),
                FieldSpec(
                    key="assembly_mode",
                    label="装配方式",
                    priority="P1",
                    question="装配方式是什么？",
                    options=["SMT 贴片", "DIP 直插", "混合装配"],
                    custom_hint="请描述制造装配方式，例如“SMT 双面贴片”。",
                    key_p1=True,
                ),
                FieldSpec(
                    key="reference_design_available",
                    label="参考设计",
                    priority="P2",
                    question="是否有可参考的设计？",
                    options=["有官方参考设计", "有历史项目可复用", "暂无参考设计"],
                    custom_hint="请说明参考来源，例如“STM32 Nucleo 原理图”。",
                ),
            ]

        return [
            FieldSpec("board_type", "板卡类型", "P0", "板卡类型是什么？", ["控制板", "电源板", "接口板"], "请补充板卡类型。"),
            FieldSpec("use_case", "使用场景", "P0", "主要应用场景是什么？", ["验证原型", "工程样机", "量产产品"], "请描述使用场景。"),
            FieldSpec("power.input_sources", "输入电源", "P0", "输入电源来源是什么？", ["USB 5V", "12V", "电池"], "请补充电源来源。"),
            FieldSpec("interfaces", "关键接口", "P1", "关键接口有哪些？", ["USB+UART", "SPI+I2C", "CAN+RS485"], "请补充关键接口。"),
            FieldSpec("assembly_mode", "装配方式", "P2", "装配方式是什么？", ["SMT", "DIP", "混合"], "请补充装配方式。"),
        ]

    def infer(
        self,
        *,
        requirement: str,
        board_class: str,
        board_family: str,
        values: dict[str, str],
        sources: dict[str, FieldSource],
    ) -> tuple[dict[str, str], dict[str, FieldSource]]:
        updated_values = dict(values)
        updated_sources = dict(sources)
        lower = requirement.lower()

        def set_if_unknown(key: str, value: str) -> None:
            if not value:
                return
            if updated_sources.get(key, "unknown") == "unknown":
                updated_values[key] = value
                updated_sources[key] = "system_inferred"

        if board_class == "mcu_core":
            set_if_unknown("board_type", "MCU 核心板")
        if board_family and board_family != "generic":
            set_if_unknown("main_controller_type", board_family.upper())

        part = re.search(r"\b(stm32[a-z0-9]+|esp32[a-z0-9-]*)\b", lower)
        if part:
            set_if_unknown("main_controller_part", part.group(1).upper())

        power_tags: list[str] = []
        if "usb" in lower or "5v" in lower:
            power_tags.append("USB 5V")
        if "12v" in lower:
            power_tags.append("12V")
        if "24v" in lower:
            power_tags.append("24V")
        if "battery" in lower or "电池" in requirement:
            power_tags.append("电池")
        if power_tags:
            set_if_unknown("power.input_sources", ", ".join(dict.fromkeys(power_tags)))

        interface_tokens = [
            ("USB", "usb"),
            ("UART", "uart"),
            ("CAN", "can"),
            ("SPI", "spi"),
            ("I2C", "i2c"),
            ("RS485", "rs485"),
        ]
        interfaces = [label for label, token in interface_tokens if token in lower]
        if interfaces:
            set_if_unknown("interfaces", ", ".join(interfaces))

        if "晶振" in requirement or "crystal" in lower:
            set_if_unknown("clock", "外部晶振")
        if "boot0" in lower or "reset" in lower or "复位" in requirement:
            set_if_unknown("reset_boot", "含复位与启动控制")
        if "smt" in lower or "贴片" in requirement:
            set_if_unknown("assembly_mode", "SMT")
        if "dip" in lower or "直插" in requirement:
            set_if_unknown("assembly_mode", "DIP")
        if "参考设计" in requirement or "reference design" in lower:
            set_if_unknown("reference_design_available", "有参考设计")

        return updated_values, updated_sources

    def collect(
        self,
        *,
        board_class: str,
        board_family: str,
        user_text: str,
        values: dict[str, str],
        sources: dict[str, FieldSource],
        pending_field: str | None,
        pending_options: list[str] | None,
        expect_custom_input: bool,
    ) -> ArchitectureCollectResult:
        specs = self.specs_for(board_class)
        spec_map = {s.key: s for s in specs}
        updated_values = dict(values)
        updated_sources = dict(sources)

        for spec in specs:
            updated_sources.setdefault(spec.key, "unknown")

        retry_reason: str | None = None
        answered_field = pending_field

        text = user_text.strip()
        if pending_field and text:
            spec = spec_map[pending_field]
            value, retry_reason = self._parse_answer(
                text=text,
                options=pending_options or spec.options,
                custom_hint=spec.custom_hint,
                expect_custom_input=expect_custom_input,
            )
            if value is not None:
                updated_values[pending_field] = value
                updated_sources[pending_field] = "user_confirmed"

        missing_specs = self._missing_specs(specs, updated_sources)
        next_questions = [
            QuestionItem(
                key=s.key,
                label=s.label,
                priority=s.priority,
                question=s.question,
                options=s.options,
            )
            for s in missing_specs[:3]
        ]

        active_spec = None
        if retry_reason and pending_field:
            active_spec = spec_map[pending_field]
        elif next_questions:
            active_spec = spec_map[next_questions[0].key]

        assumptions = [
            f"{s.label}: {updated_values.get(s.key, '')}"
            for s in specs
            if updated_sources.get(s.key, "unknown") == "system_inferred"
        ]

        stage_status = self._stage_status(specs, updated_sources)

        return ArchitectureCollectResult(
            updated_values=updated_values,
            updated_sources=updated_sources,
            answered_field=answered_field,
            retry_reason=retry_reason,
            active_field=active_spec.key if active_spec else None,
            active_options=active_spec.options if active_spec else [],
            next_questions=next_questions,
            assumptions=assumptions,
            stage_status=stage_status,
        )

    def label_for(self, board_class: str, key: str) -> str:
        for spec in self.specs_for(board_class):
            if spec.key == key:
                return spec.label
        return key

    def key_p1_fields(self, board_class: str) -> list[str]:
        return [s.key for s in self.specs_for(board_class) if s.priority == "P1" and s.key_p1]

    def _missing_specs(self, specs: list[FieldSpec], sources: dict[str, FieldSource]) -> list[FieldSpec]:
        missing = [s for s in specs if sources.get(s.key, "unknown") == "unknown"]
        return sorted(missing, key=lambda s: (self._priority_rank[s.priority], specs.index(s)))

    def _stage_status(self, specs: list[FieldSpec], sources: dict[str, FieldSource]) -> dict[str, object]:
        p0 = [s.key for s in specs if s.priority == "P0"]
        key_p1 = [s.key for s in specs if s.priority == "P1" and s.key_p1]
        architecture_ready = all(sources.get(k, "unknown") != "unknown" for k in p0)
        schematic_ready = architecture_ready and all(sources.get(k, "unknown") != "unknown" for k in key_p1)
        layout_ready = schematic_ready and all(sources.get(s.key, "unknown") != "unknown" for s in specs if s.priority != "P2")

        missing = [s.key for s in self._missing_specs(specs, sources)]
        blocking_missing = [
            k
            for k in (p0 + key_p1)
            if sources.get(k, "unknown") == "unknown"
        ]
        assumptions = [k for k, v in sources.items() if v == "system_inferred"]
        return {
            "current_stage": "architecture" if not schematic_ready else "schematic",
            "architecture_ready": architecture_ready,
            "schematic_ready": schematic_ready,
            "layout_ready": layout_ready,
            "missing_fields": missing,
            "blocking_missing_fields": blocking_missing,
            "assumptions": assumptions,
        }

    def _parse_answer(
        self,
        *,
        text: str,
        options: list[str],
        custom_hint: str,
        expect_custom_input: bool,
    ) -> tuple[str | None, str | None]:
        if expect_custom_input:
            return self._validate_custom(text=text, custom_hint=custom_hint)
        if text in {"1", "2", "3"}:
            idx = int(text) - 1
            if idx >= len(options):
                return None, "选项超出范围，请输入 1/2/3/4。"
            return options[idx], None
        if text == "4":
            return None, "已选择自定义，请输入你的具体内容。"
        if text.isdigit():
            return None, "无效选项，请输入 1/2/3/4，或直接输入文本。"
        return self._validate_custom(text=text, custom_hint=custom_hint)

    def _validate_custom(self, *, text: str, custom_hint: str) -> tuple[str | None, str | None]:
        value = text.strip()
        if len(value) < 2:
            return None, f"输入内容过短。{custom_hint}"
        return value, None
