package com.sqltestgen.sql_test_generator.generator;

import com.sqltestgen.sql_test_generator.model.*;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
public class ScenarioGenerator {

    public List<Scenario> generateScenarios(List<FilterCondition> conditions) {

        List<Scenario> scenarios = new ArrayList<>();
        int id = 1;

        for (FilterCondition condition : conditions) {

            String column = condition.getColumn();
            String operator = condition.getOperator();
            List<String> values = condition.getValues();
            String value = values.isEmpty() ? "" : values.get(0);

            if (">".equals(operator)) {

                scenarios.add(createScenario(id++, column + " > " + value,
                        "Records should be returned",
                        operator,
                        TestIntent.MATCH));

                scenarios.add(createScenario(id++, column + " = " + value,
                        "Boundary condition validation",
                        operator,
                        TestIntent.EQUAL));

                scenarios.add(createScenario(id++, column + " < " + value,
                        "No records should be returned",
                        operator,
                        TestIntent.LESS));

                scenarios.add(createScenario(id++, column + " IS NULL",
                        "System should handle NULL appropriately",
                        operator,
                        TestIntent.NULL_CHECK));
            }

            if ("=".equals(operator)) {

                scenarios.add(createScenario(id++, column + " = " + value,
                        "Records should be returned",
                        operator,
                        TestIntent.MATCH));

                scenarios.add(createScenario(id++, column + " != " + value,
                        "No records should be returned",
                        operator,
                        TestIntent.NOT_MATCH));

                scenarios.add(createScenario(id++, column + " IS NULL",
                        "System should handle NULL appropriately",
                        operator,
                        TestIntent.NULL_CHECK));
            }
            if ("BETWEEN".equalsIgnoreCase(operator)) {

                String lower = values.get(0);
                String upper = values.get(1);

                scenarios.add(createScenario(id++, column + " BETWEEN " + lower + " AND " + upper,
                        "Records within range should be returned",
                        operator,
                        TestIntent.MATCH));

                scenarios.add(createScenario(id++, column + " = " + lower,
                        "Lower boundary validation",
                        operator,
                        TestIntent.EQUAL));

                scenarios.add(createScenario(id++, column + " = " + upper,
                        "Upper boundary validation",
                        operator,
                        TestIntent.EQUAL));

                scenarios.add(createScenario(id++, column + " < " + lower,
                        "Below range should not return records",
                        operator,
                        TestIntent.LESS));

                scenarios.add(createScenario(id++, column + " > " + upper,
                        "Above range should not return records",
                        operator,
                        TestIntent.NOT_MATCH));

                scenarios.add(createScenario(id++, column + " IS NULL",
                        "System should handle NULL appropriately",
                        operator,
                        TestIntent.NULL_CHECK));
            }
            if ("IN".equalsIgnoreCase(operator)) {

                scenarios.add(createScenario(id++, column + " IN " + values,
                        "Records matching values should be returned",
                        operator,
                        TestIntent.MATCH));

                scenarios.add(createScenario(id++, column + " NOT IN " + values,
                        "Records outside list should not be returned",
                        operator,
                        TestIntent.NOT_MATCH));

                scenarios.add(createScenario(id++, column + " IS NULL",
                        "System should handle NULL appropriately",
                        operator,
                        TestIntent.NULL_CHECK));
            }


        }

        return scenarios;
    }

    private Scenario createScenario(int id,
                                    String description,
                                    String expected,
                                    String operator,
                                    TestIntent intent) {

        ScenarioType type = determineScenarioType(operator, intent);
        Criticality criticality = determineCriticality(type);

        return new Scenario(
                "TC_" + id,
                description,
                expected,
                type,
                criticality
        );
    }

    private ScenarioType determineScenarioType(String operator, TestIntent intent) {

        switch (operator) {

            case ">":
                switch (intent) {
                    case MATCH: return ScenarioType.POSITIVE;
                    case EQUAL: return ScenarioType.BOUNDARY;
                    case LESS:
                    case NULL_CHECK:
                        return ScenarioType.NEGATIVE;
                }
                break;

            case "=":
                switch (intent) {
                    case MATCH: return ScenarioType.POSITIVE;
                    case NOT_MATCH:
                    case NULL_CHECK:
                        return ScenarioType.NEGATIVE;
                }
                break;

            case "BETWEEN":
                switch (intent) {
                    case MATCH:
                        return ScenarioType.POSITIVE;
                    case EQUAL:
                        return ScenarioType.BOUNDARY;
                    case LESS:
                    case NOT_MATCH:
                    case NULL_CHECK:
                        return ScenarioType.NEGATIVE;
                }
                break;

            case "IN":
                switch (intent) {
                    case MATCH:
                        return ScenarioType.POSITIVE;
                    case NOT_MATCH:
                    case NULL_CHECK:
                        return ScenarioType.NEGATIVE;
                }
                break;



        }

        return ScenarioType.NEGATIVE;
    }

    private Criticality determineCriticality(ScenarioType type) {

        if (type == ScenarioType.BOUNDARY) {
            return Criticality.HIGH;
        }

        if (type == ScenarioType.NEGATIVE) {
            return Criticality.MEDIUM;
        }

        return Criticality.MEDIUM;
    }


}
