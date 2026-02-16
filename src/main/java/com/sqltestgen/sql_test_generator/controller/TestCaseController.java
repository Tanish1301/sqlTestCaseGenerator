package com.sqltestgen.sql_test_generator.controller;

import com.sqltestgen.sql_test_generator.generator.SemanticScenarioGenerator;
import com.sqltestgen.sql_test_generator.model.QueryModel;
import com.sqltestgen.sql_test_generator.model.Scenario;
import com.sqltestgen.sql_test_generator.parser.SqlParserService;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/testcase")
public class TestCaseController {

    private final SqlParserService sqlParserService;
    private final SemanticScenarioGenerator scenarioGenerator;

    public TestCaseController(SqlParserService sqlParserService,
                              SemanticScenarioGenerator scenarioGenerator) {
        this.sqlParserService = sqlParserService;
        this.scenarioGenerator = scenarioGenerator;
    }

    // ================= RULE BASED =================

    @PostMapping("/generate")
    public List<Scenario> generate(@RequestBody String sql) throws Exception {

        QueryModel model = sqlParserService.parseQuery(sql);
        return scenarioGenerator.generateScenarios(model);
    }

    // ================= AI BASED =================

    @PostMapping("/generate-ai")
    public String generateAI(@RequestBody String sql) {

        return scenarioGenerator.generateAIScenarios(sql);
    }
}
