from typing import List, Any, Dict

from models.element import ElementData, ElementType
from solvers.base import BaseSolver
from utils.assertions import assert_valid_dimensions, assert_non_negative, assert_positive
from utils.helpers import format_tensor, tab_out, calculate_priority_order, get_completion_times, lp_sum


class ElementSolver(BaseSolver):
    """Solver for element-level optimization problems."""

    def __init__(self, data: ElementData):
        super().__init__()
        # Validate input dimensions
        assert_valid_dimensions(
            [data.coeffs_functional],
            [(data.config.num_decision_variables,)],
            ["coeffs_functional"]
        )
        assert_non_negative(
            data.config.id,
            "data.config.id"
        )
        assert_positive(
            data.config.num_decision_variables,
            "data.config.num_decision_variables"
        )
        assert_positive(
            data.config.num_aggregated_products,
            "data.config.num_aggregated_products"
        )
        assert_non_negative(
            data.config.num_soft_deadline_products,
            "data.config.num_soft_deadline_products"
        )
        assert_positive(
            data.config.num_constraints,
            "data.config.num_constraints"
        )

        # Validate non-negative coefficients
        for i, (coeff) in enumerate(data.coeffs_functional):
            assert_non_negative(coeff, f"coeffs_functional[{i}]")

        self.data = data
        self.y_e: List[Any] = list()
        self.z_e: List[Any] = list()
        self.t_0_e: List[Any] = list()
        self.order_e: List[int] = calculate_priority_order(data)

    def setup_variables(self) -> None:
        """Set up optimization variables for the element problem."""

        self.y_e = [
            self.solver.NumVar(0, self.solver.infinity(), f"y_{self.data.config.id}_{i}")
            for i in range(self.data.config.num_decision_variables)
        ]
        self.z_e = [
            self.solver.NumVar(0, self.solver.infinity(), f"z_{self.data.config.id}_{i}")
            for i in range(self.data.config.num_aggregated_products)
        ]
        self.t_0_e = [
            self.solver.NumVar(0, self.solver.infinity(), f"t_0_{self.data.config.id}_{i}")
            for i in range(self.data.config.num_aggregated_products)
        ]

    def setup_constraints(self) -> None:
        """Set up constraints for the element problem."""

        T_e = get_completion_times(self.data, self.y_e, self.t_0_e, self.order_e)

        # Resource constraints: MS_AGGREGATED_PLAN_COSTS[e] * y_e <= VS_RESOURCE_CONSTRAINTS[e]
        for i in range(self.data.config.num_constraints):
            self.solver.Add(
                lp_sum(self.data.aggregated_plan_costs[i][j] * self.y_e[j]
                       for j in range(self.data.config.num_decision_variables))
                <= self.data.resource_constraints[i]
            )

        if self.data.config.type == ElementType.SEQUENTIAL:
            # Times dependencies constraints: t_0_e_i >= t_0_e_{i-1} + sum_j={0..i-1}(VS_AGGREGATED_PLAN_TIMES[e][j] * y_e[j]), i=1..n1_e
            for i in range(self.data.config.num_aggregated_products):
                self.solver.Add(self.t_0_e[self.order_e[i]] >= T_e[i])

        # If n2_e == 0, skip the following constraints
        if self.data.config.num_soft_deadline_products != 0:
            # Soft deadline constraints: T_e_i - D_e_i <= z_e_i, i=1..n2_e
            for i in range(self.data.config.num_soft_deadline_products):
                self.solver.Add(T_e[i] - self.data.directive_terms[i] <= self.z_e[i])

        # If n2_e == n1_e, skip the following constraints
        if self.data.config.num_soft_deadline_products != self.data.config.num_aggregated_products:
            # Hard deadline constraints: -z_e_i <= T_e_i - D_e_i <= z_e_i, i=n2_e+1..n1_e
            for i in range(self.data.config.num_soft_deadline_products, self.data.config.num_aggregated_products):
                self.solver.Add(-self.z_e[i] <= T_e[i] - self.data.directive_terms[i])
                self.solver.Add(T_e[i] - self.data.directive_terms[i] <= self.z_e[i])

        # Minimum production constraints: y_e_i >= y_assigned_e_i, i=1..n1_e
        for i in range(self.data.config.num_aggregated_products):
            self.solver.Add(self.y_e[i] >= self.data.num_directive_products[i])

    def setup_objective(self) -> None:
        """
        Set up the objective function.

        max (C_e^T * y_e - sum_j={1..n1_e}(FINES_FOR_DEADLINE[e][j] * z_e_j))
        """

        objective = self.solver.Objective()

        for i, (coeff_func) in enumerate(self.data.coeffs_functional):
            objective.SetCoefficient(
                self.y_e[i],
                float(coeff_func)
            )

        for i, (deadline_fine) in enumerate(self.data.fines_for_deadline):
            objective.SetCoefficient(
                self.z_e[i],
                float(-deadline_fine)
            )

        objective.SetMaximization()

    def get_solution(self) -> Dict[str, Any]:
        """Extract solution values with formatting."""

        solution = {
            "y_e": [v.solution_value() for v in self.y_e],
            "z_e": [v.solution_value() for v in self.z_e],
            "t_0_e": [v.solution_value() for v in self.t_0_e],
        }
        return solution

    def print_results(self) -> None:
        """Print the results of the optimization for the element."""

        element_objective, dict_solved = self.solve()

        if element_objective == float("inf"):
            print("\nNo optimal solution found.")
            return

        tab_out(f"\nInput data for element {format_tensor(self.data.config.id)}", (
            ("Element Functional Coefficients", format_tensor(self.data.coeffs_functional)),
            ("Element Aggregated Plan Costs", format_tensor(self.data.aggregated_plan_costs)),
            ("Element Resource Constraints", format_tensor(self.data.resource_constraints)),
            ("Element Aggregated Plan Times", format_tensor(self.data.aggregated_plan_times)),
            ("Element Directive Terms", format_tensor(self.data.directive_terms)),
            ("Element Number of Directive Products", format_tensor(self.data.num_directive_products)),
            ("Element Fines for Deadline", format_tensor(self.data.fines_for_deadline)),
            ("Element Free Order", format_tensor(self.data.config.free_order)),
            ("Element Type", format_tensor(self.data.config.type)),
        ))

        tab_out(f"\nSolution for element {format_tensor(self.data.config.id)}", (
            ("y_e", format_tensor(dict_solved["y_e"])),
            ("z_e", format_tensor(dict_solved["z_e"])),
            ("t_0_e", format_tensor(dict_solved["t_0_e"])),
            ("order", format_tensor(self.order_e)),
        ))

        print(f"\nElement {format_tensor(self.data.config.id)} quality functionality: {format_tensor(element_objective)}")
