package com.sqltestgen.sql_test_generator.model;

public class Scenario {

    private String id;
    private String description;
    private String expectedResult;
    private ScenarioType scenarioType;
    private Criticality criticality;

    public Scenario(String id,
                    String description,
                    String expectedResult,
                    ScenarioType scenarioType,
                    Criticality criticality) {
        this.id = id;
        this.description = description;
        this.expectedResult = expectedResult;
        this.scenarioType = scenarioType;
        this.criticality = criticality;
    }

    public String getId() { return id; }
    public String getDescription() { return description; }
    public String getExpectedResult() { return expectedResult; }
    public ScenarioType getScenarioType() { return scenarioType; }
    public Criticality getCriticality() { return criticality; }
}
