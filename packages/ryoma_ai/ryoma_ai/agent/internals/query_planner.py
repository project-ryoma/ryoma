import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from ryoma_ai.agent.chat_agent import ChatAgent
from ryoma_ai.datasource.sql import SqlDataSource


class QueryComplexity(Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"


@dataclass
class QueryStep:
    """Represents a single step in a multi-step query plan."""

    step_id: int
    description: str
    sql_query: str
    depends_on: List[int]
    estimated_rows: Optional[int] = None
    execution_time_estimate: Optional[float] = None


@dataclass
class QueryPlan:
    """Represents a complete query execution plan."""

    original_question: str
    complexity: QueryComplexity
    steps: List[QueryStep]
    total_estimated_time: Optional[float] = None
    optimization_notes: List[str] = None


class QueryPlannerAgent(ChatAgent):
    """
    Specialized agent for query planning and optimization.
    Breaks down complex questions into multiple SQL steps and optimizes execution.
    """

    def __init__(
        self,
        model: str,
        model_parameters: Optional[Dict] = None,
        datasource: Optional[SqlDataSource] = None,
        **kwargs,
    ):
        super().__init__(
            model=model,
            model_parameters=model_parameters,
            datasource=datasource,
            **kwargs,
        )

    def create_query_plan(
        self, question: str, context: Optional[Dict] = None
    ) -> QueryPlan:
        """
        Create a comprehensive query plan for a complex question.

        Args:
            question: Natural language question
            context: Additional context like relevant tables, constraints

        Returns:
            QueryPlan object with steps and optimization notes
        """
        # Analyze question complexity
        complexity = self._analyze_question_complexity(question)

        # Break down into steps based on complexity
        if complexity == QueryComplexity.SIMPLE:
            steps = self._create_simple_plan(question, context)
        elif complexity == QueryComplexity.MODERATE:
            steps = self._create_moderate_plan(question, context)
        else:
            steps = self._create_complex_plan(question, context)

        # Generate optimization notes
        optimization_notes = self._generate_optimization_notes(steps, question)

        # Estimate total execution time
        total_time = sum(step.execution_time_estimate or 0 for step in steps)

        return QueryPlan(
            original_question=question,
            complexity=complexity,
            steps=steps,
            total_estimated_time=total_time,
            optimization_notes=optimization_notes,
        )

    def optimize_query_plan(self, plan: QueryPlan) -> QueryPlan:
        """
        Optimize an existing query plan for better performance.

        Args:
            plan: Original query plan

        Returns:
            Optimized query plan
        """
        optimized_steps = []

        for step in plan.steps:
            optimized_step = self._optimize_query_step(step)
            optimized_steps.append(optimized_step)

        # Look for opportunities to combine steps
        combined_steps = self._combine_steps_if_possible(optimized_steps)

        # Reorder steps for optimal execution
        reordered_steps = self._reorder_steps_for_performance(combined_steps)

        return QueryPlan(
            original_question=plan.original_question,
            complexity=plan.complexity,
            steps=reordered_steps,
            total_estimated_time=sum(
                step.execution_time_estimate or 0 for step in reordered_steps
            ),
            optimization_notes=plan.optimization_notes
            + ["Plan optimized for performance"],
        )

    def _analyze_question_complexity(self, question: str) -> QueryComplexity:
        """Analyze the complexity of a natural language question."""
        question_lower = question.lower()
        complexity_indicators = {
            "aggregation": ["sum", "count", "average", "max", "min", "total"],
            "grouping": ["by", "group", "category", "type"],
            "filtering": ["where", "filter", "only", "exclude", "include"],
            "sorting": ["top", "bottom", "highest", "lowest", "best", "worst"],
            "joining": ["and", "with", "from", "related", "associated"],
            "temporal": ["last", "first", "recent", "old", "year", "month", "day"],
            "comparison": ["more than", "less than", "greater", "smaller", "compare"],
            "ranking": ["rank", "position", "order", "sequence"],
        }

        complexity_score = 0
        for category, indicators in complexity_indicators.items():
            if any(indicator in question_lower for indicator in indicators):
                complexity_score += 1

        # Additional complexity for multiple entities
        entities = len(
            re.findall(
                r"\b(?:customer|order|product|employee|sale|payment)\w*\b",
                question_lower,
            )
        )
        complexity_score += entities

        if complexity_score <= 2:
            return QueryComplexity.SIMPLE
        elif complexity_score <= 4:
            return QueryComplexity.MODERATE
        elif complexity_score <= 6:
            return QueryComplexity.COMPLEX
        else:
            return QueryComplexity.VERY_COMPLEX

    def _create_simple_plan(
        self, question: str, context: Optional[Dict]
    ) -> List[QueryStep]:
        """Create a plan for simple questions (single query)."""
        return [
            QueryStep(
                step_id=1,
                description=f"Execute query for: {question}",
                sql_query="-- SQL query will be generated based on question",
                depends_on=[],
                execution_time_estimate=1.0,
            )
        ]

    def _create_moderate_plan(
        self, question: str, context: Optional[Dict]
    ) -> List[QueryStep]:
        """Create a plan for moderate complexity questions."""
        steps = []

        # Step 1: Data preparation/filtering
        steps.append(
            QueryStep(
                step_id=1,
                description="Filter and prepare base data",
                sql_query="-- Filter relevant records",
                depends_on=[],
                execution_time_estimate=2.0,
            )
        )

        # Step 2: Main query execution
        steps.append(
            QueryStep(
                step_id=2,
                description="Execute main query with aggregations",
                sql_query="-- Main query with joins and aggregations",
                depends_on=[1],
                execution_time_estimate=3.0,
            )
        )

        return steps

    def _create_complex_plan(
        self, question: str, context: Optional[Dict]
    ) -> List[QueryStep]:
        """Create a plan for complex questions (multiple steps)."""
        steps = []

        # Step 1: Schema analysis and table selection
        steps.append(
            QueryStep(
                step_id=1,
                description="Analyze schema and select relevant tables",
                sql_query="-- Schema analysis query",
                depends_on=[],
                execution_time_estimate=1.0,
            )
        )

        # Step 2: Data validation and preparation
        steps.append(
            QueryStep(
                step_id=2,
                description="Validate data quality and prepare datasets",
                sql_query="-- Data validation and preparation",
                depends_on=[1],
                execution_time_estimate=2.5,
            )
        )

        # Step 3: Intermediate calculations
        steps.append(
            QueryStep(
                step_id=3,
                description="Perform intermediate calculations and aggregations",
                sql_query="-- Intermediate calculations",
                depends_on=[2],
                execution_time_estimate=4.0,
            )
        )

        # Step 4: Final result compilation
        steps.append(
            QueryStep(
                step_id=4,
                description="Compile final results with formatting",
                sql_query="-- Final result query",
                depends_on=[3],
                execution_time_estimate=2.0,
            )
        )

        return steps

    def _optimize_query_step(self, step: QueryStep) -> QueryStep:
        """Optimize a single query step."""
        # This is a simplified optimization - in practice, you'd analyze the SQL
        optimized_sql = step.sql_query
        optimized_time = step.execution_time_estimate

        # Apply basic optimizations
        if "SELECT *" in step.sql_query:
            optimized_time = (optimized_time or 0) * 1.2  # Penalty for SELECT *

        if "ORDER BY" in step.sql_query and "LIMIT" not in step.sql_query:
            optimized_time = (
                optimized_time or 0
            ) * 1.3  # Penalty for unlimited ORDER BY

        return QueryStep(
            step_id=step.step_id,
            description=step.description,
            sql_query=optimized_sql,
            depends_on=step.depends_on,
            estimated_rows=step.estimated_rows,
            execution_time_estimate=optimized_time,
        )

    def _combine_steps_if_possible(self, steps: List[QueryStep]) -> List[QueryStep]:
        """Combine steps that can be executed together."""
        # This is a simplified implementation
        # In practice, you'd analyze dependencies and SQL compatibility

        combined_steps = []
        skip_next = False

        for i, step in enumerate(steps):
            if skip_next:
                skip_next = False
                continue

            # Check if next step can be combined
            if (
                i + 1 < len(steps)
                and len(step.depends_on) == 0
                and steps[i + 1].depends_on == [step.step_id]
            ):
                # Combine the steps
                combined_step = QueryStep(
                    step_id=step.step_id,
                    description=f"Combined: {step.description} + {steps[i + 1].description}",
                    sql_query=f"-- Combined query\n{step.sql_query}\n{steps[i + 1].sql_query}",
                    depends_on=step.depends_on,
                    execution_time_estimate=(step.execution_time_estimate or 0)
                    + (steps[i + 1].execution_time_estimate or 0) * 0.8,
                )
                combined_steps.append(combined_step)
                skip_next = True
            else:
                combined_steps.append(step)

        return combined_steps

    def _reorder_steps_for_performance(self, steps: List[QueryStep]) -> List[QueryStep]:
        """Reorder steps for optimal performance while respecting dependencies."""
        # Topological sort considering dependencies and performance
        # This is a simplified implementation

        # For now, just return steps in dependency order
        # In practice, you'd implement a more sophisticated algorithm
        return sorted(steps, key=lambda x: (len(x.depends_on), x.step_id))

    def _generate_optimization_notes(
        self, steps: List[QueryStep], question: str
    ) -> List[str]:
        """Generate optimization notes for the query plan."""
        notes = []

        # Check for common optimization opportunities
        if len(steps) > 3:
            notes.append("Consider using temporary tables for intermediate results")

        if any("JOIN" in step.sql_query for step in steps):
            notes.append("Ensure proper indexing on join columns")

        if any("ORDER BY" in step.sql_query for step in steps):
            notes.append("Consider adding LIMIT clauses to reduce sorting overhead")

        if "aggregate" in question.lower() or "sum" in question.lower():
            notes.append(
                "Consider using materialized views for frequently accessed aggregations"
            )

        return notes

    def explain_plan(self, plan: QueryPlan) -> str:
        """Generate a human-readable explanation of the query plan."""
        explanation = f"Query Plan for: '{plan.original_question}'\n"
        explanation += f"Complexity: {plan.complexity.value}\n"
        explanation += f"Total Steps: {len(plan.steps)}\n"
        explanation += f"Estimated Total Time: {plan.total_estimated_time:.1f}s\n\n"

        explanation += "Execution Steps:\n"
        for step in plan.steps:
            explanation += f"  {step.step_id}. {step.description}\n"
            if step.depends_on:
                explanation += (
                    f"     Depends on: {', '.join(map(str, step.depends_on))}\n"
                )
            explanation += (
                f"     Estimated time: {step.execution_time_estimate:.1f}s\n\n"
            )

        if plan.optimization_notes:
            explanation += "Optimization Notes:\n"
            for note in plan.optimization_notes:
                explanation += f"  • {note}\n"

        return explanation

    def estimate_query_cost(self, sql_query: str) -> Dict[str, Any]:
        """Estimate the cost and performance characteristics of a SQL query."""
        # This is a simplified cost estimation
        # In practice, you'd use database-specific query planners

        query_upper = sql_query.upper()

        cost_factors = {
            "table_scans": query_upper.count("FROM"),
            "joins": query_upper.count("JOIN"),
            "subqueries": query_upper.count("(SELECT"),
            "aggregations": sum(
                query_upper.count(agg)
                for agg in ["SUM(", "COUNT(", "AVG(", "MAX(", "MIN("]
            ),
            "sorts": query_upper.count("ORDER BY"),
            "groups": query_upper.count("GROUP BY"),
        }

        # Calculate relative cost score
        base_cost = 1.0
        cost_multipliers = {
            "table_scans": 1.2,
            "joins": 2.0,
            "subqueries": 1.8,
            "aggregations": 1.5,
            "sorts": 1.3,
            "groups": 1.4,
        }

        total_cost = base_cost
        for factor, count in cost_factors.items():
            total_cost *= cost_multipliers[factor] ** count

        return {
            "estimated_cost": round(total_cost, 2),
            "cost_factors": cost_factors,
            "performance_category": self._categorize_performance(total_cost),
            "recommendations": self._get_performance_recommendations(cost_factors),
        }

    def _categorize_performance(self, cost: float) -> str:
        """Categorize query performance based on cost."""
        if cost < 2.0:
            return "Fast"
        elif cost < 5.0:
            return "Moderate"
        elif cost < 10.0:
            return "Slow"
        else:
            return "Very Slow"

    def _get_performance_recommendations(
        self, cost_factors: Dict[str, int]
    ) -> List[str]:
        """Get performance recommendations based on cost factors."""
        recommendations = []

        if cost_factors["joins"] > 3:
            recommendations.append(
                "Consider reducing the number of joins or using subqueries"
            )

        if cost_factors["subqueries"] > 2:
            recommendations.append(
                "Consider converting subqueries to joins where possible"
            )

        if cost_factors["sorts"] > 1:
            recommendations.append(
                "Multiple ORDER BY clauses detected - consider combining or using indexes"
            )

        if cost_factors["aggregations"] > 3:
            recommendations.append(
                "Heavy aggregation detected - consider using summary tables"
            )

        return recommendations
