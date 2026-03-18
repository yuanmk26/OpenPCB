from __future__ import annotations

import pytest
from pydantic import BaseModel, ConfigDict

from openpcb.infra.llm.structured_output import (
    StructuredOutputFormatError,
    StructuredOutputParser,
    StructuredOutputValidationError,
)


class DemoModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    count: int


def test_parse_json_object_with_plain_json() -> None:
    parser = StructuredOutputParser()
    text = '{"name": "uart", "count": 2}'

    result = parser.parse_json_object(text)

    assert result.data == {"name": "uart", "count": 2}
    assert result.json_data == {"name": "uart", "count": 2}
    assert result.raw_text == text


def test_parse_json_object_with_markdown_code_fence() -> None:
    parser = StructuredOutputParser()
    text = """```json
{"name": "uart", "count": 2}
```"""

    result = parser.parse_json_object(text)

    assert result.data == {"name": "uart", "count": 2}


def test_parse_json_object_with_extra_text_around_json() -> None:
    parser = StructuredOutputParser()
    text = """
Here is the extracted result:

{
  "name": "uart",
  "count": 2
}

Please review it.
"""

    result = parser.parse_json_object(text)

    assert result.data == {"name": "uart", "count": 2}


def test_parse_model_success() -> None:
    parser = StructuredOutputParser()
    text = '{"name": "uart", "count": 2}'

    result = parser.parse_model(text, DemoModel)

    assert isinstance(result.data, DemoModel)
    assert result.data.name == "uart"
    assert result.data.count == 2


def test_parse_model_validation_error() -> None:
    parser = StructuredOutputParser()
    text = '{"name": "uart", "count": "abc"}'

    with pytest.raises(StructuredOutputValidationError):
        parser.parse_model(text, DemoModel)


def test_parse_json_object_empty_text_error() -> None:
    parser = StructuredOutputParser()

    with pytest.raises(StructuredOutputFormatError):
        parser.parse_json_object("   ")


def test_parse_json_object_invalid_json_error() -> None:
    parser = StructuredOutputParser()
    text = "this is not json"

    with pytest.raises(StructuredOutputFormatError):
        parser.parse_json_object(text)


def test_build_json_response_format() -> None:
    parser = StructuredOutputParser()
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
        },
        "required": ["name"],
        "additionalProperties": False,
    }

    result = parser.build_json_response_format(
        schema=schema,
        name="demo_output",
        strict=True,
    )

    assert result["type"] == "json_schema"
    assert result["json_schema"]["name"] == "demo_output"
    assert result["json_schema"]["schema"] == schema
    assert result["json_schema"]["strict"] is True