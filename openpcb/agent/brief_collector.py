"""Template-driven architecture brief collector."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from openpcb.utils.errors import InputError


@dataclass
class BriefCollectResult:
    next_question: str | None
    options: list[str]
    updated_brief: dict[str, str]
    missing_fields: list[str]
    is_complete: bool
    retry_reason: str | None = None
    answered_field: str | None = None
    current_field: str | None = None
    template_id: str = ""
    template_version: str = ""


class ArchitectureBriefCollector:
    """Collect architecture brief fields by board-class template."""

    def __init__(self, template_root: Path | None = None) -> None:
        default_root = Path(__file__).resolve().parent / "templates" / "architecture_brief"
        self.template_root = template_root or default_root
        self._template_cache: dict[str, dict[str, Any]] = {}

    def required_fields(self, board_class: str) -> list[str]:
        template = self._load_template(board_class)
        return list(template["required_fields"])

    def missing_fields(self, brief: dict[str, str], board_class: str = "generic") -> list[str]:
        fields = self.required_fields(board_class)
        return [field for field in fields if not brief.get(field, "").strip()]

    def label_for(self, field: str, board_class: str = "generic") -> str:
        template = self._load_template(board_class)
        question = template["question_map"][field]
        return str(question["label"])

    def collect(
        self,
        *,
        board_class: str,
        board_family: str,
        user_text: str,
        brief: dict[str, str],
        pending_field: str | None,
        pending_options: list[str] | None = None,
        expect_custom_input: bool = False,
    ) -> BriefCollectResult:
        _ = board_family
        template = self._load_template(board_class)
        question_map: dict[str, dict[str, Any]] = template["question_map"]
        required_fields: list[str] = list(template["required_fields"])
        updated = dict(brief)

        retry_reason: str | None = None
        answered_field = pending_field

        text = user_text.strip()
        if pending_field and text:
            question = question_map[pending_field]
            value, retry_reason = self._parse_answer(
                text=text,
                question=question,
                pending_options=pending_options or [],
                expect_custom_input=expect_custom_input,
            )
            if value is not None:
                updated[pending_field] = value

        missing = [field for field in required_fields if not updated.get(field, "").strip()]
        if not missing:
            return BriefCollectResult(
                next_question=None,
                options=[],
                updated_brief=updated,
                missing_fields=[],
                is_complete=True,
                retry_reason=None,
                answered_field=answered_field,
                current_field=None,
                template_id=str(template["template_id"]),
                template_version=str(template["version"]),
            )

        field = pending_field if retry_reason and pending_field else missing[0]
        question = question_map[field]
        index = required_fields.index(field) + 1
        next_question = f"问题 {index}/{len(required_fields)}：{question['question']}"
        options = [str(item) for item in question["options"]]
        return BriefCollectResult(
            next_question=next_question,
            options=options,
            updated_brief=updated,
            missing_fields=missing,
            is_complete=False,
            retry_reason=retry_reason,
            answered_field=answered_field,
            current_field=field,
            template_id=str(template["template_id"]),
            template_version=str(template["version"]),
        )

    def custom_hint_for(self, board_class: str, field: str) -> str:
        template = self._load_template(board_class)
        return str(template["question_map"][field].get("custom_hint", "请输入自定义内容。"))

    def _template_path(self, board_class: str) -> Path:
        return self.template_root / f"{board_class}.json"

    def _load_template(self, board_class: str) -> dict[str, Any]:
        if board_class in self._template_cache:
            return self._template_cache[board_class]

        path = self._template_path(board_class)
        used_class = board_class
        if not path.exists():
            path = self._template_path("generic")
            used_class = "generic"
        if not path.exists():
            raise InputError(
                f"Architecture brief template not found for '{board_class}', and fallback 'generic' is missing."
            )

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise InputError(f"Invalid template JSON: {path}") from exc

        template = self._validate_template(data=data, path=path)
        self._template_cache[used_class] = template
        if used_class != board_class:
            self._template_cache[board_class] = template
        return template

    def _validate_template(self, *, data: dict[str, Any], path: Path) -> dict[str, Any]:
        for key in ("template_id", "version", "required_fields", "questions"):
            if key not in data:
                raise InputError(f"Template missing key '{key}': {path}")
        required_fields = data["required_fields"]
        questions = data["questions"]
        if not isinstance(required_fields, list) or not required_fields:
            raise InputError(f"Template 'required_fields' must be non-empty list: {path}")
        if not isinstance(questions, list) or not questions:
            raise InputError(f"Template 'questions' must be non-empty list: {path}")

        question_map: dict[str, dict[str, Any]] = {}
        for item in questions:
            if not isinstance(item, dict):
                raise InputError(f"Template question must be object: {path}")
            field = item.get("field")
            if not isinstance(field, str) or not field:
                raise InputError(f"Template question field invalid: {path}")
            for key in ("label", "question", "options", "custom_hint"):
                if key not in item:
                    raise InputError(f"Template question missing '{key}' for field '{field}': {path}")
            options = item["options"]
            if not isinstance(options, list) or len(options) != 3:
                raise InputError(f"Template question options must be exactly 3 for field '{field}': {path}")
            validation = item.get("validation", {})
            if validation and not isinstance(validation, dict):
                raise InputError(f"Template question validation must be object for field '{field}': {path}")
            question_map[field] = item

        for field in required_fields:
            if field not in question_map:
                raise InputError(f"Template required field '{field}' has no question definition: {path}")

        return {
            "template_id": data["template_id"],
            "version": data["version"],
            "required_fields": required_fields,
            "questions": questions,
            "question_map": question_map,
        }

    def _parse_answer(
        self,
        *,
        text: str,
        question: dict[str, Any],
        pending_options: list[str],
        expect_custom_input: bool,
    ) -> tuple[str | None, str | None]:
        if expect_custom_input:
            return self._validate_custom_answer(text=text, question=question)

        if text in {"1", "2", "3"}:
            index = int(text) - 1
            options = pending_options or [str(x) for x in question["options"]]
            if index >= len(options):
                return None, "选项编号超出范围，请重新选择。"
            return str(options[index]), None
        if text == "4":
            return None, "已选择自定义，请输入你的具体内容。"
        if text.isdigit():
            return None, "无效选项，请输入 1/2/3/4，或直接输入自定义文本。"
        return self._validate_custom_answer(text=text, question=question)

    def _validate_custom_answer(self, *, text: str, question: dict[str, Any]) -> tuple[str | None, str | None]:
        validation = question.get("validation", {}) or {}
        min_length = int(validation.get("min_length", 2))
        if len(text.strip()) < min_length:
            hint = str(question.get("custom_hint", "请输入更具体的信息。"))
            return None, f"输入内容过短。{hint}"
        return text.strip(), None

