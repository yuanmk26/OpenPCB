from openpcb.agent.classifier import RequirementClassifier


def test_classify_stm32_core_board() -> None:
    classifier = RequirementClassifier()
    result = classifier.classify("\u6211\u60f3\u8bbe\u8ba1\u4e00\u4e2aSTM32\u6838\u5fc3\u677f")
    assert result.should_route is True
    assert result.board_class == "mcu_core"
    assert result.board_family == "stm32"
    assert result.confidence >= 0.6


def test_classify_power_board() -> None:
    classifier = RequirementClassifier()
    result = classifier.classify("\u8bf7\u5e2e\u6211\u505a\u4e00\u4e2a5V\u8f6c3.3V\u7535\u6e90\u677f")
    assert result.should_route is True
    assert result.board_class == "power"
    assert result.board_family == "generic"


def test_classify_non_board_text() -> None:
    classifier = RequirementClassifier()
    result = classifier.classify("\u4f60\u597d\uff0c\u4eca\u5929\u8fc7\u5f97\u600e\u4e48\u6837")
    assert result.should_route is False
    assert result.board_class == "other"
    assert result.board_family == "unknown"
    assert result.confidence == 0.0
