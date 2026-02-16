package com.sqltestgen.sql_test_generator.model;

import java.util.List;

public class QueryModel {

    private List<JoinCondition> joins;
    private List<FilterCondition> filters;
    private List<AggregateCondition> aggregates;
    private List<CaseCondition> caseConditions;
    private List<HavingCondition> havingConditions;

    public QueryModel(List<JoinCondition> joins,
                      List<FilterCondition> filters,
                      List<AggregateCondition> aggregates,
                      List<CaseCondition> caseConditions,
                      List<HavingCondition> havingConditions) {

        this.joins = joins;
        this.filters = filters;
        this.aggregates = aggregates;
        this.caseConditions = caseConditions;
        this.havingConditions = havingConditions;
    }

    public List<JoinCondition> getJoins() {
        return joins;
    }

    public List<FilterCondition> getFilters() {
        return filters;
    }

    public List<AggregateCondition> getAggregates() {
        return aggregates;
    }

    public List<CaseCondition> getCaseConditions() {
        return caseConditions;
    }

    public List<HavingCondition> getHavingConditions() {
        return havingConditions;
    }
}
