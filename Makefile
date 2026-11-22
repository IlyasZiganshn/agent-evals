.PHONY: install test lint oracle openai

install:
	uv sync --extra dev

test:
	uv run pytest

lint:
	uv run ruff check .

oracle:
	uv run python -m harness --provider oracle

openai:
	uv run python -m harness --provider openai --model $(MODEL) --out results/$(MODEL).json
