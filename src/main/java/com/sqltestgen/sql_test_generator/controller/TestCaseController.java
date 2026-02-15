package com.sqltestgen.sql_test_generator.controller;

import com.sqltestgen.sql_test_generator.generator.ScenarioGenerator;
import com.sqltestgen.sql_test_generator.model.Scenario;
import com.sqltestgen.sql_test_generator.model.FilterCondition;
import com.sqltestgen.sql_test_generator.parser.SqlParserService;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/testcase")
public class TestCaseController {

    private final SqlParserService sqlParserService;
    private final ScenarioGenerator scenarioGenerator;

    public TestCaseController(SqlParserService sqlParserService,
                              ScenarioGenerator scenarioGenerator) {
        this.sqlParserService = sqlParserService;
        this.scenarioGenerator = scenarioGenerator;
    }

    @PostMapping("/generate")
    public List<Scenario> generate(@RequestBody String sql) throws Exception {

        List<FilterCondition> conditions = sqlParserService.extractConditions(sql);
        return scenarioGenerator.generateScenarios(conditions);
    }
}
