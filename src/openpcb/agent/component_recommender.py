"""Rule-based component recommendation for architecture interaction."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RecommendationQuestion:
    key: str
    label: str
    prompt: str
    options: list[str]
    custom_hint: str


@dataclass(frozen=True)
class RecommendationCandidate:
    part_number: str
    vendor: str
    category: str
    summary: str
    score: int
    match_points: list[str]
    gaps: list[str]
    recommendation_level: str


@dataclass(frozen=True)
class RecommendationResult:
    category: str
    candidates: list[RecommendationCandidate]
    exact_match_count: int


class ComponentRecommendationService:
    """Local-catalog recommendation service for module-level component selection."""

    _CATEGORY_KEYWORDS: dict[str, tuple[str, ...]] = {
        "mcu": ("主控", "单片机", "mcu", "stm32", "esp32", "nrf52", "芯片"),
        "power": ("电源", "稳压", "ldo", "buck", "boost", "dc-dc", "降压", "升压", "供电"),
        "transceiver": ("can", "rs485", "485", "usb-uart", "usb uart", "usb转串口", "收发器", "transceiver"),
    }

    _QUESTION_BANK: dict[str, list[RecommendationQuestion]] = {
        "mcu": [
            RecommendationQuestion(
                key="performance",
                label="性能级别",
                prompt="这个主控大致需要什么性能级别？",
                options=["低功耗基础控制", "中等通用控制", "高性能实时控制"],
                custom_hint="请补充主频、实时性或性能级别，例如“主频 168MHz，要求浮点运算”。",
            ),
            RecommendationQuestion(
                key="memory",
                label="存储规模",
                prompt="Flash / RAM 大致需要什么规模？",
                options=["小容量（<=128KB Flash）", "中容量（256KB-512KB Flash）", "大容量（>=1MB Flash）"],
                custom_hint="请补充 Flash / RAM 规模，例如“512KB Flash，192KB RAM”。",
            ),
            RecommendationQuestion(
                key="interfaces",
                label="关键外设",
                prompt="这个主控必须覆盖哪些关键外设？",
                options=["UART + I2C + SPI", "USB + UART + CAN", "以太网 / 高速外设"],
                custom_hint="请补充关键外设，例如“USB、CAN、SPI、多个 UART”。",
            ),
            RecommendationQuestion(
                key="package",
                label="封装偏好",
                prompt="对封装或尺寸有什么偏好？",
                options=["小封装优先", "通用贴片封装", "引脚资源优先"],
                custom_hint="请补充封装偏好，例如“LQFP64，手焊友好”。",
            ),
        ],
        "power": [
            RecommendationQuestion(
                key="topology",
                label="电源类型",
                prompt="这个电源模块需要哪类拓扑？",
                options=["LDO 线性稳压", "Buck 降压", "Boost 升压"],
                custom_hint="请补充拓扑需求，例如“隔离式 24V 转 5V”。",
            ),
            RecommendationQuestion(
                key="input_output",
                label="输入输出",
                prompt="输入和输出电压大致是多少？",
                options=["5V 转 3.3V", "12V 转 5V", "24V 转 5V"],
                custom_hint="请补充输入输出，例如“9-24V 输入，5V 输出”。",
            ),
            RecommendationQuestion(
                key="output_current",
                label="输出电流",
                prompt="输出电流大致要多大？",
                options=["小电流（<=0.3A）", "中电流（0.5A-1A）", "大电流（>=2A）"],
                custom_hint="请补充输出电流，例如“持续 2A，峰值 3A”。",
            ),
            RecommendationQuestion(
                key="priority",
                label="优先级",
                prompt="更看重哪一类电源特性？",
                options=["低噪声", "效率优先", "成本优先"],
                custom_hint="请补充偏好，例如“效率优先，但 EMI 要可控”。",
            ),
        ],
        "transceiver": [
            RecommendationQuestion(
                key="protocol",
                label="协议类型",
                prompt="需要哪类收发器协议？",
                options=["CAN", "RS485", "USB 转 UART"],
                custom_hint="请补充协议类型，例如“隔离 CAN”或“3.3V RS485”。",
            ),
            RecommendationQuestion(
                key="isolation",
                label="隔离需求",
                prompt="是否需要隔离？",
                options=["不需要隔离", "建议预留隔离版本", "必须隔离"],
                custom_hint="请补充隔离要求，例如“工业现场，需要隔离”。",
            ),
            RecommendationQuestion(
                key="bus_voltage",
                label="总线/接口电压",
                prompt="总线侧或接口侧电压是什么？",
                options=["3.3V 逻辑", "5V 逻辑", "宽电压工业现场"],
                custom_hint="请补充逻辑电压或总线环境，例如“MCU 侧 3.3V，现场 24V 系统”。",
            ),
            RecommendationQuestion(
                key="data_rate",
                label="速率要求",
                prompt="对通信速率有什么要求？",
                options=["低速稳定", "中速通用", "高速优先"],
                custom_hint="请补充速率要求，例如“CAN 1Mbps”或“串口 921600”。",
            ),
        ],
    }

    def __init__(self, catalog_root: Path | None = None) -> None:
        default_root = Path(__file__).resolve().parent / "templates" / "component_catalog"
        self.catalog_root = catalog_root or default_root
        self._cache: dict[str, list[dict[str, Any]]] = {}

    def supported_categories(self) -> tuple[str, ...]:
        return tuple(self._QUESTION_BANK.keys())

    def questions_for(self, category: str) -> list[RecommendationQuestion]:
        return list(self._QUESTION_BANK.get(category, []))

    def load_catalog(self, category: str) -> list[dict[str, Any]]:
        if category in self._cache:
            return self._cache[category]
        path = self.catalog_root / f"{category}.json"
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        items = payload.get("items", [])
        if not isinstance(items, list):
            raise ValueError(f"Invalid catalog items: {path}")
        self._cache[category] = items
        return items

    def detect_category(self, *, board_class: str, text: str) -> str | None:
        if board_class != "mcu_core":
            return None
        lowered = text.lower()
        ranked: list[tuple[int, str]] = []
        for category, keywords in self._CATEGORY_KEYWORDS.items():
            hits = sum(1 for keyword in keywords if keyword in lowered or keyword in text)
            if hits > 0:
                ranked.append((hits, category))
        if not ranked:
            return None
        ranked.sort(reverse=True)
        return ranked[0][1]

    def detect_part_number(self, text: str, category: str | None = None) -> dict[str, Any] | None:
        search_categories = [category] if category else list(self.supported_categories())
        lowered = text.lower()
        for item_category in search_categories:
            if item_category is None:
                continue
            for item in self.load_catalog(item_category):
                part_number = str(item.get("part_number", ""))
                if part_number and part_number.lower() in lowered:
                    return item
        generic_part = re.search(r"\b[A-Z]{2,}[A-Z0-9\-]{3,}\b", text.upper())
        if not generic_part:
            return None
        token = generic_part.group(0)
        for item_category in search_categories:
            if item_category is None:
                continue
            for item in self.load_catalog(item_category):
                if str(item.get("part_number", "")).upper() == token:
                    return item
        return None

    def recommend(self, category: str, constraints: dict[str, Any]) -> RecommendationResult:
        scored: list[tuple[int, int, RecommendationCandidate]] = []
        exact_match_count = 0
        for item in self.load_catalog(category):
            candidate = self._score_item(category=category, item=item, constraints=constraints)
            gap_count = len(candidate.gaps)
            if gap_count == 0:
                exact_match_count += 1
            scored.append((candidate.score, -gap_count, candidate))
        scored.sort(key=lambda entry: (entry[0], entry[1], entry[2].part_number), reverse=True)
        top = [entry[2] for entry in scored[:3]]
        return RecommendationResult(category=category, candidates=top, exact_match_count=exact_match_count)

    def initial_state(self, category: str) -> dict[str, Any]:
        questions = self.questions_for(category)
        first = questions[0] if questions else None
        return {
            "active_module": category,
            "module_category": category,
            "collected_constraints": {},
            "candidate_parts": [],
            "selected_part": None,
            "status": "collecting",
            "question_index": 0,
            "current_question_key": first.key if first else None,
        }

    def serialize_candidate(self, candidate: RecommendationCandidate) -> dict[str, Any]:
        return {
            "part_number": candidate.part_number,
            "vendor": candidate.vendor,
            "category": candidate.category,
            "summary": candidate.summary,
            "score": candidate.score,
            "match_points": candidate.match_points,
            "gaps": candidate.gaps,
            "recommendation_level": candidate.recommendation_level,
        }

    def serialize_catalog_item(self, item: dict[str, Any]) -> dict[str, Any]:
        return {
            "part_number": str(item.get("part_number", "")),
            "vendor": str(item.get("vendor", "")),
            "category": str(item.get("category", "")),
            "summary": str(item.get("summary", "")),
            "key_specs": item.get("key_specs", {}),
            "package_options": item.get("package_options", []),
            "typical_use_cases": item.get("typical_use_cases", []),
            "constraints": item.get("constraints", {}),
            "priority_tags": item.get("priority_tags", []),
        }

    def _score_item(self, *, category: str, item: dict[str, Any], constraints: dict[str, Any]) -> RecommendationCandidate:
        match_points: list[str] = []
        gaps: list[str] = []
        score = 0
        for key, value in constraints.items():
            normalized_value = str(value).strip()
            if not normalized_value:
                continue
            matched, reason = self._match_constraint(category=category, item=item, key=key, value=normalized_value)
            if matched:
                score += 3
                match_points.append(reason)
            else:
                gaps.append(reason)

        priority_tags = [str(tag) for tag in item.get("priority_tags", [])]
        extra_notes = str(constraints.get("extra_notes", "")).lower()
        if extra_notes:
            extra_hits = [tag for tag in priority_tags if tag.lower() in extra_notes]
            if extra_hits:
                score += len(extra_hits)
                match_points.append(f"附加偏好匹配: {', '.join(extra_hits)}")

        recommendation_level = "A" if not gaps and score >= 9 else "B" if score >= 5 else "C"
        return RecommendationCandidate(
            part_number=str(item.get("part_number", "")),
            vendor=str(item.get("vendor", "")),
            category=str(item.get("category", category)),
            summary=str(item.get("summary", "")),
            score=score,
            match_points=match_points or ["基础能力匹配"],
            gaps=gaps,
            recommendation_level=recommendation_level,
        )

    def _match_constraint(self, *, category: str, item: dict[str, Any], key: str, value: str) -> tuple[bool, str]:
        lowered = value.lower()
        key_specs = item.get("key_specs", {})
        tags = [str(tag).lower() for tag in item.get("priority_tags", [])]
        summary = str(item.get("summary", "")).lower()
        package_options = [str(option).lower() for option in item.get("package_options", [])]

        if category == "mcu":
            interfaces = [str(token).lower() for token in key_specs.get("interfaces", [])]
            if key == "interfaces":
                matched = any(token in lowered for token in interfaces) or any(token in summary for token in lowered.split())
                return matched, f"关键外设: {value}" if matched else f"未完全覆盖关键外设: {value}"
            if key == "package":
                matched = any(option in lowered or lowered in option for option in package_options) or any(
                    tag in lowered for tag in ("小封装", "lqfp", "qfn", "引脚")
                ) and bool(package_options)
                return matched, f"封装偏好: {value}" if matched else f"封装偏好待确认: {value}"
            spec_value = str(key_specs.get(key, "")).lower()
            matched = spec_value and (spec_value in lowered or lowered in spec_value)
            return bool(matched), f"{key}: {value}" if matched else f"{key} 不完全匹配: {value}"

        if category == "power":
            input_range = str(key_specs.get("input_range", "")).lower()
            output = str(key_specs.get("output_voltage", "")).lower()
            topology = str(key_specs.get("topology", "")).lower()
            current_tag = str(key_specs.get("output_current", "")).lower()
            if key == "input_output":
                matched = any(token in input_range or token in output for token in lowered.replace("转", " ").split())
                return matched, f"输入输出: {value}" if matched else f"输入输出待确认: {value}"
            if key == "topology":
                matched = topology and (topology in lowered or lowered in topology)
                return bool(matched), f"拓扑: {value}" if matched else f"拓扑不匹配: {value}"
            if key == "output_current":
                matched = current_tag and (current_tag in lowered or lowered in current_tag)
                return bool(matched), f"输出电流: {value}" if matched else f"输出电流待确认: {value}"
            matched = any(tag in lowered for tag in tags)
            return matched, f"偏好: {value}" if matched else f"偏好不明显: {value}"

        protocol = str(key_specs.get("protocol", "")).lower()
        isolation = str(key_specs.get("isolation", "")).lower()
        logic = str(key_specs.get("logic_voltage", "")).lower()
        speed = str(key_specs.get("max_rate", "")).lower()
        if key == "protocol":
            matched = protocol and (protocol in lowered or lowered in protocol)
            return bool(matched), f"协议: {value}" if matched else f"协议不匹配: {value}"
        if key == "isolation":
            matched = isolation and (isolation in lowered or lowered in isolation)
            return bool(matched), f"隔离: {value}" if matched else f"隔离需求待确认: {value}"
        if key == "bus_voltage":
            matched = logic and any(token in logic for token in lowered.split())
            return bool(matched), f"接口电压: {value}" if matched else f"接口电压待确认: {value}"
        matched = speed and any(token in speed for token in lowered.split())
        return bool(matched), f"速率: {value}" if matched else f"速率待确认: {value}"
