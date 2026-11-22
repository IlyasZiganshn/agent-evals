from pathlib import Path

from harness.providers import constant_provider, oracle_provider
from harness.runner import render_table, run_all, summarize, write_json
from harness.tasks import load_tasks

ROOT = Path(__file__).resolve().parent.parent


def test_oracle_passes_every_task():
    tasks = load_tasks(ROOT / "harness" / "data" / "tasks")
    results = run_all(tasks, oracle_provider)
    summary = summarize(results)
    assert summary["passed"] == summary["total"] == 12
    assert summary["success_rate"] == 1.0


def test_constant_navigate_baseline_fails_tasks():
    tasks = load_tasks(ROOT / "harness" / "data" / "tasks")
    results = run_all(tasks, constant_provider("navigate"))
    summary = summarize(results)
    assert summary["passed"] == 0
    assert summary["failed"] == 12


def test_table_has_one_row_per_task():
    tasks = load_tasks(ROOT / "harness" / "data" / "tasks")
    table = render_table(run_all(tasks, oracle_provider))
    assert table.count("\n") == 13
    assert "| 01-navigate-docs | pass |" in table


def test_write_json_contains_summary(tmp_path):
    tasks = load_tasks(ROOT / "harness" / "data" / "tasks")
    out = tmp_path / "results.json"
    write_json(run_all(tasks, oracle_provider), out)
    body = out.read_text(encoding="utf-8")
    assert '"total": 12' in body
    assert '"success_rate": 1.0' in body
