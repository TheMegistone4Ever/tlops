from typing import Dict, List, Any

from models.center import CenterData
from solvers.base import BaseSolver
from solvers.element.default import ElementSolver
from utils.assertions import assert_valid_dimensions, assert_non_negative, assert_positive
from utils.helpers import format_tensor, tab_out, copy_element_coeffs


class CenterCriteria2Solver(BaseSolver):
    """Implementation of the second optimization criteria for the center."""

    def __init__(self, data: CenterData, delta: float):
        super().__init__()
        for e, (element) in enumerate(data.elements):
            assert_valid_dimensions(
                [data.coeffs_functional[e]],
                [(data.elements[e].config.num_decision_variables,)],
                [f"coeffs_functional[{e}]"]
            )
            assert_non_negative(
                element.config.id,
                f"element.config.id[{e}]"
            )
            assert_positive(
                element.config.num_decision_variables,
                f"element.config.num_decision_variables[{e}]"
            )
            assert_positive(
                element.config.num_aggregated_products,
                f"element.config.num_aggregated_products[{e}]"
            )
            assert_positive(
                element.config.num_soft_deadline_products,
                f"element.config.num_soft_deadline_products[{e}]"
            )
            assert_positive(
                element.config.num_constraints,
                f"element.config.num_constraints[{e}]"
            )

        self.data = data
        self.delta = delta
        self.y: List[List[Any]] = list()
        self.z: List[List[Any]] = list()
        self.t_0: List[List[Any]] = list()
        self.f_2opt: List[float] = list()

        for e in range(self.data.config.num_elements):
            element_data = copy_element_coeffs(self.data.elements[e], self.data.coeffs_functional[e])
            element_solver = ElementSolver(element_data)
            element_solver.setup()
            f_e_2opt = element_solver.solve()[0]
            self.f_2opt.append(f_e_2opt)

    def setup_variables(self) -> None:
        """Set up optimization variables."""

        for e, (element) in enumerate(self.data.elements):
            self.y.append([
                self.solver.NumVar(0, self.solver.infinity(), f"y_{e}_{i}")
                for i in range(element.config.num_decision_variables)
            ])
            self.z.append([
                self.solver.NumVar(0, self.solver.infinity(), f"z_{e}_{i}")
                for i in range(element.config.num_aggregated_products)
            ])
            self.t_0.append([
                self.solver.NumVar(0, self.solver.infinity(), f"t_0_{e}_{i}")
                for i in range(element.config.num_aggregated_products)
            ])

    def setup_constraints(self) -> None:
        """Set up optimization constraints."""

        for e, (element) in enumerate(self.data.elements):
            # Resource constraints: MS_AGGREGATED_PLAN_COSTS[e] * y_e <= VS_RESOURCE_CONSTRAINTS[e]
            for i in range(element.config.num_constraints):
                self.solver.Add(
                    sum(element.aggregated_plan_costs[i][j] * self.y[e][j]
                        for j in range(element.config.num_decision_variables))
                    <= element.resource_constraints[i]
                )

            # Soft deadline constraints: T_e_i - z_e_i <= D_e_i, i=1..n2_e
            for i in range(element.config.num_soft_deadline_products):
                T_i = self.t_0[e][i] + element.aggregated_plan_times[i] * self.y[e][i]
                self.solver.Add(T_i - self.z[e][i] <= element.directive_terms[i])
                if i != 0:
                    self.solver.Add(
                        self.t_0[e][i] >= self.t_0[e][i - 1] +
                        sum(element.aggregated_plan_times[j] * self.y[e][j]
                            for j in range(i))
                    )

            # Hard deadline constraints: -z_e_i <= D_e_i - T_e_i <= z_e_i, i=n2_e+1..n1_e
            for i in range(element.config.num_soft_deadline_products, element.config.num_aggregated_products):
                T_i = self.t_0[e][i] + element.aggregated_plan_times[i] * self.y[e][i]
                self.solver.Add(-self.z[e][i] <= element.directive_terms[i] - T_i)
                self.solver.Add(element.directive_terms[i] - T_i <= self.z[e][i])

            # Minimum production constraints: y_e_i >= y_assigned_e_i, i=1..n1_e
            for i in range(element.config.num_aggregated_products):
                self.solver.Add(self.y[e][i] >= element.num_directive_products[i])

            # Suboptimality Bound Constraint: VS_COEFFS_CENTER_FUNCTIONAL[e]^T * y_e - sum_j={1..n1_e}(FINES_FOR_DEADLINE[e][j] * z_e_j) >= f_2opt_e - DELTA
            self.solver.Add(
                sum(self.data.coeffs_functional[e][i] * self.y[e][i]
                    for i in range(element.config.num_decision_variables))
                - sum(element.fines_for_deadline[j] * self.z[e][j]
                      for j in range(element.config.num_aggregated_products))
                >= self.f_2opt[e] - self.delta
            )

    def setup_objective(self) -> None:
        """
        Set up the objective function.

        max (C_e^T * y_e - sum_j={1..n1_e}(FINES_FOR_DEADLINE[e][j] * z_e_j))
        """

        objective = self.solver.Objective()

        for e, (element) in enumerate(self.data.elements):
            for c, (coeff) in enumerate(element.coeffs_functional):
                objective.SetCoefficient(
                    self.y[e][c],
                    float(coeff)
                )

            for f, (fine) in enumerate(element.fines_for_deadline):
                objective.SetCoefficient(
                    self.z[e][f],
                    float(-fine)
                )

        objective.SetMaximization()

    def get_solution(self) -> Dict[str, Any]:
        """Extract and format solution values."""

        if self.solution is None:
            self.solution = {
                "y": [[v.solution_value() for v in element] for element in self.y],
                "z": [[v.solution_value() for v in element] for element in self.z],
                "t_0": [[v.solution_value() for v in element] for element in self.t_0]
            }
        return self.solution

    def print_results(self) -> None:
        """Print the results of the optimization for the center (first criteria)."""

        center_data = (
            ("Number of Elements", format_tensor(self.data.config.num_elements)),
            ("Number of Constraints",
             format_tensor([element.config.num_constraints for element in self.data.elements])),
            ("Number of Decision Variables",
             format_tensor([element.config.num_decision_variables for element in self.data.elements])),
            ("Number of Aggregated Products",
             format_tensor([element.config.num_aggregated_products for element in self.data.elements])),
            ("Number of Soft Deadline Products",
             format_tensor([element.config.num_soft_deadline_products for element in self.data.elements])),
            ("Free Order", format_tensor(self.data.config.free_order)),
            ("Delta", format_tensor(self.delta)),
        )

        tab_out(f"\nCenter data (second criteria)", center_data)

        objective, dict_solved = self.solve()

        if objective == float("inf"):
            print("\nNo optimal solution found.")
            return

        center_objective = 0
        for e, (element) in enumerate(self.data.elements):
            input_data = (
                ("Element Functional Coefficients", format_tensor(element.coeffs_functional)),
                ("Center Functional Coefficients for element", format_tensor(self.data.coeffs_functional[e])),
                ("Element Aggregated Plan Costs", format_tensor(element.aggregated_plan_costs)),
                ("Element Resource Constraints", format_tensor(element.resource_constraints)),
                ("Element Aggregated Plan Times", format_tensor(element.aggregated_plan_times)),
                ("Element Directive Terms", format_tensor(element.directive_terms)),
                ("Element Number of Directive Products", format_tensor(element.num_directive_products)),
                ("Element Fines for Deadline", format_tensor(element.fines_for_deadline)),
            )

            tab_out(f"\nInput data for element {element.config.id}", input_data)

            y_e_solved, z_e_solved, t_0_e_solved = dict_solved["y"][e], dict_solved["z"][e], dict_solved["t_0"][e]

            solution_data = (
                ("y_e", format_tensor(y_e_solved)),
                ("z_e", format_tensor(z_e_solved)),
                ("t_0_e", format_tensor(t_0_e_solved)),
            )

            tab_out(f"\nSolution for element {element.config.id}", solution_data)

            print(f"\nElement {element.config.id} quality functionality: {format_tensor(objective)}")

            center_objective += (sum(self.data.coeffs_functional[e][i] * y_e_solved[i]
                                     for i in range(element.config.num_decision_variables))
                                 - sum(element.fines_for_deadline[j] * z_e_solved[j]
                                       for j in range(element.config.num_aggregated_products)))

        print(f"\nCenter (second criteria) quality functionality: {format_tensor(center_objective)}")
