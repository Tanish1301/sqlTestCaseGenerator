package com.sqltestgen.sql_test_generator.model;


public class CaseCondition {

    private String condition;
    private String result;

    public CaseCondition(String condition, String result) {
        this.condition = condition;
        this.result = result;
    }

    public String getCondition() { return condition; }
    public String getResult() { return result; }
}

