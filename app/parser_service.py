from typing import List, Set, Tuple

from sqlglot import exp, parse_one

from app.models import (
    AggregateCondition,
    FilterCondition,
    HavingCondition,
    JoinCondition,
    QueryModel,
)


class SqlParserService:
    def parse_query(self, sql: str) -> QueryModel:
        tree = parse_one(sql, read="oracle")
        if not self._is_supported_statement(tree):
            raise ValueError("Only SELECT or MERGE queries are supported")

        filters: List[FilterCondition] = []
        joins: List[JoinCondition] = []
        aggregates: List[AggregateCondition] = []
        having_conditions: List[HavingCondition] = []

        self._extract_filters(tree, filters)
        self._extract_joins(tree, joins)
        self._extract_aggregates(tree, aggregates)
        self._extract_having(tree, having_conditions)

        return QueryModel(
            joins=joins,
            filters=filters,
            aggregates=aggregates,
            having_conditions=having_conditions,
        )

    def _is_supported_statement(self, tree: exp.Expression) -> bool:
        return isinstance(tree, (exp.Select, exp.Merge)) or tree.find(exp.Select) is not None

    def _extract_filters(self, tree: exp.Expression, conditions: List[FilterCondition]) -> None:
        seen: Set[Tuple[str, str, Tuple[str, ...]]] = set()
        for where in tree.find_all(exp.Where):
            self._walk_filter_expr(where.this, conditions, seen)

    def _walk_filter_expr(
        self,
        expression: exp.Expression,
        conditions: List[FilterCondition],
        seen: Set[Tuple[str, str, Tuple[str, ...]]],
    ) -> None:
        if expression is None:
            return
        if isinstance(expression, exp.Paren):
            self._walk_filter_expr(expression.this, conditions, seen)
            return

        if isinstance(expression, (exp.And, exp.Or)):
            self._walk_filter_expr(expression.left, conditions, seen)
            self._walk_filter_expr(expression.right, conditions, seen)
            return

        for expr_type, operator in (
            (exp.EQ, "="),
            (exp.GT, ">"),
            (exp.GTE, ">="),
            (exp.LT, "<"),
            (exp.LTE, "<="),
            (exp.NEQ, "!="),
            (exp.Like, "LIKE"),
        ):
            if isinstance(expression, expr_type):
                self._add_filter_condition(
                    conditions,
                    seen,
                    column=expression.left.sql(),
                    operator=operator,
                    values=[expression.right.sql()],
                )
                return

        if isinstance(expression, exp.Between):
            self._add_filter_condition(
                conditions,
                seen,
                column=expression.this.sql(),
                operator="BETWEEN",
                values=[expression.args["low"].sql(), expression.args["high"].sql()],
            )
            return

        if isinstance(expression, exp.In):
            values = [value.sql() for value in expression.expressions]
            self._add_filter_condition(
                conditions,
                seen,
                column=expression.this.sql(),
                operator="IN",
                values=values,
            )
            return

        if isinstance(expression, exp.Not) and isinstance(expression.this, exp.In):
            in_expr = expression.this
            values = [value.sql() for value in in_expr.expressions]
            self._add_filter_condition(
                conditions,
                seen,
                column=in_expr.this.sql(),
                operator="NOT IN",
                values=values,
            )
            return

        if isinstance(expression, exp.Is):
            self._add_filter_condition(
                conditions,
                seen,
                column=expression.this.sql(),
                operator="IS",
                values=[expression.expression.sql()],
            )

    def _add_filter_condition(
        self,
        conditions: List[FilterCondition],
        seen: Set[Tuple[str, str, Tuple[str, ...]]],
        column: str,
        operator: str,
        values: List[str],
    ) -> None:
        key = (column, operator, tuple(values))
        if key in seen:
            return
        seen.add(key)
        conditions.append(FilterCondition(column=column, operator=operator, values=values))

    def _extract_joins(self, tree: exp.Expression, joins: List[JoinCondition]) -> None:
        seen: Set[Tuple[str, str]] = set()
        for join in tree.find_all(exp.Join):
            on_expr = join.args.get("on")
            self._walk_join_expr(on_expr, joins, seen)

        for merge in tree.find_all(exp.Merge):
            on_expr = merge.args.get("on")
            self._walk_join_expr(on_expr, joins, seen)

    def _walk_join_expr(
        self,
        expression: exp.Expression,
        joins: List[JoinCondition],
        seen: Set[Tuple[str, str]],
    ) -> None:
        if expression is None:
            return
        if isinstance(expression, exp.Paren):
            self._walk_join_expr(expression.this, joins, seen)
            return
        if isinstance(expression, (exp.And, exp.Or)):
            self._walk_join_expr(expression.left, joins, seen)
            self._walk_join_expr(expression.right, joins, seen)
            return
        if not isinstance(expression, (exp.EQ, exp.GT, exp.GTE, exp.LT, exp.LTE, exp.NEQ)):
            return

        left = expression.left.sql() if expression.left else None
        right = expression.right.sql() if expression.right else None
        if not left or not right:
            return
        if "." not in left and "." not in right:
            return
        key = (left, right)
        if key in seen:
            return
        seen.add(key)
        joins.append(JoinCondition(left_column=left, right_column=right))

    def _extract_aggregates(self, tree: exp.Expression, aggregates: List[AggregateCondition]) -> None:
        seen: Set[Tuple[str, str]] = set()
        for select in tree.find_all(exp.Select):
            for select_expr in select.expressions:
                target = select_expr.this if isinstance(select_expr, exp.Alias) else select_expr
                if isinstance(target, exp.AggFunc):
                    column_expr = target.this or (target.expressions[0] if target.expressions else None)
                    if column_expr is not None:
                        key = (target.key.upper(), column_expr.sql())
                        if key in seen:
                            continue
                        seen.add(key)
                        aggregates.append(
                            AggregateCondition(
                                function=target.key.upper(),
                                column=column_expr.sql(),
                            )
                        )

    def _extract_having(self, tree: exp.Expression, having_conditions: List[HavingCondition]) -> None:
        seen: Set[Tuple[str, str, str, str]] = set()
        for select in tree.find_all(exp.Select):
            having = select.args.get("having")
            if having is None:
                continue
            self._walk_having_expr(having.this, having_conditions, seen)

    def _walk_having_expr(
        self,
        expression: exp.Expression,
        having_conditions: List[HavingCondition],
        seen: Set[Tuple[str, str, str, str]],
    ) -> None:
        if expression is None:
            return
        if isinstance(expression, exp.Paren):
            self._walk_having_expr(expression.this, having_conditions, seen)
            return

        if isinstance(expression, (exp.And, exp.Or)):
            self._walk_having_expr(expression.left, having_conditions, seen)
            self._walk_having_expr(expression.right, having_conditions, seen)
            return

        operator = None
        for expr_type, value in (
            (exp.GT, ">"),
            (exp.GTE, ">="),
            (exp.EQ, "="),
            (exp.LT, "<"),
            (exp.LTE, "<="),
            (exp.NEQ, "!="),
        ):
            if isinstance(expression, expr_type):
                operator = value
                break

        if operator is None or not isinstance(expression.left, exp.AggFunc):
            return

        func = expression.left
        column_expr = func.this or (func.expressions[0] if func.expressions else None)
        if column_expr is None:
            return

        value = expression.right.sql() if expression.right else ""
        key = (func.key.upper(), column_expr.sql(), operator, value)
        if key in seen:
            return
        seen.add(key)
        having_conditions.append(
            HavingCondition(
                function=func.key.upper(),
                column=column_expr.sql(),
                operator=operator,
                value=value,
            )
        )
