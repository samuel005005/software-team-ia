from factory.progress import describe_tool


def test_describe_tool_with_path() -> None:
    text = describe_tool("read_file", {"path": "docs/TASKS.md"})
    assert "docs/TASKS.md" in text


def test_describe_tool_shell() -> None:
    text = describe_tool("Shell", {"command": "pytest -q"})
    assert "pytest" in text
