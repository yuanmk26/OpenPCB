import pytest

from openpcb.agent.planner import extract_json_payload, parse_project_spec_from_json
from openpcb.utils.errors import InputError


def test_extract_json_from_fenced_block() -> None:
    payload = extract_json_payload("```json\n{\"name\":\"demo\",\"requirements\":\"x\",\"modules\":[]}\n```")
    assert payload.startswith("{")


def test_parse_project_spec_from_json_success() -> None:
    spec = parse_project_spec_from_json(
        "{\"name\":\"demo\",\"description\":\"d\",\"requirements\":\"r\",\"modules\":[]}",
        project_name="demo",
    )
    assert spec.name == "demo"


def test_parse_project_spec_from_json_invalid() -> None:
    with pytest.raises(InputError):
        parse_project_spec_from_json("not-json", project_name="demo")
