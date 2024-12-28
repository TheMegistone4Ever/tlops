from typing import Dict
from typing import List, Any

from models.center import CenterData
from models.element import ElementData
from solvers.base import BaseSolver
from solvers.element.default import ElementSolver
from utils.assertions import assert_valid_dimensions, assert_non_negative, assert_positive
from utils.formatters import format_tensor, tab_out


class CenterCriteria2Solver(BaseSolver):
    """Implementation of the second optimization criteria for the center."""

    def __init__(self, data: CenterData, delta: float):
        super().__init__()
        for e, (element) in enumerate(data.elements):
            assert_valid_dimensions(
                [data.coeffs_functional[e]],
                [(len(element.aggregated_plan_costs[0]),)],
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
            delta_element_data = ElementData(
                element.config,
                self.data.coeffs_functional[e],
                element.resource_constraints,
                element.aggregated_plan_costs,
                element.aggregated_plan_times,
                element.directive_terms,
                element.num_directive_products,
                element.fines_for_deadline
            )
            element_solver = ElementSolver(delta_element_data)
            element_solver.setup()
            optimal_value = element_solver.solve()[0]

            self.solver.Add(
                sum(self.data.coeffs_functional[e][i] * self.y_e[e][i]
                    for i in range(len(self.data.coeffs_functional[e]))) -
                sum(element.fines_for_deadline[i] * self.z_e[e][i]
                    for i in range(len(element.fines_for_deadline)))
                >= optimal_value - self.delta
            )

    def setup_objective(self) -> None:
        """
        Set up the objective function.

        max (C^e^T * y^e - sum_j={1..n1}(FINES_FOR_DEADLINE[e][j] * z_j))
        """

        objective = self.solver.Objective()

        for e, (element) in enumerate(self.data.elements):
            for c, (coeff) in enumerate(element.coeffs_functional):
                objective.SetCoefficient(
                    self.y_e[e][c],
                    float(coeff)
                )

            for f, (fine) in enumerate(element.fines_for_deadline):
                objective.SetCoefficient(
                    self.z_e[e][f],
                    float(-fine)
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

        tab_out(f"\nCenter data (second criteria):", center_data)

        objective, dict_solved = self.solve()

        if objective == float("inf"):
            print("\nNo optimal solution found.")
            return

        center_objective = 0
        for e in range(len(self.data.elements)):
            input_data = (
                ("Functional Coefficients", format_tensor(self.data.elements[e].coeffs_functional)),
                ("Aggregated Plan Costs", format_tensor(self.data.elements[e].aggregated_plan_costs)),
                ("Resource Constraints", format_tensor(self.data.elements[e].resource_constraints)),
                ("Aggregated Plan Times", format_tensor(self.data.elements[e].aggregated_plan_times)),
                ("Directive Terms", format_tensor(self.data.elements[e].directive_terms)),
                ("Number of Directive Products", format_tensor(self.data.elements[e].num_directive_products)),
                ("Fines for Deadline", format_tensor(self.data.elements[e].fines_for_deadline)),
            )

            tab_out(f"\nInput data for element {self.data.elements[e].config.id}:", input_data)

            y_e_solved, z_e_solved, t_0_e_solved = dict_solved['y_e'][e], dict_solved['z_e'][e], dict_solved['t_0_e'][e]

            solution_data = (
                ("y_e", format_tensor(y_e_solved)),
                ("z_e", format_tensor(z_e_solved)),
                ("t_0_e", format_tensor(t_0_e_solved)),
            )

            tab_out(f"\nSolution for element {self.data.elements[e].config.id}:", solution_data)

            print(f"\nElement {self.data.elements[e].config.id} quality functionality: {format_tensor(objective)}")

            center_objective += sum(self.data.coeffs_functional[e][i] * y_e_solved[i] for i in
                                    range(len(self.data.coeffs_functional[e]))) - sum(
                self.data.elements[e].fines_for_deadline[j] * z_e_solved[j] for j in
                range(len(self.data.elements[e].aggregated_plan_times)))

        print(f"\nCenter (second criteria) quality functionality: {center_objective}")
