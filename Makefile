SHELL:=/bin/bash

.DEFAULT_GOAL := help

PY_SRC := lumapps/
CI ?= false
TESTING ?= false

VENV_BIN=./.venv/bin
pip:=$(VENV_BIN)/pip

.PHONY: help
help:  ## Print this help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

.PHONY: check
check: check-docs check-code-quality check-types  ## Check it all!

.PHONY: check-code-quality
check-code-quality:  ## Check the code quality.
	source $(VENV_BIN)/activate && \
	failprint -t "Checking code quality" -- flake8 --config=config/flake8.ini $(PY_SRC)

.PHONY: check-docs
check-docs:  ## Check if the documentation builds correctly.
	source $(VENV_BIN)/activate && \
	failprint -t "Building documentation" -- mkdocs build -s

.PHONY: check-types
check-types:  ## Check that the code is correctly typed.
	source $(VENV_BIN)/activate && \
	failprint -t "Type-checking" -- mypy --config-file config/mypy.ini $(PY_SRC)

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
	source $(VENV_BIN)/activate && \
	mkdocs build

.PHONY: docs-serve
docs-serve: docs-cp ## Serve the documentation (localhost:8000).
	source $(VENV_BIN)/activate && \
	mkdocs serve

.PHONY: docs-deploy
docs-deploy: docs-cp ## Deploy the documentation on GitHub pages.
	source $(VENV_BIN)/activate && \
	mkdocs gh-deploy



.PHONY: format
format:  ## Run formatting tools on the code.
	source $(VENV_BIN)/activate && \
	failprint -t "Formatting code" -- black $(PY_SRC)


.PHONY: setup
setup:  ## Setup the development environment (install dependencies).
	rm -rf .venv
	python3.8 -m venv .venv
	$(pip) install -U pip
	$(pip) install -r requirements.txt
	$(pip) install -r requirements-dev.txt
	@if !$(CI); then \
		source $(VENV_BIN)/activate && \
		pre-commit install && \
		pre-commit install --hook-type commit-msg; \
	fi; \


.PHONY: test
test:  ## Run the test suite and report coverage. 2>/dev/null
	source $(VENV_BIN)/activate && \
	pytest -c config/pytest.ini
	coverage html --rcfile=config/coverage.ini

# Pypi https://packaging.python.org/tutorials/packaging-projects/

.PHONY: build
build:  ## B Build the wheel and tar.gz package in the dist folder
	source $(VENV_BIN)/activate && \
	python3 -m build 

.PHONY: publish-test
publish-test: build  
	source $(VENV_BIN)/activate && \
	twine upload --repository testpypi dist/*

.PHONY: publish
publish: build  ## Publish the built (dist folder) package on pypi
	source $(VENV_BIN)/activate && \
	twine upload dist/*