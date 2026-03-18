from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from openpcb.domain.requirements.models import BoardType, RequirementSpec


@dataclass(slots=True)
class RequirementValidationResult:
    """
    Result of business-level requirement validation.

    This is not schema validation. Schema validation is handled by Pydantic.
    This object answers a different question:

    "Given a structurally valid RequirementSpec, is it complete enough for the
    next workflow stage, and if not, what is still missing?"
    """

    missing_fields: list[str]
    clarification_questions: list[str]

    @property
    def is_complete(self) -> bool:
        """
        Whether the current requirement spec is complete enough.
        """
        return len(self.missing_fields) == 0


class RequirementValidator:
    """
    Business-level validator for RequirementSpec.

    Design goals:
    1. Keep MVP implementation simple
    2. Avoid hard-coding all logic into long if/elif chains
    3. Make future board-type expansion easier
    4. Separate "what fields are required" from "how to ask about them"
    """

    FIELD_QUESTION_TEMPLATES: dict[str, str] = {
        "board_type": "What type of board do you want to design?",
        "power_input": "How is the board powered? (e.g. USB, battery, header power)",
        "mcu.family": "Which MCU family do you want? (e.g. STM32, ESP32, GD32)",
    }

    BOARD_REQUIRED_FIELDS: dict[BoardType, list[str]] = {
        BoardType.MCU_MINIMUM_SYSTEM: [
            "power_input",
            "mcu.family",
        ],
    }

    def __init__(self) -> None:
        self._field_checkers: dict[str, Callable[[RequirementSpec], bool]] = {
            "board_type": self._is_board_type_missing,
            "power_input": self._is_power_input_missing,
            "mcu.family": self._is_mcu_family_missing,
        }

    def validate(self, spec: RequirementSpec) -> RequirementValidationResult:
        """
        Validate a RequirementSpec at the business-rule level.

        Validation strategy:
        1. If board_type is unknown, ask for board type first
        2. Otherwise, load required fields for that board type
        3. Check each required field using field-specific checkers
        4. Generate clarification questions for missing fields

        Args:
            spec: The structured requirement specification to validate.

        Returns:
            RequirementValidationResult
        """
        missing_fields: list[str] = []
        clarification_questions: list[str] = []

        if self._is_board_type_missing(spec):
            missing_fields.append("board_type")
            clarification_questions.append(
                self._question_for("board_type")
            )
            return RequirementValidationResult(
                missing_fields=missing_fields,
                clarification_questions=clarification_questions,
            )

        required_fields = self.BOARD_REQUIRED_FIELDS.get(spec.board_type, [])

        for field_name in required_fields:
            if self._is_field_missing(spec, field_name):
                missing_fields.append(field_name)
                clarification_questions.append(self._question_for(field_name))

        clarification_questions = self._append_contextual_questions(
            spec=spec,
            missing_fields=missing_fields,
            clarification_questions=clarification_questions,
        )

        return RequirementValidationResult(
            missing_fields=missing_fields,
            clarification_questions=clarification_questions,
        )

    def _is_field_missing(self, spec: RequirementSpec, field_name: str) -> bool:
        """
        Check whether a specific normalized field is missing.

        This method routes to field-specific checker functions so that:
        - field logic stays explicit
        - future expansion is easier
        - we avoid giant nested if/else blocks in validate()
        """
        checker = self._field_checkers.get(field_name)
        if checker is None:
            return False
        return checker(spec)

    def _question_for(self, field_name: str) -> str:
        """
        Return a user-facing clarification question for a missing field.
        """
        return self.FIELD_QUESTION_TEMPLATES.get(
            field_name,
            f"Please provide information for: {field_name}",
        )

    def _append_contextual_questions(
        self,
        *,
        spec: RequirementSpec,
        missing_fields: list[str],
        clarification_questions: list[str],
    ) -> list[str]:
        """
        Add non-mandatory but useful follow-up questions.

        These questions are not treated as required-field failures, but they help
        the agent collect better design information.

        Current MVP behavior:
        - For MCU minimum system boards, if interfaces are not specified at all,
          ask one general question about needed interfaces.
        """
        questions = list(clarification_questions)

        if (
            spec.board_type == BoardType.MCU_MINIMUM_SYSTEM
            and not spec.interfaces
            and "What interfaces do you need? (e.g. UART, I2C, SPI)" not in questions
        ):
            questions.append("What interfaces do you need? (e.g. UART, I2C, SPI)")

        return questions

    # ------------------------------------------------------------------
    # Field-specific missing checkers
    # ------------------------------------------------------------------

    def _is_board_type_missing(self, spec: RequirementSpec) -> bool:
        return spec.board_type == BoardType.UNKNOWN

    def _is_power_input_missing(self, spec: RequirementSpec) -> bool:
        return spec.power_input is None

    def _is_mcu_family_missing(self, spec: RequirementSpec) -> bool:
        return spec.mcu is None or spec.mcu.family is None