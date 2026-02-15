package com.sqltestgen.sql_test_generator.model;

public class JoinCondition {

    private String leftColumn;
    private String rightColumn;

    public JoinCondition(String leftColumn, String rightColumn) {
        this.leftColumn = leftColumn;
        this.rightColumn = rightColumn;
    }

    public String getLeftColumn() { return leftColumn; }
    public String getRightColumn() { return rightColumn; }
}

