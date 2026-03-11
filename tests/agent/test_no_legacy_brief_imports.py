from pathlib import Path


LEGACY_SYMBOLS = [
    "ArchitectureBriefCollector",
    "BriefQuestionGenerator",
    "openpcb.agent.brief_collector",
    "openpcb.agent.brief_question_generator",
]


def test_no_legacy_brief_imports_in_repo() -> None:
    root = Path(__file__).resolve().parents[2]
    py_files = [p for p in root.rglob("*.py") if ".git" not in p.parts and "__pycache__" not in p.parts]
    for path in py_files:
        if path.name == "test_no_legacy_brief_imports.py":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for symbol in LEGACY_SYMBOLS:
            assert symbol not in text, f"legacy symbol '{symbol}' found in {path}"
