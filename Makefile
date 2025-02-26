.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

fmt: ## format style with black and isort
	poetry run black .
	poetry run isort .

test: ## run tests quickly with pytest
	poetry run pytest

install: clean ## install the package to the active Python's site-packages
	poetry install

docs: ## build the docs and run a mkdocs server
	poetry run python scripts/generate_ref_docs.py
	poetry run mkdocs serve

mypy: ## run type hinting check
	poetry run mypy pinot_connect

test-cov: ## run the tests with coverage turned on
	poetry run pytest --cov=. --cov-branch -v --durations=25

cov: ## check code coverage and run the html report
	poetry run pytest --cov=. -v --durations=25 tests/unit
	poetry run coverage report -m
	poetry run coverage html
	$(BROWSER) htmlcov/index.html

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

waitforpinot:  # waits for pinot quickstart controller to be healthy
	@echo "Waiting for Pinot container to be healthy..."
	@timeout=60; \
	while [ $$timeout -gt 0 ]; do \
	    status=$$(docker inspect -f '{{.State.Health.Status}}' pinot-quickstart); \
	    if [ "$$status" = "healthy" ]; then \
	        echo "Pinot container is healthy and ready!"; \
	        exit 0; \
	    elif [ "$$status" = "unhealthy" ]; then \
	        echo "ERROR: Pinot container became unhealthy."; \
	        exit 1; \
	    fi; \
	    echo "Waiting for container to be healthy... ($$timeout seconds left)"; \
	    sleep 2; \
	    timeout=$$((timeout - 2)); \
	done; \
	echo "ERROR: Pinot container did not become healthy within the timeout period."; \
	exit 1

startpinot:  # starts apache pinot batch processing quick start
	@echo "Staring apache pinot"
	@docker run -d --name pinot-quickstart -p 9000:9000 \
      -p 8099:8000 \
      --health-cmd="curl -f http://localhost:9000/health || exit 1" \
	  --health-interval=10s \
	  --health-timeout=5s \
	  --health-retries=3 \
	  --health-start-period=5s \
	  apachepinot/pinot:latest QuickStart -type batch

stoppinot:  # stops the pinot-quickstart container
	@docker stop pinot-quickstart
	@docker rm pinot-quickstart

pinot-qs: startpinot waitforpinot  # starts the pinot-quickstart cluster

pinot-with-auth:  # starts a pinot cluster with two empty tables and basic auth
	docker compose up -d --wait

stop-pinot-with-auth:  # stops the pinot cluster with basic auth
	docker compose down

reset-pinot-with-auth:  # restarts the pinot cluster with basic auth
	docker compose restart

reset-pinot-quickstart: stoppinot pinot  # restarts the pinot-quickstart cluster