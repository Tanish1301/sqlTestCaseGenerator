from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class ScenarioType(str, Enum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    BOUNDARY = "BOUNDARY"


class Criticality(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class FilterCondition(BaseModel):
    column: str
    operator: str
    values: List[str] = Field(default_factory=list)


class JoinCondition(BaseModel):
    left_column: str
    right_column: str


class AggregateCondition(BaseModel):
    function: str
    column: str


class CaseCondition(BaseModel):
    condition: str
    result: str


class HavingCondition(BaseModel):
    function: str
    column: str
    operator: str
    value: str


class QueryModel(BaseModel):
    joins: List[JoinCondition] = Field(default_factory=list)
    filters: List[FilterCondition] = Field(default_factory=list)
    aggregates: List[AggregateCondition] = Field(default_factory=list)
    case_conditions: List[CaseCondition] = Field(default_factory=list)
    having_conditions: List[HavingCondition] = Field(default_factory=list)


class Scenario(BaseModel):
    id: str
    description: str
    expected_result: str
    scenario_type: ScenarioType
    criticality: Criticality


class SqlRequest(BaseModel):
    sql: str


class AIScenarioRequest(BaseModel):
    sql: str
    model: Optional[str] = None
    endpoint: Optional[str] = None
    timeout_seconds: Optional[int] = None


class HybridScenarioRequest(BaseModel):
    sql: str
    include_ai_supplement: bool = False
    model: Optional[str] = None
    endpoint: Optional[str] = None
    timeout_seconds: Optional[int] = None


class ParserValidationSummary(BaseModel):
    join_count: int
    filter_count: int
    aggregate_count: int
    having_count: int
    generated_scenarios: int


class HybridScenarioResponse(BaseModel):
    standardized: bool
    scenarios: List[Scenario]
    validation: ParserValidationSummary
    ai_used: bool
    ai_supplement: Optional[str] = None
