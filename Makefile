BACKEND_DIR := backend
BACKEND_VENV := $(BACKEND_DIR)/.venv
BACKEND_PYTEST := $(BACKEND_VENV)/bin/python -m pytest
BACKEND_RUFF := $(BACKEND_VENV)/bin/ruff
FRONTEND_DIR := frontend

.PHONY: test test-backend lint-backend build-frontend

test: test-backend

test-backend:
	cd $(BACKEND_DIR) && ./.venv/bin/python -m pytest -q

lint-backend:
	cd $(BACKEND_DIR) && ./.venv/bin/ruff check .

build-frontend:
	cd $(FRONTEND_DIR) && npm run build
