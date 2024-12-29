from typing import Dict, List, Any

from models.center import CenterData
from solvers.base import BaseSolver
from solvers.element.default import ElementSolver
from utils.assertions import assert_valid_dimensions, assert_non_negative, assert_positive
from utils.helpers import format_tensor, tab_out, copy_element_coeffs


# TODO: PRE-CALCULATE PRIORITY VECTOR: VS_AGGREGATED_PLAN_TIMES * VS_NUM_DIRECTIVE_PRODUCTS / VS_DIRECTIVE_TERMS
# TODO: SOLVE BY PRIORITY VALUES: THE HIGHER PRIORITY THAN TO SOLVE IN THE FIRST PLACE (JUST SORT T_I_L ( (№2 formula)) by this index)
# TODO: OR ADD ORDERING: T_
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
            assert_positive(
                element.config.num_soft_deadline_products,
                f"element.config.num_soft_deadline_products[{e}]"
            )
            assert_positive(
                element.config.num_constraints,
                f"element.config.num_constraints[{e}]"
            )

        self.data = data
        self.y_e: List[List[Any]] = list()
        self.z_e: List[List[Any]] = list()
        self.t_0_e: List[List[Any]] = list()
        self.f_e_1opt: List[float] = list()

        for e in range(self.data.config.num_elements):
            element_data = copy_element_coeffs(self.data.elements[e], self.data.coeffs_functional[e])
            element_solver = ElementSolver(element_data)
            element_solver.setup()
            f_e_1opt = element_solver.solve()[0]
            self.f_e_1opt.append(f_e_1opt)

    def setup_variables(self) -> None:
        """Set up optimization variables."""

        for e, (element) in enumerate(self.data.elements):
            self.y_e.append([
                self.solver.NumVar(0, self.solver.infinity(), f"y_{e}_{i}")
                for i in range(element.config.num_decision_variables)
            ])
            self.z_e.append([
                self.solver.NumVar(0, self.solver.infinity(), f"z_{e}_{i}")
                for i in range(element.config.num_aggregated_products)
            ])
            self.t_0_e.append([
                self.solver.NumVar(0, self.solver.infinity(), f"t_0_{e}_{i}")
                for i in range(element.config.num_aggregated_products)
            ])

    def setup_constraints(self) -> None:
        """Set up optimization constraints."""

        for e, (element) in enumerate(self.data.elements):
            # Resource constraints: MS_AGGREGATED_PLAN_COSTS[e] * y_e <= VS_RESOURCE_CONSTRAINTS[e]
            for i in range(element.config.num_constraints):
                self.solver.Add(
                    sum(element.aggregated_plan_costs[i][j] * self.y_e[e][j]
                        for j in range(element.config.num_decision_variables))
                    <= element.resource_constraints[i]
                )

            # Soft deadline constraints: T_i - z_i <= D_i, i=1..n2
            for i in range(element.config.num_soft_deadline_products):
                T_i = self.t_0_e[e][i] + element.aggregated_plan_times[i] * self.y_e[e][i]
                self.solver.Add(T_i - self.z_e[e][i] <= element.directive_terms[i])
                if i != 0:
                    self.solver.Add(
                        self.t_0_e[e][i] >= self.t_0_e[e][i - 1] +
                        sum(element.aggregated_plan_times[j] * self.y_e[e][j]
                            for j in range(i))
                    )

            # Hard deadline constraints: -z_i <= D_i - T_i <= z_i, i=n2+1..n1
            for i in range(element.config.num_soft_deadline_products, element.config.num_aggregated_products):
                T_i = self.t_0_e[e][i] + element.aggregated_plan_times[i] * self.y_e[e][i]
                self.solver.Add(-self.z_e[e][i] <= element.directive_terms[i] - T_i)
                self.solver.Add(element.directive_terms[i] - T_i <= self.z_e[e][i])

            # Minimum production constraints: y_e_i >= y_assigned_e_i, i=1..n1
            for i in range(element.config.num_aggregated_products):
                self.solver.Add(self.y_e[e][i] >= element.num_directive_products[i])

            # Optimality Equality Constraint: VS_COEFFS_CENTER_FUNCTIONAL[e]^T * y_e - sum_j={1..n1}(FINES_FOR_DEADLINE[e][j] * z_j) = f_e_1opt
            self.solver.Add(
                sum(self.data.coeffs_functional[e][i] * self.y_e[e][i]
                    for i in range(element.config.num_decision_variables))
                - sum(element.fines_for_deadline[j] * self.z_e[e][j]
                      for j in range(element.config.num_aggregated_products))
                == self.f_e_1opt[e]
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

        if self.solution is None:
            self.solution = {
                "y_e": [[v.solution_value() for v in element] for element in self.y_e],
                "z_e": [[v.solution_value() for v in element] for element in self.z_e],
                "t_0_e": [[v.solution_value() for v in element] for element in self.t_0_e],
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
        )

        tab_out(f"\nCenter data (first criteria)", center_data)

        objective, dict_solved = self.solve()

        if objective == float("inf"):
            print("\nNo optimal solution found.")
            return

        center_objective = 0
        for e, (element) in enumerate(self.data.elements):
            input_data = (
                ("Functional Coefficients", format_tensor(element.coeffs_functional)),
                ("Aggregated Plan Costs", format_tensor(element.aggregated_plan_costs)),
                ("Resource Constraints", format_tensor(element.resource_constraints)),
                ("Aggregated Plan Times", format_tensor(element.aggregated_plan_times)),
                ("Directive Terms", format_tensor(element.directive_terms)),
                ("Number of Directive Products", format_tensor(element.num_directive_products)),
                ("Fines for Deadline", format_tensor(element.fines_for_deadline)),
            )

            tab_out(f"\nInput data for element {element.config.id}", input_data)

            y_e_solved, z_e_solved, t_0_e_solved = dict_solved["y_e"][e], dict_solved["z_e"][e], dict_solved["t_0_e"][e]

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

        print(f"\nCenter (first criteria) quality functionality: {center_objective}")
