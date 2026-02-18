from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.models import (
    AIScenarioRequest,
    HybridScenarioRequest,
    HybridScenarioResponse,
    ParserValidationSummary,
    QueryModel,
    Scenario,
    SqlRequest,
)
from app.ollama_service import OllamaService
from app.parser_service import SqlParserService
from app.scenario_generator import SemanticScenarioGenerator

app = FastAPI(title="SQL Test Generator (Python)")

parser_service = SqlParserService()
ollama_service = OllamaService()
scenario_generator = SemanticScenarioGenerator(ollama_service)


class AIScenarioResponse(BaseModel):
    scenarios: str


@app.post("/testcase/generate", response_model=list[Scenario])
def generate(request: SqlRequest) -> list[Scenario]:
    try:
        model: QueryModel = parser_service.parse_query(request.sql)
        return scenario_generator.generate_scenarios(model)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/testcase/generate-ai", response_model=AIScenarioResponse)
def generate_ai(request: AIScenarioRequest) -> AIScenarioResponse:
    try:
        result = scenario_generator.generate_ai_scenarios(
            request.sql,
            model=request.model,
            endpoint=request.endpoint,
            timeout_seconds=request.timeout_seconds,
        )
        return AIScenarioResponse(scenarios=result)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/testcase/generate-hybrid", response_model=HybridScenarioResponse)
def generate_hybrid(request: HybridScenarioRequest) -> HybridScenarioResponse:
    try:
        model: QueryModel = parser_service.parse_query(request.sql)
        scenarios = scenario_generator.generate_scenarios(model)

        ai_supplement = None
        ai_used = bool(request.include_ai_supplement)
        if request.include_ai_supplement:
            ai_supplement = scenario_generator.generate_ai_scenarios(
                request.sql,
                model=request.model,
                endpoint=request.endpoint,
                timeout_seconds=request.timeout_seconds,
            )

        summary = ParserValidationSummary(
            join_count=len(model.joins),
            filter_count=len(model.filters),
            aggregate_count=len(model.aggregates),
            having_count=len(model.having_conditions),
            generated_scenarios=len(scenarios),
        )

        return HybridScenarioResponse(
            standardized=True,
            scenarios=scenarios,
            validation=summary,
            ai_used=ai_used,
            ai_supplement=ai_supplement,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
