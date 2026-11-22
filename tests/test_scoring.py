from harness.scoring import normalize, score_action

TASK = {
    "id": "t",
    "expected": {"tool": "click", "args": {"text": "Next"}},
}


def test_exact_match_passes():
    assert score_action(TASK, {"tool": "click", "args": {"text": "Next"}})["passed"] is True


def test_case_and_spaces_are_normalized():
    verdict = score_action(TASK, {"tool": "click", "args": {"text": "  next "}})
    assert verdict["passed"] is True


def test_wrong_tool_fails_with_reason():
    verdict = score_action(TASK, {"tool": "scroll", "args": {"text": "Next"}})
    assert verdict["passed"] is False
    assert "tool" in verdict["reason"]


def test_wrong_arg_fails_with_reason():
    verdict = score_action(TASK, {"tool": "click", "args": {"text": "Previous"}})
    assert verdict["passed"] is False
    assert "text" in verdict["reason"]


def test_missing_action_fails():
    assert score_action(TASK, {})["passed"] is False


def test_normalize_collapses_whitespace():
    assert normalize("  A   B  ") == "a b"
