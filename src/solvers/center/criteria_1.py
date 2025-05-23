from typing import Dict, List, Any

from models.center import CenterData
from models.element import ElementType
from solvers.base import BaseSolver
from solvers.element.default import ElementSolver
from utils.assertions import assert_valid_dimensions, assert_non_negative, assert_positive
from utils.helpers import (stringify, tab_out, copy_element_coeffs, calculate_priority_order, get_completion_times,
                           lp_sum)


class CenterCriteria1Solver(BaseSolver):
    """Implementation of the first optimization criteria for the center."""

    def __init__(self, data: CenterData):
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
            assert_non_negative(
                element.config.num_soft_deadline_products,
                f"element.config.num_soft_deadline_products[{e}]"
            )
            assert_positive(
                element.config.num_constraints,
                f"element.config.num_constraints[{e}]"
            )

        self.data = data
        self.y: List[List[Any]] = list()
        self.z: List[List[Any]] = list()
        self.t_0: List[List[Any]] = list()
        self.f_1opt: List[float] = list()
        self.order: List[List[int]] = [calculate_priority_order(element) for element in data.elements]

        for e in range(data.config.num_elements):
            element_data = copy_element_coeffs(data.elements[e], data.coeffs_functional[e])
            element_solver = ElementSolver(element_data)
            element_solver.setup()
            f_e_1opt = element_solver.solve()[0]
            self.f_1opt.append(f_e_1opt)

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
            T_e = get_completion_times(element, self.y[e], self.t_0[e], self.order[e])

            # Resource constraints: MS_AGGREGATED_PLAN_COSTS[e] * y_e <= VS_RESOURCE_CONSTRAINTS[e]
            for i in range(element.config.num_constraints):
                self.solver.Add(
                    lp_sum(element.aggregated_plan_costs[i][j] * self.y[e][j]
                           for j in range(element.config.num_decision_variables))
                    <= element.resource_constraints[i]
                )

            if element.config.type == ElementType.SEQUENTIAL:
                # Times dependencies constraints: t_0_e_i >= t_0_e_{i-1} + sum_j={0..i-1}(VS_AGGREGATED_PLAN_TIMES[e][j] * y_e[j]), i=1..n1_e
                for i in range(element.config.num_aggregated_products):
                    self.solver.Add(self.t_0[e][self.order[e][i]] >= T_e[i])

            # If n2_e == 0, skip the following constraints
            if element.config.num_soft_deadline_products != 0:
                # Soft deadline constraints: T_e_i - D_e_i <= z_e_i, i=1..n2_e
                for i in range(element.config.num_soft_deadline_products):
                    self.solver.Add(T_e[i] - element.directive_terms[i] <= self.z[e][i])

            # If n2_e == n1_e, skip the following constraints
            if element.config.num_soft_deadline_products != element.config.num_aggregated_products:
                # Hard deadline constraints: -z_e_i <= T_e_i - D_e_i <= z_e_i, i=n2_e+1..n1_e
                for i in range(element.config.num_soft_deadline_products, element.config.num_aggregated_products):
                    self.solver.Add(-self.z[e][i] <= T_e[i] - element.directive_terms[i])
                    self.solver.Add(T_e[i] - element.directive_terms[i] <= self.z[e][i])

            # Minimum production constraints: y_e_i >= y_assigned_e_i, i=1..n1_e
            for i in range(element.config.num_aggregated_products):
                self.solver.Add(self.y[e][i] >= element.num_directive_products[i])

            # Optimality Equality Constraint: VS_COEFFS_CENTER_FUNCTIONAL[e]^T * y_e - sum_j={1..n1_e}(FINES_FOR_DEADLINE[e][j] * z_e_j) = f_1opt_e
            self.solver.Add(
                lp_sum(self.data.coeffs_functional[e][i] * self.y[e][i]
                       for i in range(element.config.num_decision_variables))
                - lp_sum(element.fines_for_deadline[j] * self.z[e][j]
                         for j in range(element.config.num_aggregated_products))
                == self.f_1opt[e]
            )

    def setup_objective(self) -> None:
        """
        Set up the objective function.

        max sum_e(C_e^T * y_e - sum_j={1..n1_e}(FINES_FOR_DEADLINE[e][j] * z_e_j))
        """

        objective = self.solver.Objective()

        for e, (element) in enumerate(self.data.elements):
            for c, (coeff_func) in enumerate(element.coeffs_functional):
                objective.SetCoefficient(
                    self.y[e][c],
                    float(coeff_func)
                )

            for f, (deadline_fine) in enumerate(element.fines_for_deadline):
                objective.SetCoefficient(
                    self.z[e][f],
                    float(-deadline_fine)
                )

        objective.SetMaximization()

    def get_solution(self) -> Dict[str, Any]:
        """Extract and format solution values."""

        if self.solution is None:
            self.solution = {
                "y": [[v.solution_value() for v in element] for element in self.y],
                "z": [[v.solution_value() for v in element] for element in self.z],
                "t_0": [[v.solution_value() for v in element] for element in self.t_0],
            }
        return self.solution

    def print_results(self) -> None:
        """Print the results of the optimization for the center (first criteria)."""

        tab_out(f"\nCenter data (first criteria)", (
            ("Number of Elements", stringify(self.data.config.num_elements)),
            ("Number of Constraints", stringify([element.config.num_constraints for element in self.data.elements])),
            ("Number of Decision Variables",
             stringify([element.config.num_decision_variables for element in self.data.elements])),
            ("Number of Aggregated Products",
             stringify([element.config.num_aggregated_products for element in self.data.elements])),
            ("Number of Soft Deadline Products",
             stringify([element.config.num_soft_deadline_products for element in self.data.elements])),
        ))

        center_objective, dict_solved = self.solve()

        if center_objective == float("inf"):
            print("\nNo optimal solution found.")
            return

        center_functionality = 0
        for e, (element) in enumerate(self.data.elements):
            tab_out(f"\nInput data for element {stringify(element.config.id)}", (
                ("Element Functional Coefficients", stringify(element.coeffs_functional)),
                ("Center Functional Coefficients for element", stringify(self.data.coeffs_functional[e])),
                ("Element Aggregated Plan Costs", stringify(element.aggregated_plan_costs)),
                ("Element Resource Constraints", stringify(element.resource_constraints)),
                ("Element Aggregated Plan Times", stringify(element.aggregated_plan_times)),
                ("Element Directive Terms", stringify(element.directive_terms)),
                ("Element Number of Directive Products", stringify(element.num_directive_products)),
                ("Element Fines for Deadline", stringify(element.fines_for_deadline)),
                ("Element Free Order", stringify(element.config.free_order)),
                ("Element Type", stringify(element.config.type)),
            ))

            tab_out(f"\nSolution for element {stringify(element.config.id)}", (
                ("y_e", stringify(dict_solved["y"][e])),
                ("z_e", stringify(dict_solved["z"][e])),
                ("t_0_e", stringify(dict_solved["t_0"][e])),
                ("order", stringify(self.order[e])),
            ))

            # max (C_e^T * y_e - sum_j={1..n1_e}(FINES_FOR_DEADLINE[e][j] * z_e_j))
            element_functionality = (sum(element.coeffs_functional[i] * dict_solved["y"][e][i]
                                         for i in range(element.config.num_decision_variables))
                                     - sum(element.fines_for_deadline[j] * dict_solved["z"][e][j]
                                           for j in range(element.config.num_aggregated_products)))

            print(f"\nElement {stringify(element.config.id)} quality functionality: {stringify(element_functionality)}")

            # max (VS_COEFFS_CENTER_FUNCTIONAL[e]^T * y_e - sum_j={1..n1_e}(FINES_FOR_DEADLINE[e][j] * z_e_j))
            center_functionality += (sum(self.data.coeffs_functional[e][i] * dict_solved["y"][e][i]
                                         for i in range(element.config.num_decision_variables))
                                     - sum(element.fines_for_deadline[j] * dict_solved["z"][e][j]
                                           for j in range(element.config.num_aggregated_products)))

        print(f"\nCenter (first criteria) quality functionality: {stringify(center_functionality)}")
