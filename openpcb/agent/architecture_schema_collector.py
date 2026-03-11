"""Template-driven schema gap collector for architecture interaction."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from openpcb.utils.errors import InputError

FieldPriority = Literal["P0", "P1", "P2"]
FieldSource = Literal["user_confirmed", "system_inferred", "unknown"]


@dataclass(frozen=True)
class FieldSpec:
    key: str
    label: str
    priority: FieldPriority
    question_seed: str
    options: list[str]
    custom_hint: str
    key_p1: bool = False
    validation: dict[str, Any] | None = None


@dataclass
class QuestionItem:
    key: str
    label: str
    priority: FieldPriority
    question_seed: str
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
    template_id: str
    template_version: str


class TemplateLoader:
    """Load field templates by board class with generic fallback."""

    def __init__(self, template_root: Path | None = None) -> None:
        default_root = Path(__file__).resolve().parent / "templates" / "architecture_fields"
        self.template_root = template_root or default_root
        self._cache: dict[str, dict[str, Any]] = {}

    def load(self, board_class: str) -> dict[str, Any]:
        if board_class in self._cache:
            return self._cache[board_class]

        path = self.template_root / f"{board_class}.json"
        used_class = board_class
        if not path.exists():
            path = self.template_root / "generic.json"
            used_class = "generic"
        if not path.exists():
            raise InputError(
                f"Architecture field template not found for '{board_class}', and fallback 'generic' is missing."
            )

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise InputError(f"Invalid JSON template: {path}") from exc

        template = self._validate_template(data, path)
        self._cache[used_class] = template
        if used_class != board_class:
            self._cache[board_class] = template
        return template

    def _validate_template(self, data: dict[str, Any], path: Path) -> dict[str, Any]:
        for key in ("template_id", "version", "required_fields", "fields"):
            if key not in data:
                raise InputError(f"Template missing key '{key}': {path}")

        required_fields = data["required_fields"]
        fields = data["fields"]
        if not isinstance(required_fields, list) or not required_fields:
            raise InputError(f"Template required_fields must be a non-empty list: {path}")
        if not isinstance(fields, list) or not fields:
            raise InputError(f"Template fields must be a non-empty list: {path}")

        field_map: dict[str, dict[str, Any]] = {}
        for item in fields:
            if not isinstance(item, dict):
                raise InputError(f"Template field entry must be object: {path}")
            for key in ("key", "label", "priority", "question_seed", "options", "custom_hint"):
                if key not in item:
                    raise InputError(f"Field definition missing '{key}' in {path}")
            if item["priority"] not in {"P0", "P1", "P2"}:
                raise InputError(f"Field priority must be P0/P1/P2, got '{item['priority']}' in {path}")
            if not isinstance(item["options"], list) or len(item["options"]) != 3:
                raise InputError(f"Field options must contain exactly 3 items in {path}")
            field_map[str(item["key"])] = item

        for key in required_fields:
            if key not in field_map:
                raise InputError(f"required_fields contains undefined key '{key}' in {path}")

        return {
            "template_id": str(data["template_id"]),
            "version": str(data["version"]),
            "required_fields": [str(x) for x in required_fields],
            "field_map": field_map,
        }


class ArchitectureSchemaCollector:
    """Schema-gap-driven collector powered by external board_class templates."""

    def __init__(self, template_root: Path | None = None) -> None:
        self.loader = TemplateLoader(template_root=template_root)
        self._priority_rank = {"P0": 0, "P1": 1, "P2": 2}

    def specs_for(self, board_class: str) -> list[FieldSpec]:
        template = self.loader.load(board_class)
        specs: list[FieldSpec] = []
        for key in template["required_fields"]:
            item = template["field_map"][key]
            specs.append(
                FieldSpec(
                    key=key,
                    label=str(item["label"]),
                    priority=item["priority"],
                    question_seed=str(item["question_seed"]),
                    options=[str(x) for x in item["options"]],
                    custom_hint=str(item["custom_hint"]),
                    key_p1=bool(item.get("key_p1", False)),
                    validation=item.get("validation", {}),
                )
            )
        return specs

    def template_info(self, board_class: str) -> tuple[str, str]:
        template = self.loader.load(board_class)
        return template["template_id"], template["version"]

    def infer(
        self,
        *,
        requirement: str,
        board_class: str,
        board_family: str,
        values: dict[str, str],
        sources: dict[str, FieldSource],
    ) -> tuple[dict[str, str], dict[str, FieldSource]]:
        specs = self.specs_for(board_class)
        key_set = {s.key for s in specs}

        updated_values = dict(values)
        updated_sources = dict(sources)
        lower = requirement.lower()

        def set_if_unknown(key: str, value: str) -> None:
            if key not in key_set or not value:
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
        _ = board_family
        specs = self.specs_for(board_class)
        spec_map = {s.key: s for s in specs}
        template_id, template_version = self.template_info(board_class)

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
                validation=spec.validation or {},
            )
            if value is not None:
                updated_values[pending_field] = value
                updated_sources[pending_field] = "user_confirmed"

        missing_specs = self._missing_specs(specs, updated_sources)
        # Single active question per round.
        next_questions = [
            QuestionItem(
                key=missing_specs[0].key,
                label=missing_specs[0].label,
                priority=missing_specs[0].priority,
                question_seed=missing_specs[0].question_seed,
                options=missing_specs[0].options,
            )
        ] if missing_specs else []

        active_spec: FieldSpec | None = None
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
            template_id=template_id,
            template_version=template_version,
        )

    def label_for(self, board_class: str, key: str) -> str:
        for spec in self.specs_for(board_class):
            if spec.key == key:
                return spec.label
        return key

    def _missing_specs(self, specs: list[FieldSpec], sources: dict[str, FieldSource]) -> list[FieldSpec]:
        missing = [s for s in specs if sources.get(s.key, "unknown") == "unknown"]
        return sorted(missing, key=lambda s: (self._priority_rank[s.priority], specs.index(s)))

    def _stage_status(self, specs: list[FieldSpec], sources: dict[str, FieldSource]) -> dict[str, object]:
        p0 = [s.key for s in specs if s.priority == "P0"]
        key_p1 = [s.key for s in specs if s.priority == "P1" and s.key_p1]

        architecture_ready = all(sources.get(k, "unknown") != "unknown" for k in p0)
        schematic_ready = architecture_ready and all(sources.get(k, "unknown") != "unknown" for k in key_p1)
        layout_ready = schematic_ready

        missing = [s.key for s in self._missing_specs(specs, sources)]
        blocking_missing = [k for k in (p0 + key_p1) if sources.get(k, "unknown") == "unknown"]
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
        validation: dict[str, Any],
    ) -> tuple[str | None, str | None]:
        if expect_custom_input:
            return self._validate_custom(text=text, custom_hint=custom_hint, validation=validation)

        if text in {"1", "2", "3"}:
            idx = int(text) - 1
            if idx >= len(options):
                return None, "选项超出范围，请输入 1/2/3/4。"
            return options[idx], None
        if text == "4":
            return None, "已选择自定义，请输入你的具体内容。"
        if text.isdigit():
            return None, "无效选项，请输入 1/2/3/4，或直接输入文本。"
        return self._validate_custom(text=text, custom_hint=custom_hint, validation=validation)

    def _validate_custom(self, *, text: str, custom_hint: str, validation: dict[str, Any]) -> tuple[str | None, str | None]:
        value = text.strip()
        min_length = int(validation.get("min_length", 2))
        if len(value) < min_length:
            return None, f"输入内容过短。{custom_hint}"
        return value, None
