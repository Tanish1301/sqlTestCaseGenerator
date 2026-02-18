from fastapi.testclient import TestClient

from app.main import app, scenario_generator


client = TestClient(app)


def test_generate_endpoint_returns_rule_scenarios():
    response = client.post(
        "/testcase/generate",
        json={"sql": "SELECT id, name FROM employees WHERE salary > 5000"},
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body) >= 2
    assert body[0]["description"]
    assert body[0]["scenario_type"] in {"POSITIVE", "NEGATIVE", "BOUNDARY"}


def test_generate_ai_endpoint_with_mock():
    original = scenario_generator.generate_ai_scenarios
    scenario_generator.generate_ai_scenarios = lambda *_args, **_kwargs: "AI scenarios sample"
    try:
        response = client.post(
            "/testcase/generate-ai",
            json={"sql": "SELECT * FROM employees"},
        )
    finally:
        scenario_generator.generate_ai_scenarios = original

    assert response.status_code == 200
    assert response.json()["scenarios"] == "AI scenarios sample"


def test_generate_endpoint_supports_complex_oracle_join_query():
    payload = {
        "sql": (
            "WITH ranked_emp AS ("
            "  SELECT e.dept_id, e.emp_id, "
            "         ROW_NUMBER() OVER (PARTITION BY e.dept_id ORDER BY e.updated_at DESC) rn "
            "  FROM employees e "
            "  WHERE ROWNUM <= 500"
            ") "
            "SELECT re.dept_id, d.dept_name, COUNT(*) "
            "FROM ranked_emp re "
            "JOIN departments d ON re.dept_id = d.dept_id "
            "LEFT JOIN dept_budget b ON d.dept_id = b.dept_id AND b.year_no >= 2024 "
            "WHERE re.rn = 1 "
            "GROUP BY re.dept_id, d.dept_name "
            "HAVING COUNT(*) > 0"
        )
    }
    response = client.post("/testcase/generate", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert len(body) > 0


def test_generate_endpoint_supports_merge_into_with_join_condition():
    payload = {
        "sql": (
            "MERGE INTO target_table t "
            "USING source_table s "
            "ON (t.customer_id = s.customer_id AND t.region_id = s.region_id) "
            "WHEN MATCHED THEN UPDATE SET t.amount = s.amount "
            "WHEN NOT MATCHED THEN INSERT (customer_id, region_id, amount) "
            "VALUES (s.customer_id, s.region_id, s.amount)"
        )
    }
    response = client.post("/testcase/generate", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert len(body) > 0


def test_generate_hybrid_endpoint_returns_standardized_output():
    payload = {
        "sql": "SELECT e.department_id, COUNT(e.id) FROM employees e JOIN departments d ON e.department_id = d.id WHERE e.salary > 5000 GROUP BY e.department_id HAVING COUNT(e.id) > 2"
    }
    response1 = client.post("/testcase/generate-hybrid", json=payload)
    response2 = client.post("/testcase/generate-hybrid", json=payload)

    assert response1.status_code == 200
    assert response2.status_code == 200
    body1 = response1.json()
    body2 = response2.json()

    assert body1["standardized"] is True
    assert body1["ai_used"] is False
    assert body1["validation"]["join_count"] == 1
    assert body1["validation"]["generated_scenarios"] == len(body1["scenarios"])
    assert body1["scenarios"] == body2["scenarios"]


def test_generate_hybrid_endpoint_can_include_ai_supplement():
    original = scenario_generator.generate_ai_scenarios
    scenario_generator.generate_ai_scenarios = lambda *_args, **_kwargs: "supplemental ideas"
    try:
        response = client.post(
            "/testcase/generate-hybrid",
            json={"sql": "SELECT * FROM employees", "include_ai_supplement": True},
        )
    finally:
        scenario_generator.generate_ai_scenarios = original

    assert response.status_code == 200
    body = response.json()
    assert body["ai_used"] is True
    assert body["ai_supplement"] == "supplemental ideas"
