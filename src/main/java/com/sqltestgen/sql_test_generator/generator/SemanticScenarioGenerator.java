package com.sqltestgen.sql_test_generator.generator;

import com.sqltestgen.sql_test_generator.model.*;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Service
public class SemanticScenarioGenerator {

    private final OllamaService ollamaService;

    public SemanticScenarioGenerator(OllamaService ollamaService) {
        this.ollamaService = ollamaService;
    }

    // ================= RULE BASED ENGINE =================

    public List<Scenario> generateScenarios(QueryModel model) {

        List<Scenario> scenarios = new ArrayList<>();

        for (FilterCondition filter : model.getFilters()) {
            scenarios.addAll(generateFilterScenarios(filter));
        }

        for (JoinCondition join : model.getJoins()) {
            scenarios.addAll(generateJoinScenarios(join));
        }

        for (AggregateCondition aggregate : model.getAggregates()) {
            scenarios.addAll(generateAggregateScenarios(aggregate));
        }

        for (HavingCondition having : model.getHavingConditions()) {
            scenarios.addAll(generateHavingScenarios(having));
        }

        return scenarios;
    }

    // ================= AI ENGINE =================

    public String generateAIScenarios(String sqlQuery) {

        String prompt = """
        You are a professional QA engineer.

        Generate structured SQL test scenarios for the following query.

        Include:
        - Positive cases
        - Negative cases
        - Boundary cases
        - Edge cases

        SQL Query:
        """ + sqlQuery;

        return ollamaService.generate(prompt);
    }

    // ================= FILTER =================

    private List<Scenario> generateFilterScenarios(FilterCondition filter) {

        List<Scenario> scenarios = new ArrayList<>();

        scenarios.add(new Scenario(
                UUID.randomUUID().toString(),
                "Verify " + filter.getColumn() + " satisfies condition " + filter.getOperator(),
                "Rows matching condition should be returned",
                ScenarioType.POSITIVE,
                Criticality.HIGH
        ));

        scenarios.add(new Scenario(
                UUID.randomUUID().toString(),
                "Verify rows not satisfying " + filter.getColumn() + " condition are excluded",
                "Non matching rows should not appear",
                ScenarioType.NEGATIVE,
                Criticality.HIGH
        ));

        return scenarios;
    }

    // ================= JOIN =================

    private List<Scenario> generateJoinScenarios(JoinCondition join) {

        List<Scenario> scenarios = new ArrayList<>();

        scenarios.add(new Scenario(
                UUID.randomUUID().toString(),
                "Verify join between " + join.getLeftColumn() + " and " + join.getRightColumn(),
                "Only matching rows across tables should be returned",
                ScenarioType.POSITIVE,
                Criticality.CRITICAL
        ));

        scenarios.add(new Scenario(
                UUID.randomUUID().toString(),
                "Verify behavior when join condition fails",
                "Rows without matching join should not appear",
                ScenarioType.NEGATIVE,
                Criticality.HIGH
        ));

        return scenarios;
    }

    // ================= AGGREGATE =================

    private List<Scenario> generateAggregateScenarios(AggregateCondition aggregate) {

        List<Scenario> scenarios = new ArrayList<>();

        scenarios.add(new Scenario(
                UUID.randomUUID().toString(),
                "Verify " + aggregate.getFunction() +
                        " aggregation on column " + aggregate.getColumn(),
                "Aggregation should compute correct value",
                ScenarioType.POSITIVE,
                Criticality.CRITICAL
        ));

        scenarios.add(new Scenario(
                UUID.randomUUID().toString(),
                "Verify aggregation handles null values correctly",
                "Null values should not break aggregation logic",
                ScenarioType.BOUNDARY,
                Criticality.MEDIUM
        ));

        return scenarios;
    }

    // ================= HAVING =================

    private List<Scenario> generateHavingScenarios(HavingCondition having) {

        List<Scenario> scenarios = new ArrayList<>();

        scenarios.add(new Scenario(
                UUID.randomUUID().toString(),
                "Verify HAVING condition on " + having.getFunction()
                        + "(" + having.getColumn() + ")",
                "Only groups satisfying HAVING condition should appear",
                ScenarioType.POSITIVE,
                Criticality.CRITICAL
        ));

        scenarios.add(new Scenario(
                UUID.randomUUID().toString(),
                "Verify groups not satisfying HAVING condition are excluded",
                "Invalid groups should not be returned",
                ScenarioType.NEGATIVE,
                Criticality.HIGH
        ));

        return scenarios;
    }
}
