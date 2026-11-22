from pathlib import Path

import pytest

from harness.tasks import TOOLS, load_tasks, task_prompt, validate_task

ROOT = Path(__file__).resolve().parent.parent


def test_loads_all_tasks():
    tasks = load_tasks(ROOT / "tasks")
    assert len(tasks) == 12
    assert len({task["id"] for task in tasks}) == 12


def test_every_expected_tool_is_supported():
    tasks = load_tasks(ROOT / "tasks")
    assert {task["expected"]["tool"] for task in tasks} <= TOOLS


def test_task_prompt_contains_goal_url_and_elements():
    task = load_tasks(ROOT / "tasks")[0]
    prompt = task_prompt(task)
    assert task["goal"] in prompt
    assert task["observation"]["url"] in prompt
    assert "Docs" in prompt


def test_missing_goal_is_rejected():
    with pytest.raises(ValueError, match="missing goal"):
        validate_task(
            {
                "id": "x",
                "observation": {"url": "https://x"},
                "expected": {"tool": "finish"},
            }
        )


def test_unknown_tool_is_rejected():
    with pytest.raises(ValueError, match="expected.tool"):
        validate_task(
            {
                "id": "x",
                "goal": "g",
                "observation": {"url": "https://x"},
                "expected": {"tool": "teleport"},
            }
        )


def test_negative_budget_is_rejected():
    with pytest.raises(ValueError, match="budget.steps"):
        validate_task(
            {
                "id": "x",
                "goal": "g",
                "observation": {"url": "https://x"},
                "expected": {"tool": "finish"},
                "budget": {"steps": 0},
            }
        )


def test_duplicate_ids_are_rejected(tmp_path):
    body = (
        "id: same\n"
        "goal: g\n"
        "observation:\n  url: https://x\n"
        "expected:\n  tool: finish\n"
    )
    (tmp_path / "a.yaml").write_text(body, encoding="utf-8")
    (tmp_path / "b.yaml").write_text(body, encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate"):
        load_tasks(tmp_path)
