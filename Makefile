.DEFAULT_GOAL := help
.PHONY: check check-code-quality check-docs check-types clean docs-cp docs docs-serve docs-deploy help format setup test

PY_SRC := lumapps/
CI ?= false
TESTING ?= false
PYTHON ?= python3.7
PIP = .venv/bin/pip
POETRY ?= .venv/bin/poetry

check: check-docs check-code-quality check-types  ## Check it all!

check-code-quality:  ## Check the code quality.
	@$(POETRY) run failprint -t "Checking code quality" -- flake8 --config=config/flake8.ini $(PY_SRC)

check-docs:  ## Check if the documentation builds correctly.
	@$(POETRY) run failprint -t "Building documentation" -- mkdocs build -s

check-types:  ## Check that the code is correctly typed.
	@$(POETRY) run failprint -t "Type-checking" -- mypy --config-file config/mypy.ini $(PY_SRC)

clean:  ## Delete temporary files.
	@rm -rf build 2>/dev/null
	@rm -rf .coverage* 2>/dev/null
	@rm -rf dist 2>/dev/null
	@rm -rf .mypy_cache 2>/dev/null
	@rm -rf pip-wheel-metadata 2>/dev/null
	@rm -rf .pytest_cache 2>/dev/null
	@rm -rf site 2>/dev/null
	@rm -rf lumapps_sdk.egg-info>/dev/null
	@rm -rf tests/__pycache__ 2>/dev/null
	@find . -name "*.rej" -delete 2>/dev/null

docs-cp:
	cp README.md docs/index.md
	cp LICENSE.md docs/

docs: docs-cp ## Build the documentation locally.
	@$(POETRY) run mkdocs build

docs-serve: docs-cp ## Serve the documentation (localhost:8000).
	@$(POETRY) run mkdocs serve

docs-deploy: docs-cp ## Deploy the documentation on GitHub pages.
	@$(POETRY) run mkdocs gh-deploy

help:  ## Print this help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

format:  ## Run formatting tools on the code.
	@$(POETRY) run failprint -t "Formatting code" -- black $(PY_SRC)
	@$(POETRY) run failprint -t "Ordering imports" -- isort -y -rc $(PY_SRC)

setup: .venv  ## Setup the development environment (install dependencies).
	$(POETRY) config virtualenvs.in-project true
	$(POETRY) install -v
	$(POETRY) run pre-commit install
	$(POETRY) run pre-commit install --hook-type commit-msg

test:  ## Run the test suite and report coverage. 2>/dev/null
	@$(POETRY) run pytest -c config/pytest.ini
	@$(POETRY) run coverage html --rcfile=config/coverage.ini

.venv:  ## Install the virtual env directory
	$(PYTHON) -m venv .venv
	$(PIP) install --quiet --upgrade pip
	$(PIP) install poetry
