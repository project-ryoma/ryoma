#* Variables
SHELL := /usr/bin/env bash
PYTHON := python
PYTHONPATH := '.'

#* Docker variables
IMAGE := ryoma
VERSION := latest

.PHONY: poetry-download
poetry-download:
	curl -sSL https://install.python-poetry.org | python3 -

.PHONY: poetry-remove
poetry-remove:
	curl -sSL https://install.python-poetry.org | python3 - --uninstall

.PHONY: uv-download
uv-download:
	curl -LsSf https://astral.sh/uv/install.sh | sh

#* Installation
.PHONY: install
install:
	uv lock && uv pip compile pyproject.toml -o requirements.txt
	uv sync
	#uv run mypy --install-types --non-interactive ./

.PHONY: pre-commit-install
pre-commit-install:
	uv run pre-commit install

#* Formatters
.PHONY: codestyle
codestyle:
	uv run pyupgrade --exit-zero-even-if-changed --py310-plus **/*.py
	uv run isort --settings-path pyproject.toml ./
	uv run black --config pyproject.toml ./

.PHONY: formatting
formatting: codestyle

#* Linting
.PHONY: test
unit-test:
	PYTHONPATH=$(PYTHONPATH) uv run pytest -c pyproject.toml --cov-report=html --cov=packages tests/unit_tests
	uv run coverage-badge -o assets/images/coverage.svg -f

.PHONY: check-codestyle
check-codestyle:
	uv run isort --diff --check-only --settings-path pyproject.toml ./
	uv run black --diff --check --config pyproject.toml ./ 

.PHONY: mypy
mypy:
	uv run mypy --config-file pyproject.toml ./

.PHONY: check-safety
check-safety:
	uv run safety check --full-report
	uv run bandit -ll --recursive ryoma tests

.PHONY: lint
lint: test check-codestyle mypy check-safety

.PHONY: update-dev-deps
update-dev-deps:
	uv add -D bandit@latest darglint@latest "isort[colors]@latest" mypy@latest pre-commit@latest pydocstyle@latest pylint@latest pytest@latest pyupgrade@latest safety@latest coverage@latest coverage-badge@latest pytest-html@latest pytest-cov@latest
	uv add -D --allow-prereleases black@latest

#* Docker
# Example: make docker-build VERSION=latest
# Example: make docker-build IMAGE=some_name VERSION=0.1.0
.PHONY: docker-build
docker-build:
	@echo Building docker $(IMAGE):$(VERSION) ...
	docker build \
		-t $(IMAGE):$(VERSION) . \
		-f ./Dockerfile

# Example: make docker-remove VERSION=latest
# Example: make docker-remove IMAGE=some_name VERSION=0.1.0
.PHONY: docker-remove
docker-remove:
	@echo Removing docker $(IMAGE):$(VERSION) ...
	docker rmi -f $(IMAGE):$(VERSION)

#* Cleaning
.PHONY: pycache-remove
pycache-remove:
	find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf

.PHONY: dsstore-remove
dsstore-remove:
	find . | grep -E ".DS_Store" | xargs rm -rf

.PHONY: mypycache-remove
mypycache-remove:
	find . | grep -E ".mypy_cache" | xargs rm -rf

.PHONY: ipynbcheckpoints-remove
ipynbcheckpoints-remove:
	find . | grep -E ".ipynb_checkpoints" | xargs rm -rf

.PHONY: pytestcache-remove
pytestcache-remove:
	find . | grep -E ".pytest_cache" | xargs rm -rf

.PHONY: build-remove
build-remove:
	rm -rf build/

.PHONY: cleanup
cleanup: pycache-remove dsstore-remove mypycache-remove ipynbcheckpoints-remove pytestcache-remove

.PHONY: start-ryoma-lab
start-ryoma-lab:
	uv run reflex run

.PHONY: build
build:
	uv build

.PHONY: publish
publish:
	uv publish

.PHONY: init-data
init-data:
	uv run init-data

.PHONY: migrate
migrate:
	uv run reflex db migrate
