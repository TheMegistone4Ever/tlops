from typing import List, Any, Dict

import numpy as np

from models.element import ElementData
from solvers.base import BaseSolver
from utils.assertions import assert_valid_dimensions, assert_non_negative


class ElementSolver(BaseSolver):
    """Solver for element-level optimization problems."""

    def __init__(self, element_id: int, coeffs_functional: np.ndarray, data: ElementData):
        super().__init__()
        # Validate input dimensions
        assert_valid_dimensions(
            [coeffs_functional],
            [(len(data.aggregated_plan_costs[0]),)],
            ["coeffs_functional"]
        )

        # Validate non-negative coefficients
        for i, coeff in enumerate(coeffs_functional):
            assert_non_negative(coeff, f"coeffs_functional[{i}]")

        self.element_id = element_id
        self.coeffs_functional = coeffs_functional
        self.data = data
        self.y_e: List[Any] = []
        self.z_e: List[Any] = []
        self.t_0_e: List[Any] = []

    def setup_variables(self) -> None:
        """Set up optimization variables for the element problem."""
        self.y_e = [
            self.solver.NumVar(0, self.solver.infinity(), f"y_{self.element_id}_{i}")
            for i in range(len(self.coeffs_functional))
        ]
        self.z_e = [
            self.solver.NumVar(0, self.solver.infinity(), f"z_{self.element_id}_{i}")
            for i in range(len(self.data.aggregated_plan_times))
        ]
        self.t_0_e = [
            self.solver.NumVar(0, self.solver.infinity(), f"t_0_{self.element_id}_{i}")
            for i in range(len(self.data.aggregated_plan_times))
        ]

    def setup_constraints(self) -> None:
        """Set up constraints for the element problem."""
        # Resource constraints
        for i in range(len(self.data.resource_constraints)):
            self.solver.Add(
                sum(self.data.aggregated_plan_costs[i][j] * self.y_e[j]
                    for j in range(len(self.coeffs_functional)))
                <= self.data.resource_constraints[i]
            )

        # Soft deadline constraints
        for i in range(len(self.data.aggregated_plan_times)):
            T_i = self.t_0_e[i] + self.data.aggregated_plan_times[i] * self.y_e[i]
            self.solver.Add(T_i - self.z_e[i] <= self.data.directive_terms[i])
            if i != 0:
                self.solver.Add(
                    self.t_0_e[i] >= self.t_0_e[i - 1] +
                    sum(self.data.aggregated_plan_times[j] * self.y_e[j]
                        for j in range(i))
                )

        # Minimum production constraints
        for i in range(len(self.data.num_directive_products)):
            self.solver.Add(self.y_e[i] >= self.data.num_directive_products[i])

    def setup_objective(self) -> None:
        """
        Set up the objective function.

        max (C^e^T * y^e - sum_j={1..n1}(FINES_FOR_DEADLINE[e][j] * z_j))
        """

        objective = self.solver.Objective()

        for i in range(len(self.coeffs_functional)):
            objective.SetCoefficient(self.y_e[i], float(self.coeffs_functional[i]))

        for i in range(len(self.data.fines_for_deadline)):
            objective.SetCoefficient(self.z_e[i], float(-self.data.fines_for_deadline[i]))

        objective.SetMaximization()

    def get_solution(self) -> Dict[str, Any]:
        """Extract solution values with formatting."""
        solution = {
            'y_e': [v.solution_value() for v in self.y_e],
            'z_e': [v.solution_value() for v in self.z_e],
            't_0_e': [v.solution_value() for v in self.t_0_e]
        }
        return solution
