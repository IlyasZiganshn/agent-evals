from pathlib import Path

import yaml

TOOLS = {"navigate", "click", "type_text", "scroll", "finish"}


def load_tasks(directory: str | Path) -> list[dict]:
    paths = sorted(Path(directory).glob("*.yaml"))
    if not paths:
        raise ValueError(f"no task files in {directory}")
    tasks = [load_task(path) for path in paths]
    ids = [task["id"] for task in tasks]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate task ids")
    return tasks


def load_task(path: str | Path) -> dict:
    task = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    validate_task(task, str(path))
    task["_path"] = str(path)
    return task


def validate_task(task: dict, source: str = "task") -> None:
    if not isinstance(task, dict):
        raise ValueError(f"{source}: task must be a mapping")
    for key in ("id", "goal", "observation", "expected"):
        if key not in task:
            raise ValueError(f"{source}: missing {key}")
    observation = task["observation"]
    if not isinstance(observation, dict) or not observation.get("url"):
        raise ValueError(f"{source}: observation.url is required")
    elements = observation.get("elements", [])
    if not isinstance(elements, list):
        raise ValueError(f"{source}: observation.elements must be a list")
    for element in elements:
        if not isinstance(element, dict) or "role" not in element or "text" not in element:
            raise ValueError(f"{source}: each element needs role and text")
    expected = task["expected"]
    if not isinstance(expected, dict) or expected.get("tool") not in TOOLS:
        raise ValueError(f"{source}: expected.tool must be one of {sorted(TOOLS)}")
    if not isinstance(expected.get("args", {}), dict):
        raise ValueError(f"{source}: expected.args must be a mapping")
    budget = task.get("budget", {})
    if not isinstance(budget, dict):
        raise ValueError(f"{source}: budget must be a mapping")
    steps = budget.get("steps", 1)
    if not isinstance(steps, int) or steps < 1:
        raise ValueError(f"{source}: budget.steps must be a positive int")


def task_prompt(task: dict) -> str:
    observation = task["observation"]
    lines = [f"URL: {observation['url']}"]
    if observation.get("text"):
        lines.append(f"Page text: {observation['text']}")
    elements = observation.get("elements", [])
    if elements:
        lines.append("Visible elements:")
        for element in elements:
            lines.append(f"- {element['role']}: {element['text']}")
    lines.append(f"Goal: {task['goal']}")
    lines.append("Pick exactly one tool call.")
    return "\n".join(lines)
