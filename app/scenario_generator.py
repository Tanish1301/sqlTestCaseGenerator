import hashlib
from typing import Optional

from app.models import Criticality, FilterCondition, QueryModel, Scenario, ScenarioType
from app.ollama_service import OllamaService


class SemanticScenarioGenerator:
    def __init__(self, ollama_service: OllamaService):
        self.ollama_service = ollama_service

    def generate_scenarios(self, model: QueryModel) -> list[Scenario]:
        scenarios: list[Scenario] = []
        seen: set[tuple[str, str, ScenarioType, Criticality]] = set()

        for filter_condition in model.filters:
            for scenario in self._generate_filter_scenarios(filter_condition):
                self._append_unique(scenarios, seen, scenario)

        for join in model.joins:
            self._append_unique(
                scenarios,
                seen,
                self._build_scenario(
                    description=f"Verify join between {join.left_column} and {join.right_column}",
                    expected_result="Only matching rows across tables should be returned",
                    scenario_type=ScenarioType.POSITIVE,
                    criticality=Criticality.CRITICAL,
                ),
            )
            self._append_unique(
                scenarios,
                seen,
                self._build_scenario(
                    description=f"Verify behavior when join condition between {join.left_column} and {join.right_column} fails",
                    expected_result="Rows without matching join should not appear",
                    scenario_type=ScenarioType.NEGATIVE,
                    criticality=Criticality.HIGH,
                ),
            )

        for aggregate in model.aggregates:
            self._append_unique(
                scenarios,
                seen,
                self._build_scenario(
                    description=f"Verify {aggregate.function} aggregation on column {aggregate.column}",
                    expected_result="Aggregation should compute correct value",
                    scenario_type=ScenarioType.POSITIVE,
                    criticality=Criticality.CRITICAL,
                ),
            )
            self._append_unique(
                scenarios,
                seen,
                self._build_scenario(
                    description=f"Verify {aggregate.function} aggregation handles null values correctly on {aggregate.column}",
                    expected_result="Null values should not break aggregation logic",
                    scenario_type=ScenarioType.BOUNDARY,
                    criticality=Criticality.MEDIUM,
                ),
            )

        for having in model.having_conditions:
            self._append_unique(
                scenarios,
                seen,
                self._build_scenario(
                    description=f"Verify HAVING condition on {having.function}({having.column}) {having.operator} {having.value}",
                    expected_result="Only groups satisfying HAVING condition should appear",
                    scenario_type=ScenarioType.POSITIVE,
                    criticality=Criticality.CRITICAL,
                ),
            )
            self._append_unique(
                scenarios,
                seen,
                self._build_scenario(
                    description=f"Verify groups not satisfying HAVING condition {having.function}({having.column}) {having.operator} {having.value} are excluded",
                    expected_result="Invalid groups should not be returned",
                    scenario_type=ScenarioType.NEGATIVE,
                    criticality=Criticality.HIGH,
                ),
            )

        return sorted(
            scenarios,
            key=lambda s: (s.scenario_type.value, s.criticality.value, s.description, s.expected_result),
        )

    def generate_ai_scenarios(
        self,
        sql_query: str,
        model: Optional[str] = None,
        endpoint: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
    ) -> str:
        prompt = (
            "You are a professional QA engineer.\n\n"
            "Generate structured SQL test scenarios for the following query.\n\n"
            "Include:\n"
            "- Positive cases\n"
            "- Negative cases\n"
            "- Boundary cases\n"
            "- Edge cases\n\n"
            f"SQL Query:\n{sql_query}"
        )
        return self.ollama_service.generate(
            prompt,
            model=model,
            endpoint=endpoint,
            timeout_seconds=timeout_seconds,
        )

    def _generate_filter_scenarios(self, filter_condition: FilterCondition) -> list[Scenario]:
        return [
            self._build_scenario(
                description=f"Verify {filter_condition.column} satisfies condition {filter_condition.operator}",
                expected_result="Rows matching condition should be returned",
                scenario_type=ScenarioType.POSITIVE,
                criticality=Criticality.HIGH,
            ),
            self._build_scenario(
                description=f"Verify rows not satisfying {filter_condition.column} condition are excluded",
                expected_result="Non matching rows should not appear",
                scenario_type=ScenarioType.NEGATIVE,
                criticality=Criticality.HIGH,
            ),
        ]

    def _build_scenario(
        self,
        description: str,
        expected_result: str,
        scenario_type: ScenarioType,
        criticality: Criticality,
    ) -> Scenario:
        stable_input = f"{description}|{expected_result}|{scenario_type.value}|{criticality.value}"
        stable_id = hashlib.sha1(stable_input.encode("utf-8")).hexdigest()[:16]
        return Scenario(
            id=stable_id,
            description=description,
            expected_result=expected_result,
            scenario_type=scenario_type,
            criticality=criticality,
        )

    def _append_unique(
        self,
        scenarios: list[Scenario],
        seen: set[tuple[str, str, ScenarioType, Criticality]],
        scenario: Scenario,
    ) -> None:
        key = (scenario.description, scenario.expected_result, scenario.scenario_type, scenario.criticality)
        if key in seen:
            return
        seen.add(key)
        scenarios.append(scenario)
