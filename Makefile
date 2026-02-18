PYTHON ?= python3

.PHONY: venv install run test docker-build docker-run

venv:
	$(PYTHON) -m venv .venv

install:
	. .venv/bin/activate && pip install -r requirements.txt

run:
	. .venv/bin/activate && uvicorn app.main:app --reload --port 8080

test:
	. .venv/bin/activate && pytest -q

docker-build:
	docker build -t sql-test-generator:py .

docker-run:
	docker run --rm -p 8080:8080 sql-test-generator:py
