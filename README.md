# SQL Test Generator (Python)

Java/Spring runtime has been removed. This project now runs only on Python + FastAPI.

## Features

- SQL query parsing using `sqlglot` in Oracle dialect mode
- Rule-based test scenario generation
- Hybrid generation: parser/rule-based standardized scenarios + optional AI supplement
- AI-based scenario generation via Ollama

## Local Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run Locally

```bash
uvicorn app.main:app --reload --port 8080
```

Server: `http://localhost:8080`

## Docker

Build and run app container:

```bash
docker build -t sql-test-generator:py .
docker run --rm -p 8080:8080 sql-test-generator:py
```

Compose with app only:

```bash
docker compose up --build api
```

Compose with app + Ollama:

```bash
docker compose --profile with-ollama up --build
```

## API Endpoints

### `POST /testcase/generate`

Content-Type: `application/json`

Example:

```bash
curl -X POST "http://localhost:8080/testcase/generate" \
  -H "Content-Type: application/json" \
  -d '{"sql":"SELECT id, name FROM employees WHERE salary > 5000"}'
```

### `POST /testcase/generate-ai`

Content-Type: `application/json`

Example:

```bash
curl -X POST "http://localhost:8080/testcase/generate-ai" \
  -H "Content-Type: application/json" \
  -d '{"sql":"SELECT id, name FROM employees WHERE salary > 5000"}'
```

Optional fields for `/testcase/generate-ai`:
- `model`
- `endpoint`
- `timeout_seconds`

### `POST /testcase/generate-hybrid`

Content-Type: `application/json`

This is the recommended endpoint for consistent outputs.
- Scenarios are generated from parser/rules only (deterministic IDs + ordering).
- AI is optional and returned only as supplementary text.

Example:

```bash
curl -X POST "http://localhost:8080/testcase/generate-hybrid" \
  -H "Content-Type: application/json" \
  -d '{"sql":"SELECT e.department_id, COUNT(e.id) FROM employees e JOIN departments d ON e.department_id = d.id WHERE e.salary > 5000 GROUP BY e.department_id HAVING COUNT(e.id) > 2","include_ai_supplement":true}'
```

## Insomnia Example

Place your screenshot at `docs/images/insomnia-hybrid-response.png` to render below:

![Hybrid endpoint response](docs/images/insomnia-hybrid-response.png)

## Complex Query Support

Works best for:
- multi-table joins (including chained `JOIN ... ON ... AND ...` conditions)
- Oracle `WITH` CTE queries
- Oracle analytic/window functions like `ROW_NUMBER() OVER (PARTITION BY ...)`
- Oracle `ROWNUM` predicates
- Oracle `MERGE INTO ... USING ... ON (...)`
- nested AND/OR conditions
- filters with `=`, `!=`, `>`, `>=`, `<`, `<=`, `BETWEEN`, `IN`, `NOT IN`, `LIKE`, `IS`
- HAVING with aggregate comparisons and nested AND/OR

Current limits:
- scenario generation is still rule-based and does not fully reason about deeply nested subqueries/CTE semantics

## Tests

```bash
pytest -q
```

Test coverage includes parser extraction and endpoint-level API tests with sample payloads.
