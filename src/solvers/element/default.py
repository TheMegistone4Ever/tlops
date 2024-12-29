from typing import List, Any, Dict

from models.element import ElementData
from solvers.base import BaseSolver
from utils.assertions import assert_valid_dimensions, assert_non_negative
from utils.helpers import format_tensor, tab_out


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

        # Validate non-negative coefficients
        for i, (coeff) in enumerate(data.coeffs_functional):
            assert_non_negative(coeff, f"coeffs_functional[{i}]")

        self.data = data
        self.y_e: List[Any] = list()
        self.z_e: List[Any] = list()
        self.t_0_e: List[Any] = list()

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

        # Resource constraints: MS_AGGREGATED_PLAN_COSTS[e] * y_e <= VS_RESOURCE_CONSTRAINTS[e]
        for i in range(self.data.config.num_constraints):
            self.solver.Add(
                sum(self.data.aggregated_plan_costs[i][j] * self.y_e[j]
                    for j in range(self.data.config.num_decision_variables))
                <= self.data.resource_constraints[i]
            )

        # Soft deadline constraints: T_i - z_i <= D_i, i=1..n2
        for i in range(self.data.config.num_soft_deadline_products):
            T_i = self.t_0_e[i] + self.data.aggregated_plan_times[i] * self.y_e[i]
            self.solver.Add(T_i - self.z_e[i] <= self.data.directive_terms[i])
            if i != 0:
                self.solver.Add(
                    self.t_0_e[i] >= self.t_0_e[i - 1] +
                    sum(self.data.aggregated_plan_times[j] * self.y_e[j]
                        for j in range(i))
                )

        # Hard deadline constraints: -z_i <= D_i - T_i <= z_i, i=n2+1..n1
        for i in range(self.data.config.num_soft_deadline_products, self.data.config.num_aggregated_products):
            T_i = self.t_0_e[i] + self.data.aggregated_plan_times[i] * self.y_e[i]
            self.solver.Add(-self.z_e[i] <= self.data.directive_terms[i] - T_i)
            self.solver.Add(self.data.directive_terms[i] - T_i <= self.z_e[i])

        # Minimum production constraints: y_e_i >= y_assigned_e_i, i=1..n1
        for i in range(self.data.config.num_aggregated_products):
            self.solver.Add(self.y_e[i] >= self.data.num_directive_products[i])

    def setup_objective(self) -> None:
        """
        Set up the objective function.

        max (C^e^T * y^e - sum_j={1..n1}(FINES_FOR_DEADLINE[e][j] * z_j))
        """

        objective = self.solver.Objective()

        for i, (coeff_func) in enumerate(self.data.coeffs_functional):
            objective.SetCoefficient(self.y_e[i], float(coeff_func))

        for i, (deadline_fine) in enumerate(self.data.fines_for_deadline):
            objective.SetCoefficient(self.z_e[i], float(-deadline_fine))

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

        objective, dict_solved = self.solve()

        if objective == float("inf"):
            print("\nNo optimal solution found.")
            return

        input_data = (
            ("Element Functional Coefficients", format_tensor(self.data.coeffs_functional)),
            ("Element Aggregated Plan Costs", format_tensor(self.data.aggregated_plan_costs)),
            ("Element Resource Constraints", format_tensor(self.data.resource_constraints)),
            ("Element Aggregated Plan Times", format_tensor(self.data.aggregated_plan_times)),
            ("Element Directive Terms", format_tensor(self.data.directive_terms)),
            ("Element Number of Directive Products", format_tensor(self.data.num_directive_products)),
            ("Element Fines for Deadline", format_tensor(self.data.fines_for_deadline)),
        )

        tab_out(f"\nInput data for element {self.data.config.id}", input_data)

        y_e_solved, z_e_solved, t_0_e_solved = dict_solved["y_e"], dict_solved["z_e"], dict_solved["t_0_e"]

        solution_data = (
            ("y_e", format_tensor(y_e_solved)),
            ("z_e", format_tensor(z_e_solved)),
            ("t_0_e", format_tensor(t_0_e_solved)),
        )

        tab_out(f"\nSolution for element {self.data.config.id}", solution_data)

        print(f"\nElement {self.data.config.id} quality functionality: {format_tensor(objective)}")
