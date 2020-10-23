.DEFAULT_GOAL := help

PY_SRC := lumapps/
CI ?= false
TESTING ?= false

.PHONY: check
check: check-docs check-code-quality check-types check-dependencies  ## Check it all!

.PHONY: check-code-quality
check-code-quality:  ## Check the code quality.
	@poetry run failprint -t "Checking code quality" -- flake8 --config=config/flake8.ini $(PY_SRC)

.PHONY: check-dependencies
check-dependencies:  ## Check for vulnerabilities in dependencies.
	poetry run pip freeze 2>/dev/null | \
		grep -iv 'mkdocstrings' | \
		poetry run failprint --no-pty -t "Checking dependencies" -- safety check --stdin --full-report

.PHONY: check-docs
check-docs:  ## Check if the documentation builds correctly.
	@poetry run failprint -t "Building documentation" -- mkdocs build -s

.PHONY: check-types
check-types:  ## Check that the code is correctly typed.
	@poetry run failprint -t "Type-checking" -- mypy --config-file config/mypy.ini $(PY_SRC)

.PHONY: clean
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

.PHONY: docs-cp
docs-cp:
	cp README.md docs/index.md
	cp LICENSE.md docs/

.PHONY: docs
docs: docs-cp ## Build the documentation locally.
	@poetry run mkdocs build

.PHONY: docs-serve
docs-serve: docs-cp ## Serve the documentation (localhost:8000).
	@poetry run mkdocs serve

.PHONY: docs-deploy
docs-deploy: docs-cp ## Deploy the documentation on GitHub pages.
	@poetry run mkdocs gh-deploy

.PHONY: help
help:  ## Print this help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

.PHONY: format
format:  ## Run formatting tools on the code.
	@poetry run failprint -t "Formatting code" -- black $(PY_SRC)
	@poetry run failprint -t "Ordering imports" -- isort -y -rc $(PY_SRC)


.PHONY: setup
setup:  ## Setup the development environment (install dependencies).
	@if ! $(CI); then \
		if ! command -v pipx &>/dev/null; then \
			pip install pipx; \
		fi; \
		if ! command -v poetry &>/dev/null; then \
		  pipx install poetry; \
		fi; \
	fi; \
	poetry config virtualenvs.in-project true
	poetry install -v
	@if ! $(CI); then \
		poetry run pre-commit install; \
		poetry run pre-commit install --hook-type commit-msg; \
	fi; \


.PHONY: test
test:  ## Run the test suite and report coverage. 2>/dev/null
	@poetry run pytest -c config/pytest.ini
	@poetry run coverage html --rcfile=config/coverage.ini


