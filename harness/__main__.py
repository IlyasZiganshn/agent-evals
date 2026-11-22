import argparse
import sys
from pathlib import Path

from harness.providers import constant_provider, openai_provider, oracle_provider
from harness.runner import render_table, run_all, summarize, write_json
from harness.tasks import load_tasks

DEFAULT_TASKS = Path(__file__).resolve().parent.parent / "tasks"


def build_provider(args):
    if args.provider == "oracle":
        return oracle_provider
    if args.provider == "constant":
        return constant_provider(args.tool)
    if args.provider == "openai":
        if not args.model:
            raise SystemExit("--model is required with --provider openai")

        def provider(task: dict) -> dict:
            return openai_provider(
                task,
                model=args.model,
                base_url=args.base_url,
                api_key_env=args.api_key_env,
            )

        return provider
    raise SystemExit(f"unknown provider {args.provider}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run planner-level evals for a tool-using agent.")
    parser.add_argument("--tasks", default=str(DEFAULT_TASKS))
    parser.add_argument("--provider", choices=["oracle", "constant", "openai"], default="oracle")
    parser.add_argument("--tool", default="navigate", help="tool for the constant baseline")
    parser.add_argument("--model", default="")
    parser.add_argument("--base-url", default="https://api.openai.com/v1")
    parser.add_argument("--api-key-env", default="LLM_API_KEY")
    parser.add_argument("--out", default="")
    args = parser.parse_args()

    tasks = load_tasks(args.tasks)
    provider = build_provider(args)
    results = run_all(tasks, provider)
    summary = summarize(results)

    print(render_table(results))
    print()
    print(
        f"success {summary['passed']}/{summary['total']} "
        f"({summary['success_rate'] * 100:.0f}%)"
    )

    if args.out:
        write_json(results, args.out)
        print(f"results written to {args.out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
