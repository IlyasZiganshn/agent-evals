import json
import os

import httpx

from harness.tasks import TOOLS, task_prompt

SYSTEM_PROMPT = """You are the planner of a web agent.
You see one page observation and one goal. Reply with exactly one tool call.
Do not explain.
Tools: navigate(url), click(text), type_text(text), scroll(pixels), finish(summary)."""

TOOL_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "navigate",
            "description": "Open a URL in the current tab.",
            "parameters": {
                "type": "object",
                "properties": {"url": {"type": "string"}},
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "click",
            "description": "Click an element by its visible text.",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "type_text",
            "description": "Type text into the focused input.",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "scroll",
            "description": "Scroll the page by a number of pixels.",
            "parameters": {
                "type": "object",
                "properties": {"pixels": {"type": "integer"}},
                "required": ["pixels"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "finish",
            "description": "Stop when the goal is reached.",
            "parameters": {
                "type": "object",
                "properties": {"summary": {"type": "string"}},
                "required": ["summary"],
            },
        },
    },
]


def oracle_provider(task: dict) -> dict:
    """Return the expected action. Used to test the harness, not a model."""
    expected = task["expected"]
    return {"tool": expected["tool"], "args": expected.get("args", {})}


def constant_provider(tool: str):
    def provider(task: dict) -> dict:
        return {"tool": tool, "args": {}}

    return provider


def openai_provider(
    task: dict,
    model: str,
    base_url: str,
    api_key_env: str = "LLM_API_KEY",
    timeout: float = 30.0,
) -> dict:
    api_key = os.getenv(api_key_env)
    if not api_key:
        raise RuntimeError(f"{api_key_env} is not set")
    payload = {
        "model": model,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": task_prompt(task)},
        ],
        "tools": TOOL_SCHEMA,
        "tool_choice": "auto",
    }
    response = httpx.post(
        f"{base_url.rstrip('/')}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json=payload,
        timeout=timeout,
    )
    response.raise_for_status()
    message = response.json()["choices"][0]["message"]
    calls = message.get("tool_calls") or []
    if not calls:
        return {"tool": None, "args": {}, "raw": message.get("content")}
    call = calls[0]["function"]
    try:
        args = json.loads(call.get("arguments") or "{}")
    except json.JSONDecodeError:
        args = {}
        return {"tool": call.get("name"), "args": args, "invalid_json": call.get("arguments")}
    return {"tool": call.get("name"), "args": args}


SUPPORTED_TOOLS = TOOLS
