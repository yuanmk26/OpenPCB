"""Architecture brief collector for conversation routing."""

from __future__ import annotations

from dataclasses import dataclass


BRIEF_REQUIRED_FIELDS: tuple[str, ...] = (
    "board_goal",
    "power_input",
    "key_interfaces",
    "performance_constraints",
    "size_constraints",
    "cost_priority",
)

BRIEF_FIELD_LABELS: dict[str, str] = {
    "board_goal": "板卡目标",
    "power_input": "输入电源",
    "key_interfaces": "关键接口",
    "performance_constraints": "性能约束",
    "size_constraints": "尺寸约束",
    "cost_priority": "成本优先级",
}

BRIEF_QUESTION_TEMPLATES: dict[str, str] = {
    "board_goal": "这块板主要用途是什么？要完成哪些核心功能？",
    "power_input": "输入电源条件是什么？例如 USB 5V、12V 适配器、电池供电等。",
    "key_interfaces": "需要哪些关键接口？例如 USB/UART/CAN/SPI/I2C/GPIO。",
    "performance_constraints": "有哪些性能约束？例如主频、实时性、精度、功耗。",
    "size_constraints": "尺寸或结构上有什么限制？例如长宽、层数、安装孔位置。",
    "cost_priority": "成本优先级是什么？低成本、平衡，还是高性能优先？",
}


@dataclass
class BriefCollectResult:
    next_question: str | None
    updated_brief: dict[str, str]
    missing_fields: list[str]
    is_complete: bool
    answered_field: str | None = None


class ArchitectureBriefCollector:
    """Collect required architecture fields in single-question rounds."""

    def required_fields(self) -> list[str]:
        return list(BRIEF_REQUIRED_FIELDS)

    def missing_fields(self, brief: dict[str, str]) -> list[str]:
        missing: list[str] = []
        for field in BRIEF_REQUIRED_FIELDS:
            value = brief.get(field, "").strip()
            if not value:
                missing.append(field)
        return missing

    def label_for(self, field: str) -> str:
        return BRIEF_FIELD_LABELS.get(field, field)

    def next_field(self, brief: dict[str, str]) -> str | None:
        missing = self.missing_fields(brief)
        return missing[0] if missing else None

    def question_for(self, field: str, index: int, total: int) -> str:
        template = BRIEF_QUESTION_TEMPLATES.get(field, "请补充该项信息。")
        return f"问题 {index}/{total}：{template}"

    def collect(
        self,
        *,
        board_class: str,
        board_family: str,
        user_text: str,
        brief: dict[str, str],
        pending_field: str | None,
    ) -> BriefCollectResult:
        _ = (board_class, board_family)
        updated = dict(brief)

        answered_field = pending_field
        text = user_text.strip()
        if pending_field and text:
            updated[pending_field] = text

        missing = self.missing_fields(updated)
        if not missing:
            return BriefCollectResult(
                next_question=None,
                updated_brief=updated,
                missing_fields=[],
                is_complete=True,
                answered_field=answered_field,
            )

        field = missing[0]
        index = len(BRIEF_REQUIRED_FIELDS) - len(missing) + 1
        question = self.question_for(field=field, index=index, total=len(BRIEF_REQUIRED_FIELDS))
        return BriefCollectResult(
            next_question=question,
            updated_brief=updated,
            missing_fields=missing,
            is_complete=False,
            answered_field=answered_field,
        )

