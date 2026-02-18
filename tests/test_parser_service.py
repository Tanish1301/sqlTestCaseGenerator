from app.parser_service import SqlParserService


def test_parse_query_extracts_filters_joins_aggregates_having():
    sql = """
    SELECT e.department_id, COUNT(e.id) AS employee_count
    FROM employees e
    JOIN departments d ON e.department_id = d.id
    WHERE e.salary > 5000 AND d.name IN ('HR', 'ENG')
    GROUP BY e.department_id
    HAVING COUNT(e.id) > 2
    """

    model = SqlParserService().parse_query(sql)

    assert len(model.joins) == 1
    assert len(model.filters) == 2
    assert len(model.aggregates) == 1
    assert len(model.having_conditions) == 1


def test_parse_query_supports_more_complex_operators():
    sql = """
    SELECT e.department_id, COUNT(e.id)
    FROM employees e
    JOIN departments d ON e.department_id = d.id
    WHERE (e.salary >= 5000 AND d.name LIKE 'E%')
      AND e.status IS NOT NULL
      AND e.grade NOT IN ('C', 'D')
    GROUP BY e.department_id
    HAVING COUNT(e.id) >= 2 AND COUNT(e.id) != 99
    """

    model = SqlParserService().parse_query(sql)
    operators = {f.operator for f in model.filters}
    having_operators = {h.operator for h in model.having_conditions}

    assert ">=" in operators
    assert "LIKE" in operators
    assert "IS" in operators
    assert "NOT IN" in operators
    assert ">=" in having_operators
    assert "!=" in having_operators


def test_parse_query_supports_oracle_cte_partition_and_rownum():
    sql = """
    WITH ranked_emp AS (
        SELECT e.dept_id,
               e.emp_id,
               ROW_NUMBER() OVER (PARTITION BY e.dept_id ORDER BY e.updated_at DESC) rn
        FROM employees e
        WHERE ROWNUM <= 500
    )
    SELECT re.dept_id, d.dept_name, COUNT(*)
    FROM ranked_emp re
    JOIN departments d ON re.dept_id = d.dept_id
    LEFT JOIN dept_budget b ON d.dept_id = b.dept_id AND b.year_no >= 2024
    WHERE re.rn = 1
    GROUP BY re.dept_id, d.dept_name
    HAVING COUNT(*) > 0
    """

    model = SqlParserService().parse_query(sql)

    assert len(model.joins) >= 2
    assert any(j.left_column == "re.dept_id" and j.right_column == "d.dept_id" for j in model.joins)
    assert any(f.column == "ROWNUM" and f.operator == "<=" for f in model.filters)
    assert any(f.column == "re.rn" and f.operator == "=" for f in model.filters)


def test_parse_query_supports_merge_into_join_conditions():
    sql = """
    MERGE INTO target_table t
    USING source_table s
    ON (t.customer_id = s.customer_id AND t.region_id = s.region_id)
    WHEN MATCHED THEN UPDATE SET t.amount = s.amount
    WHEN NOT MATCHED THEN INSERT (customer_id, region_id, amount)
    VALUES (s.customer_id, s.region_id, s.amount)
    """

    model = SqlParserService().parse_query(sql)
    pairs = {(join.left_column, join.right_column) for join in model.joins}

    assert ("t.customer_id", "s.customer_id") in pairs
    assert ("t.region_id", "s.region_id") in pairs
