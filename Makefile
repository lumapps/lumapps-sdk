.DEFAULT_GOAL := help

PY_SRC := lumapps/ tests/ scripts/
CI ?= false
TESTING ?= false

.PHONY: changelog
changelog:  ## Update the changelog in-place with latest commits.
	@poetry run failprint -t "Updating changelog" -- python scripts/update_changelog.py \
		CHANGELOG.md "<!-- insertion marker -->" "^## \[(?P<version>[^\]]+)"

.PHONY: check
check: check-docs check-code-quality check-types check-dependencies  ## Check it all!

.PHONY: check-code-quality
check-code-quality:  ## Check the code quality.
	@poetry run failprint -t "Checking code quality" -- flake8 --config=config/flake8.ini $(PY_SRC)

.PHONY: check-dependencies
check-dependencies:  ## Check for vulnerabilities in dependencies.
	@SAFETY=safety; \
	if ! $(CI); then \
		if ! command -v $$SAFETY &>/dev/null; then \
			SAFETY="pipx run safety"; \
		fi; \
	fi; \
	poetry run pip freeze 2>/dev/null | \
		grep -iv 'mkdocstrings' | \
		poetry run failprint --no-pty -t "Checking dependencies" -- $$SAFETY check --stdin --full-report

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

.PHONY: docs
docs:  ## Build the documentation locally.
	@poetry run mkdocs build

.PHONY: docs-serve
docs-serve:  ## Serve the documentation (localhost:8000).
	@poetry run mkdocs serve

.PHONY: docs-deploy
docs-deploy:  ## Deploy the documentation on GitHub pages.
	@poetry run mkdocs gh-deploy

.PHONY: help
help:  ## Print this help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

.PHONY: format
format:  ## Run formatting tools on the code.
	@poetry run failprint -t "Formatting code" -- black $(PY_SRC)
	@poetry run failprint -t "Ordering imports" -- isort -y -rc $(PY_SRC)

.PHONY: release
release:  ## Create a new release (commit, tag, push, build, publish, deploy docs).
ifndef v
	$(error Pass the new version with 'make release v=0.0.0')
endif
	@poetry run failprint -t "Bumping version" -- poetry version $(v)
	@poetry run failprint -t "Staging files" -- git add pyproject.toml CHANGELOG.md
	@poetry run failprint -t "Committing changes" -- git commit -m "chore: Prepare release $(v)"
	@poetry run failprint -t "Tagging commit" -- git tag v$(v)
	@poetry run failprint -t "Building dist/wheel" -- poetry build
	-@if ! $(CI) && ! $(TESTING); then \
		poetry run failprint -t "Pushing commits" -- git push; \
		poetry run failprint -t "Pushing tags" -- git push --tags; \
		poetry publish; \
		poetry run failprint -t "Deploying docs" -- poetry run mkdocs gh-deploy; \
	fi

.PHONY: setup
setup:  ## Setup the development environment (install dependencies).
	@if ! $(CI); then \
		if ! command -v poetry &>/dev/null; then \
		  if ! command -v pipx &>/dev/null; then \
			  pip install pipx; \
			fi; \
		  pipx install poetry --force; \
		fi; \
	fi; \
	poetry install -v
	pre-commit install

.PHONY: test
test:  ## Run the test suite and report coverage. 2>/dev/null
	@poetry run pytest -c config/pytest.ini
	@poetry run coverage html --rcfile=config/coverage.ini


.PHONY: pypi-release-beta
pypi-release-beta:  # release to pypi without taging github
ifndef v
	$(error Pass the new version with 'make release v=0.0.0')
endif
	@poetry run failprint -t "Bumping version" -- poetry version $(v)
	@poetry run failprint -t "Building dist/wheel" -- poetry build
	-@if ! $(CI) && ! $(TESTING); then \
		poetry publish; \
	fi
