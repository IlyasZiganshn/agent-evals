def normalize(value: object) -> str:
    return " ".join(str(value).strip().lower().split())


def score_action(task: dict, action: dict) -> dict:
    expected = task["expected"]
    expected_tool = expected["tool"]
    expected_args = expected.get("args", {})
    actual_tool = (action or {}).get("tool")
    actual_args = (action or {}).get("args", {}) or {}

    if actual_tool != expected_tool:
        return {
            "passed": False,
            "reason": f"tool {actual_tool!r} != {expected_tool!r}",
        }

    mismatches = []
    for key, expected_value in expected_args.items():
        if normalize(actual_args.get(key)) != normalize(expected_value):
            mismatches.append(f"{key}={actual_args.get(key)!r} != {expected_value!r}")
    if mismatches:
        return {"passed": False, "reason": "; ".join(mismatches)}

    return {"passed": True, "reason": "ok"}
