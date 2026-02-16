package com.sqltestgen.sql_test_generator.parser;

import com.sqltestgen.sql_test_generator.model.*;
import net.sf.jsqlparser.expression.*;
import net.sf.jsqlparser.expression.operators.conditional.AndExpression;
import net.sf.jsqlparser.expression.operators.conditional.OrExpression;
import net.sf.jsqlparser.expression.operators.relational.*;
import net.sf.jsqlparser.parser.CCJSqlParserUtil;
import net.sf.jsqlparser.schema.Column;
import net.sf.jsqlparser.statement.Statement;
import net.sf.jsqlparser.statement.select.*;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
public class SqlParserService {

    public QueryModel parseQuery(String sql) throws Exception {

        Statement statement = CCJSqlParserUtil.parse(sql);
        Select select = (Select) statement;
        PlainSelect plainSelect = (PlainSelect) select.getSelectBody();

        List<FilterCondition> filters = new ArrayList<>();
        List<JoinCondition> joins = new ArrayList<>();
        List<AggregateCondition> aggregates = new ArrayList<>();
        List<HavingCondition> havingConditions = new ArrayList<>();
        List<CaseCondition> caseConditions = new ArrayList<>();

        extractFilters(plainSelect, filters);
        extractJoins(plainSelect, joins);
        extractAggregates(plainSelect, aggregates);
        extractHaving(plainSelect, havingConditions);

        return new QueryModel(
                joins,
                filters,
                aggregates,
                caseConditions,
                havingConditions
        );
    }

    // ================= FILTER EXTRACTION =================

    private void extractFilters(PlainSelect plainSelect,
                                List<FilterCondition> conditions) {

        Expression where = plainSelect.getWhere();
        if (where == null) return;

        where.accept(new ExpressionVisitorAdapter() {

            @Override
            public void visit(AndExpression expr) {
                expr.getLeftExpression().accept(this);
                expr.getRightExpression().accept(this);
            }

            @Override
            public void visit(OrExpression expr) {
                expr.getLeftExpression().accept(this);
                expr.getRightExpression().accept(this);
            }

            @Override
            public void visit(EqualsTo expr) {
                conditions.add(new FilterCondition(
                        expr.getLeftExpression().toString(),
                        "=",
                        List.of(expr.getRightExpression().toString())
                ));
            }

            @Override
            public void visit(GreaterThan expr) {
                conditions.add(new FilterCondition(
                        expr.getLeftExpression().toString(),
                        ">",
                        List.of(expr.getRightExpression().toString())
                ));
            }

            @Override
            public void visit(Between expr) {
                conditions.add(new FilterCondition(
                        expr.getLeftExpression().toString(),
                        "BETWEEN",
                        List.of(
                                expr.getBetweenExpressionStart().toString(),
                                expr.getBetweenExpressionEnd().toString()
                        )
                ));
            }

            @Override
            public void visit(InExpression expr) {

                String column = expr.getLeftExpression().toString();

                if (expr.getRightItemsList() instanceof ExpressionList expressionList) {

                    List<String> values = new ArrayList<>();

                    for (Expression valueExpr : expressionList.getExpressions()) {
                        values.add(valueExpr.toString());
                    }

                    conditions.add(new FilterCondition(
                            column,
                            "IN",
                            values
                    ));
                }
            }
        });
    }

    // ================= JOIN EXTRACTION =================

    private void extractJoins(PlainSelect plainSelect,
                              List<JoinCondition> joins) {

        if (plainSelect.getJoins() == null) return;

        for (Join join : plainSelect.getJoins()) {

            Expression onExpr = join.getOnExpression();
            if (onExpr instanceof EqualsTo equalsTo) {

                joins.add(new JoinCondition(
                        equalsTo.getLeftExpression().toString(),
                        equalsTo.getRightExpression().toString()
                ));
            }
        }
    }

    // ================= AGGREGATE EXTRACTION =================

    private void extractAggregates(PlainSelect plainSelect,
                                   List<AggregateCondition> aggregates) {

        for (SelectItem item : plainSelect.getSelectItems()) {

            if (item instanceof SelectExpressionItem expressionItem) {

                Expression expression = expressionItem.getExpression();

                if (expression instanceof Function function) {

                    String functionName = function.getName();

                    if (function.getParameters() != null) {

                        List<Expression> expressions =
                                function.getParameters().getExpressions();

                        if (!expressions.isEmpty()) {

                            aggregates.add(new AggregateCondition(
                                    functionName.toUpperCase(),
                                    expressions.get(0).toString()
                            ));
                        }
                    }
                }
            }
        }
    }

    // ================= HAVING EXTRACTION =================

    private void extractHaving(PlainSelect plainSelect,
                               List<HavingCondition> havingConditions) {

        Expression having = plainSelect.getHaving();
        if (having == null) return;

        if (having instanceof GreaterThan greaterThan) {

            if (greaterThan.getLeftExpression() instanceof Function function) {

                String functionName = function.getName();
                String column = function.getParameters()
                        .getExpressions().get(0).toString();

                havingConditions.add(new HavingCondition(
                        functionName.toUpperCase(),
                        column,
                        ">",
                        greaterThan.getRightExpression().toString()
                ));
            }
        }

        if (having instanceof EqualsTo equalsTo) {

            if (equalsTo.getLeftExpression() instanceof Function function) {

                String functionName = function.getName();
                String column = function.getParameters()
                        .getExpressions().get(0).toString();

                havingConditions.add(new HavingCondition(
                        functionName.toUpperCase(),
                        column,
                        "=",
                        equalsTo.getRightExpression().toString()
                ));
            }
        }
    }
}
