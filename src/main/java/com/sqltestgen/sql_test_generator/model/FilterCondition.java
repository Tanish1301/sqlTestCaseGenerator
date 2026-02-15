package com.sqltestgen.sql_test_generator.model;

import java.util.List;

public class FilterCondition {

    private String column;
    private String operator;
    private List<String> values;

    public FilterCondition(String column, String operator, List<String> values) {
        this.column = column;
        this.operator = operator;
        this.values = values;
    }

    public String getColumn() { return column; }
    public String getOperator() { return operator; }
    public List<String> getValues() { return values; }
}
