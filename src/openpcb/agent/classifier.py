"""Requirement classifier for conversation-first routing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


@dataclass
class ClassificationResult:
    board_class: str
    board_family: str
    confidence: float
    reason: str
    should_route: bool

    def to_dict(self) -> dict[str, str | float | bool]:
        return {
            "board_class": self.board_class,
            "board_family": self.board_family,
            "confidence": self.confidence,
            "reason": self.reason,
            "should_route": self.should_route,
        }


class RequirementClassifier:
    """Rule-based requirement classifier for board-design requests."""

    _DESIGN_VERBS: ClassVar[tuple[str, ...]] = (
        "design",
        "build",
        "make",
        "create",
        "\u505a",
        "\u8bbe\u8ba1",
        "\u5f00\u53d1",
    )
    _BOARD_NOUNS: ClassVar[tuple[str, ...]] = (
        "board",
        "\u6838\u5fc3\u677f",
        "\u5f00\u53d1\u677f",
        "\u677f\u5361",
        "\u7535\u8def\u677f",
        "\u4e3b\u677f",
        "\u677f",
    )
    _CLASS_KEYWORDS: ClassVar[dict[str, tuple[str, ...]]] = {
        "mcu_core": (
            "stm32",
            "mcu",
            "\u5355\u7247\u673a",
            "\u6838\u5fc3\u677f",
            "\u5f00\u53d1\u677f",
            "esp32",
            "nrf52",
        ),
        "power": (
            "\u7535\u6e90",
            "\u4f9b\u7535",
            "\u7a33\u538b",
            "ldo",
            "buck",
            "boost",
            "dc-dc",
            "5v",
            "3.3v",
            "12v",
        ),
        "sensor_io": (
            "sensor",
            "\u4f20\u611f\u5668",
            "\u6e29\u5ea6",
            "\u538b\u529b",
            "\u91c7\u96c6",
            "adc",
            "imu",
            "gpio",
        ),
        "connectivity": (
            "wifi",
            "bluetooth",
            "ble",
            "\u4ee5\u592a\u7f51",
            "ethernet",
            "can",
            "rs485",
            "lora",
            "zigbee",
        ),
    }
    _FAMILY_KEYWORDS: ClassVar[dict[str, tuple[str, ...]]] = {
        "stm32": ("stm32", "f103", "f4", "h7", "g0"),
        "esp32": ("esp32", "esp-32"),
    }

    def classify(self, user_text: str) -> ClassificationResult:
        text = user_text.strip()
        lowered = text.lower()

        should_route = self._is_board_design_request(text, lowered)
        if not should_route:
            return ClassificationResult(
                board_class="other",
                board_family="unknown",
                confidence=0.0,
                reason="No clear board-design intent detected.",
                should_route=False,
            )

        board_family = self._detect_family(lowered)
        board_class, hits = self._detect_class(lowered, text)
        confidence = self._score_confidence(hits=hits, board_family=board_family, board_class=board_class)
        reason = self._build_reason(board_class=board_class, board_family=board_family, hits=hits)
        return ClassificationResult(
            board_class=board_class,
            board_family=board_family,
            confidence=confidence,
            reason=reason,
            should_route=True,
        )

    def _is_board_design_request(self, text: str, lowered: str) -> bool:
        has_verb = any(word in lowered or word in text for word in self._DESIGN_VERBS)
        has_board = any(word in lowered or word in text for word in self._BOARD_NOUNS)
        if has_verb and has_board:
            return True
        if "\u6838\u5fc3\u677f" in text or "\u5f00\u53d1\u677f" in text or "board" in lowered:
            return True
        return False

    def _detect_family(self, lowered: str) -> str:
        for family, keywords in self._FAMILY_KEYWORDS.items():
            if any(word in lowered for word in keywords):
                return family
        return "generic"

    def _detect_class(self, lowered: str, text: str) -> tuple[str, int]:
        best_class = "other"
        best_hits = 0
        for board_class, keywords in self._CLASS_KEYWORDS.items():
            hits = sum(1 for word in keywords if word in lowered or word in text)
            if hits > best_hits:
                best_class = board_class
                best_hits = hits
        return best_class, best_hits

    def _score_confidence(self, *, hits: int, board_family: str, board_class: str) -> float:
        if board_class == "other":
            return 0.45
        score = 0.55 + min(hits, 3) * 0.1
        if board_family != "generic":
            score += 0.1
        return min(score, 0.95)

    def _build_reason(self, *, board_class: str, board_family: str, hits: int) -> str:
        if board_class == "other":
            return "Board intent is detected, but category keywords are weak."
        return f"Matched {hits} category keywords; family={board_family}."
