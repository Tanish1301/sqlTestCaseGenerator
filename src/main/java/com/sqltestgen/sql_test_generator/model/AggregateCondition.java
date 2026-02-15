package com.sqltestgen.sql_test_generator.model;


public class AggregateCondition {

    private String function;   // SUM, COUNT, AVG
    private String column;

    public AggregateCondition(String function, String column) {
        this.function = function;
        this.column = column;
    }

    public String getFunction() { return function; }
    public String getColumn() { return column; }
}

