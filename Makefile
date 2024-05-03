# Makefile
SHELL := /bin/bash

# Python tasks
.PHONY: lint-python autolint-python test-python run-python

lint-python:
	poetry run ruff check && poetry run isort --check-only .

autolint-python:
	poetry run ruff format && poetry run isort .

test-python:
	poetry run pytest

run-python:
	poetry run python scripts/start_chatbot.py

debug-tools:
	poetry run python scripts/debug_aws_tools.py

# Combined tasks
.PHONY: autolint lint test run

lint: lint-python
autolint: autolint-python lint
test: test-python
run: run-python
