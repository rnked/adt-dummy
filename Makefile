UV := uv

.PHONY: help install install-cli lint format test test-last-failed clean clean-build clean-test clean-pyc

help:
	@echo "Targets:"
	@echo "  install          - Sync local dev environment and install dami as a global uv tool"
	@echo "  install-cli      - Install dami as a global uv tool"
	@echo "  lint             - Run isort and black in check mode"
	@echo "  format           - Run isort and black to format code"
	@echo "  test             - Run pytest with coverage"
	@echo "  test-last-failed - Re-run only failed tests"
	@echo "  clean            - Remove generated files (build/test/cache artifacts)"

install:
	$(UV) sync --group dev --group test
	$(UV) tool install --editable --force .

install-cli:
	$(UV) tool install --editable --force .

lint:
	$(UV) run isort --check --diff src tests
	$(UV) run black --check src tests

format:
	$(UV) run isort src tests
	$(UV) run black src tests

test:
	$(UV) run pytest --cov=adt_dummy --cov-branch --cov-report=term-missing

test-last-failed:
	$(UV) run pytest --lf -vv

clean: clean-build clean-test clean-pyc

clean-build:
	rm -rf build dist .eggs
	find . -type d \( -name "*.egg-info" -o -name "pip-wheel-metadata" \) -not -path "*/.git/*" -prune -exec rm -rf {} +

clean-test:
	rm -rf .pytest_cache .mypy_cache .coverage coverage.xml htmlcov .tox .nox

clean-pyc:
	find . -type d -name "__pycache__" -not -path "*/.git/*" -prune -exec rm -rf {} +
	find . -type f \( -name "*.pyc" -o -name "*.pyo" -o -name "*.py,cover" -o -name "*$$py.class" \) -not -path "*/.git/*" -delete
