from openpcb.agent.component_recommender import ComponentRecommendationService


def test_component_catalog_loader_and_detect_part() -> None:
    service = ComponentRecommendationService()
    items = service.load_catalog("mcu")
    assert items
    assert any(item["part_number"] == "STM32F407VET6" for item in items)

    matched = service.detect_part_number("我想直接用 STM32F407VET6", category="mcu")
    assert matched is not None
    assert matched["part_number"] == "STM32F407VET6"


def test_component_recommendation_matcher_prefers_expected_part() -> None:
    service = ComponentRecommendationService()
    result = service.recommend(
        "power",
        {
            "topology": "Buck 降压",
            "input_output": "12V 转 5V",
            "output_current": "大电流（>=2A）",
            "priority": "效率优先",
        },
    )
    assert result.candidates
    assert result.candidates[0].part_number == "TPS54331"


def test_component_category_detection_only_for_mcu_core() -> None:
    service = ComponentRecommendationService()
    assert service.detect_category(board_class="mcu_core", text="帮我推荐一个 CAN 收发器") == "transceiver"
    assert service.detect_category(board_class="power", text="帮我推荐一个 CAN 收发器") is None
