.PHONY: help install dev inngest send lint format check

PORT ?= 8000

help: ## Show targets
	@grep -E '^[a-z]+:.*##' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-10s %s\n", $$1, $$2}'

install: ## Install dependencies
	uv sync

dev: ## Run the FastAPI app (expects ANTHROPIC_API_KEY in env)
	INNGEST_DEV=1 uv run uvicorn app.main:app --reload --port $(PORT)

inngest: ## Run the Inngest Dev Server pointed at the app
	npx inngest-cli@latest dev -u http://localhost:$(PORT)/api/inngest

send: ## Send an event to the Dev Server to trigger a run
	curl -s localhost:8288/e/dev -d '{"name": "demo/greeting.requested", \
		"data": {"name": "Ada", "city": "Paris", "language": "French"}}'

lint: ## Lint and check formatting
	uv run ruff check app
	uv run ruff format --check app

format: ## Format and autofix
	uv run ruff format app
	uv run ruff check --fix app

check: lint ## Lint, then import the app as a smoke test
	INNGEST_DEV=1 uv run python -c "import app.main"
