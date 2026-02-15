package com.sqltestgen.sql_test_generator.parser;

import com.sqltestgen.sql_test_generator.model.FilterCondition;
import net.sf.jsqlparser.expression.Expression;
import net.sf.jsqlparser.expression.ExpressionVisitorAdapter;
import net.sf.jsqlparser.expression.operators.relational.Between;
import net.sf.jsqlparser.expression.operators.relational.EqualsTo;
import net.sf.jsqlparser.expression.operators.relational.GreaterThan;
import net.sf.jsqlparser.expression.operators.relational.InExpression;
import net.sf.jsqlparser.expression.operators.relational.ExpressionList;
import net.sf.jsqlparser.expression.operators.conditional.AndExpression;
import net.sf.jsqlparser.expression.operators.conditional.OrExpression;
import net.sf.jsqlparser.parser.CCJSqlParserUtil;
import net.sf.jsqlparser.statement.Statement;
import net.sf.jsqlparser.statement.select.PlainSelect;
import net.sf.jsqlparser.statement.select.Select;
import net.sf.jsqlparser.statement.select.WithItem;
import net.sf.jsqlparser.statement.select.SubSelect;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
public class SqlParserService {

    public List<FilterCondition> extractConditions(String sql) throws Exception {

        Statement statement = CCJSqlParserUtil.parse(sql);
        Select select = (Select) statement;

        List<FilterCondition> conditions = new ArrayList<>();

        // Main SELECT
        if (select.getSelectBody() instanceof PlainSelect plainSelect) {
            extractFromPlainSelect(plainSelect, conditions);
        }

        // WITH CTE
        if (select.getWithItemsList() != null) {
            for (WithItem withItem : select.getWithItemsList()) {

                SubSelect subSelect = withItem.getSubSelect();

                if (subSelect != null &&
                        subSelect.getSelectBody() instanceof PlainSelect ctePlainSelect) {

                    extractFromPlainSelect(ctePlainSelect, conditions);
                }
            }
        }

        return conditions;
    }

    private void extractFromPlainSelect(PlainSelect plainSelect,
                                        List<FilterCondition> conditions) {

        Expression where = plainSelect.getWhere();
        if (where == null) return;

        where.accept(new ExpressionVisitorAdapter() {

            // AND
            @Override
            public void visit(AndExpression expr) {
                expr.getLeftExpression().accept(this);
                expr.getRightExpression().accept(this);
            }

            // OR
            @Override
            public void visit(OrExpression expr) {
                expr.getLeftExpression().accept(this);
                expr.getRightExpression().accept(this);
            }

            // Equals
            @Override
            public void visit(EqualsTo expr) {
                conditions.add(new FilterCondition(
                        expr.getLeftExpression().toString(),
                        "=",
                        List.of(expr.getRightExpression().toString())
                ));
            }

            // Greater Than
            @Override
            public void visit(GreaterThan expr) {
                conditions.add(new FilterCondition(
                        expr.getLeftExpression().toString(),
                        ">",
                        List.of(expr.getRightExpression().toString())
                ));
            }

            // BETWEEN
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

            // IN (list + subquery)
            @Override
            public void visit(InExpression expr) {

                String column = expr.getLeftExpression().toString();

                // Simple IN (10,20,30)
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

                // Subquery IN
                else if (expr.getRightItemsList() instanceof SubSelect subSelect) {

                    conditions.add(new FilterCondition(
                            column,
                            "IN_SUBQUERY",
                            List.of(subSelect.toString())
                    ));
                }
            }
        });
    }
}
