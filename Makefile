PYTHON ?= python

.PHONY: install api playground lint format check

install:
	$(PYTHON) -m pip install -e .[dev]
	npm install

api:
	$(PYTHON) -m uvicorn app.main:app --app-dir apps/api-server --reload

playground:
	npm run dev:playground

lint:
	$(PYTHON) -m ruff check packages apps/api-server

check:
	$(PYTHON) -m compileall packages apps
