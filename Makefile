PYTHON := .venv/Scripts/python.exe

.PHONY: test lint typecheck parity quality demo bench bench-tracing bench-metrics ci install-dev contract migrate release-check api-docs

install-dev:
	$(PYTHON) -m pip install -e .[dev]

test:
	$(PYTHON) -m pytest -q

lint:
	$(PYTHON) -m ruff check src tests examples scripts

typecheck:
	$(PYTHON) -m mypy src

parity:
	$(PYTHON) scripts/check_api_parity.py

quality: lint typecheck parity test

demo:
	$(PYTHON) -m examples.cli_demo

bench:
	$(PYTHON) scripts/benchmark_logging.py

bench-tracing:
	$(PYTHON) scripts/benchmark_tracing.py

bench-metrics:
	$(PYTHON) scripts/benchmark_metrics.py

ci: quality

contract:
	EW_RUN_CONTRACT=1 $(PYTHON) -m pytest -m contract -q

migrate:
	$(PYTHON) scripts/migrate_v1_api.py --path src

release-check:
	$(PYTHON) scripts/release_check.py

api-docs:
	$(PYTHON) scripts/generate_api_docs.py
