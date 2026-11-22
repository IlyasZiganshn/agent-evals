from pathlib import Path

from harness.scoring import score_action


def run_task(task: dict, provider) -> dict:
    action = provider(task)
    verdict = score_action(task, action)
    return {
        "id": task["id"],
        "goal": task["goal"],
        "expected": task["expected"],
        "actual": action,
        "passed": verdict["passed"],
        "reason": verdict["reason"],
    }


def run_all(tasks: list[dict], provider) -> list[dict]:
    return [run_task(task, provider) for task in tasks]


def summarize(results: list[dict]) -> dict:
    passed = sum(1 for item in results if item["passed"])
    return {
        "total": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "success_rate": round(passed / len(results), 3) if results else 0.0,
    }


def render_table(results: list[dict]) -> str:
    lines = [
        "| task | result | expected | actual |",
        "| --- | --- | --- | --- |",
    ]
    for item in results:
        expected = item["expected"]["tool"]
        actual = item["actual"].get("tool")
        mark = "pass" if item["passed"] else "fail"
        lines.append(f"| {item['id']} | {mark} | {expected} | {actual} |")
    return "\n".join(lines)


def write_json(results: list[dict], path: str | Path) -> None:
    import json

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(
            {"summary": summarize(results), "results": results},
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
