from typing import Dict
from typing import List, Any

from models.center import CenterData
from solvers.base import BaseSolver
from solvers.element.default import ElementSolver


class CenterCriteria2Solver(BaseSolver):
    """Implementation of the second optimization criteria for the center."""

    def __init__(self, data: CenterData, delta: float):
        super().__init__()
        self.data = data
        self.delta = delta
        self.y_e: List[List[Any]] = []
        self.z_e: List[List[Any]] = []
        self.t_0_e: List[List[Any]] = []

    def setup_variables(self) -> None:
        """Set up optimization variables."""
        for e in range(len(self.data.elements)):
            self.y_e.append([
                self.solver.NumVar(0, self.solver.infinity(), f"y_{e}_{i}")
                for i in range(len(self.data.coeffs_functional[e]))
            ])
            self.z_e.append([
                self.solver.NumVar(0, self.solver.infinity(), f"z_{e}_{i}")
                for i in range(len(self.data.elements[e].aggregated_plan_times))
            ])
            self.t_0_e.append([
                self.solver.NumVar(0, self.solver.infinity(), f"t_0_{e}_{i}")
                for i in range(len(self.data.elements[e].aggregated_plan_times))
            ])

    def setup_constraints(self) -> None:
        """Set up optimization constraints."""
        for e in range(len(self.data.elements)):
            element = self.data.elements[e]

            # Resource constraints
            for i in range(len(element.resource_constraints)):
                self.solver.Add(
                    sum(element.aggregated_plan_costs[i][j] * self.y_e[e][j]
                        for j in range(len(self.data.coeffs_functional[e])))
                    <= element.resource_constraints[i]
                )

            # Time and deadline constraints
            for i in range(len(element.aggregated_plan_times)):
                T_i = self.t_0_e[e][i] + element.aggregated_plan_times[i] * self.y_e[e][i]
                self.solver.Add(T_i - self.z_e[e][i] <= element.directive_terms[i])

                if i != 0:
                    self.solver.Add(
                        self.t_0_e[e][i] >= self.t_0_e[e][i - 1] +
                        sum(element.aggregated_plan_times[j] * self.y_e[e][j]
                            for j in range(i))
                    )

            # Production constraints
            for i in range(len(element.num_directive_products)):
                self.solver.Add(self.y_e[e][i] >= element.num_directive_products[i])

            # Delta constraint
            element_solver = ElementSolver(e, self.data.coeffs_functional[e], element)
            element_solver.setup_variables()
            element_solver.setup_constraints()
            element_solver.setup_objective()
            optimal_value = element_solver.solve()[0]

            self.solver.Add(
                sum(self.data.coeffs_functional[e][i] * self.y_e[e][i]
                    for i in range(len(self.data.coeffs_functional[e]))) -
                sum(element.fines_for_deadline[i] * self.z_e[e][i]
                    for i in range(len(element.fines_for_deadline)))
                >= optimal_value - self.delta
            )

    def setup_objective(self) -> None:
        """Set up the objective function."""
        objective = self.solver.Objective()

        for e in range(len(self.data.elements)):
            for i in range(len(self.data.coeffs_functional[e])):
                objective.SetCoefficient(
                    self.y_e[e][i],
                    float(self.data.elements[e].coeffs_functional[i])
                )

            for i in range(len(self.data.elements[e].fines_for_deadline)):
                objective.SetCoefficient(
                    self.z_e[e][i],
                    float(-self.data.elements[e].fines_for_deadline[i])
                )

        objective.SetMaximization()

    def get_solution(self) -> Dict[str, Any]:
        """Extract and format solution values."""
        solution = {
            'y_e': [[v.solution_value() for v in element] for element in self.y_e],
            'z_e': [[v.solution_value() for v in element] for element in self.z_e],
            't_0_e': [[v.solution_value() for v in element] for element in self.t_0_e]
        }
        return solution
