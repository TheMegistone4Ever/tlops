from ortools.linear_solver import pywraplp
from tabulate import tabulate

from constants import *
from data import *
from solver_element import element_model
from utils import format_tensor


def center_model():
    # """
    # 1'st criteria for the center
    # """
    #
    # for e in range(NUM_ELEMENTS):
    #     f_e_1opt = element_model(e, VS_COEFFS_CENTER_FUNCTIONAL[e])[0]
    #
    #     lp_solver = pywraplp.Solver.CreateSolver("GLOP")
    #
    #     # Define Variables
    #     y_e = [lp_solver.NumVar(0, lp_solver.infinity(), f"y_{e}_{i}") for i in range(NUM_DECISION_VARIABLES[e])]
    #     z_e = [lp_solver.NumVar(0, lp_solver.infinity(), f"z_{e}_{i}") for i in range(NUM_AGGREGATED_PRODUCTS[e])]
    #     t_0_e = [lp_solver.NumVar(0, lp_solver.infinity(), f"t_0_{e}_{i}") for i in range(NUM_AGGREGATED_PRODUCTS[e])]
    #
    #     ## Defining Constraints
    #
    #     # MS_AGGREGATED_PLAN_COSTS[e] * y_e <= VS_RESOURCE_CONSTRAINTS[e]
    #     for i in range(NUM_CONSTRAINTS[e]):
    #         lp_solver.Add(sum(MS_AGGREGATED_PLAN_COSTS[e][i][j] * y_e[j] for j in range(NUM_DECISION_VARIABLES[e])) <=
    #                       VS_RESOURCE_CONSTRAINTS[e][i])
    #
    #     # T_i - z_i <= D_i, i=1..n2
    #     for i in range(NUM_SOFT_DEADLINE_PRODUCTS[e]):
    #         T_i = t_0_e[i] + VS_AGGREGATED_PLAN_TIMES[e][i] * y_e[i]
    #         lp_solver.Add(T_i - z_e[i] <= VS_DIRECTIVE_TERMS[e][i])
    #         if i != 0:
    #             lp_solver.Add(t_0_e[i] >= t_0_e[i - 1] + sum(VS_AGGREGATED_PLAN_TIMES[e][j] * y_e[j] for j in range(i)))
    #
    #     # -z_i <= D_i - T_i <= z_i, i=n2+1..n1
    #     for i in range(NUM_SOFT_DEADLINE_PRODUCTS[e], NUM_AGGREGATED_PRODUCTS[e]):
    #         T_i = t_0_e[i] + VS_AGGREGATED_PLAN_TIMES[e][i] * y_e[i]
    #         lp_solver.Add(-z_e[i] <= VS_DIRECTIVE_TERMS[e][i] - T_i)
    #         lp_solver.Add(VS_DIRECTIVE_TERMS[e][i] - T_i <= z_e[i])
    #
    #     # Y_L_i >= Y_ASSIGNED_L_i, i=1..n1
    #     for i in range(NUM_AGGREGATED_PRODUCTS[e]):
    #         lp_solver.Add(y_e[i] >= VS_NUM_DIRECTIVE_PRODUCTS[e][i])
    #
    #     # one more constraint
    #     # VS_COEFFS_CENTER_FUNCTIONAL[e]^T * y_e - sum_j={1..n1}(FINES_FOR_DEADLINE[e][j] * z_j) = f_e_1opt
    #     lp_solver.Add(sum(VS_COEFFS_CENTER_FUNCTIONAL[e][i] * y_e[i] for i in range(NUM_DECISION_VARIABLES[e])) -
    #                   sum(VS_FINES_FOR_DEADLINE[e][j] * z_e[j] for j in
    #                       range(NUM_AGGREGATED_PRODUCTS[e])) == f_e_1opt)
    #
    #     ## Defining Objective Function
    #
    #     # max (C^l ^T x y^l - sum_j={1..n1}(FINES_FOR_DEADLINE[e][j] * z_j))
    #     objective = lp_solver.Objective()
    #     for i in range(NUM_DECISION_VARIABLES[e]):
    #         objective.SetCoefficient(y_e[i], float(VS_COEFFS_ELEMENT_FUNCTIONAL[e][i]))
    #
    #     for i in range(NUM_AGGREGATED_PRODUCTS[e]):
    #         objective.SetCoefficient(z_e[i], float(-VS_FINES_FOR_DEADLINE[e][i]))
    #
    #     objective.SetMaximization()
    #
    #     status = lp_solver.Solve()
    #
    #     yield e, lp_solver.Objective().Value(), y_e, z_e, t_0_e if status == pywraplp.Solver.OPTIMAL else None

    """
    2'nd criteria for the center
    """

    for e in range(NUM_ELEMENTS):
        f_e_2opt = element_model(e, VS_COEFFS_CENTER_FUNCTIONAL[e])[0]

        lp_solver = pywraplp.Solver.CreateSolver("GLOP")

        # Define Variables
        y_e = [lp_solver.NumVar(0, lp_solver.infinity(), f"y_{e}_{i}") for i in range(NUM_DECISION_VARIABLES[e])]
        z_e = [lp_solver.NumVar(0, lp_solver.infinity(), f"z_{e}_{i}") for i in range(NUM_AGGREGATED_PRODUCTS[e])]
        t_0_e = [lp_solver.NumVar(0, lp_solver.infinity(), f"t_0_{e}_{i}") for i in range(NUM_AGGREGATED_PRODUCTS[e])]

        ## Defining Constraints

        # MS_AGGREGATED_PLAN_COSTS[e] * y_e <= VS_RESOURCE_CONSTRAINTS[e]
        for i in range(NUM_CONSTRAINTS[e]):
            lp_solver.Add(sum(MS_AGGREGATED_PLAN_COSTS[e][i][j] * y_e[j] for j in range(NUM_DECISION_VARIABLES[e])) <=
                          VS_RESOURCE_CONSTRAINTS[e][i])

        # T_i - z_i <= D_i, i=1..n2
        for i in range(NUM_SOFT_DEADLINE_PRODUCTS[e]):
            T_i = t_0_e[i] + VS_AGGREGATED_PLAN_TIMES[e][i] * y_e[i]
            lp_solver.Add(T_i - z_e[i] <= VS_DIRECTIVE_TERMS[e][i])
            if i != 0:
                lp_solver.Add(t_0_e[i] >= t_0_e[i - 1] + sum(VS_AGGREGATED_PLAN_TIMES[e][j] * y_e[j] for j in range(i)))

        # -z_i <= D_i - T_i <= z_i, i=n2+1..n1
        for i in range(NUM_SOFT_DEADLINE_PRODUCTS[e], NUM_AGGREGATED_PRODUCTS[e]):
            T_i = t_0_e[i] + VS_AGGREGATED_PLAN_TIMES[e][i] * y_e[i]
            lp_solver.Add(-z_e[i] <= VS_DIRECTIVE_TERMS[e][i] - T_i)
            lp_solver.Add(VS_DIRECTIVE_TERMS[e][i] - T_i <= z_e[i])

        # Y_L_i >= Y_ASSIGNED_L_i, i=1..n1
        for i in range(NUM_AGGREGATED_PRODUCTS[e]):
            lp_solver.Add(y_e[i] >= VS_NUM_DIRECTIVE_PRODUCTS[e][i])

        # one more constraint
        # C^l^T * y^l - sum_j={1..n1}(FINES_FOR_DEADLINE[e][j] * z_j) >= f_e_2opt - DELTA
        lp_solver.Add(sum(VS_COEFFS_CENTER_FUNCTIONAL[e][i] * y_e[i] for i in range(NUM_DECISION_VARIABLES[e])) -
                      sum(VS_FINES_FOR_DEADLINE[e][j] * z_e[j] for j in
                          range(NUM_AGGREGATED_PRODUCTS[e])) >= f_e_2opt - DELTA)

        ## Defining Objective Function

        # max (C^l ^T x y^l - sum_j={1..n1}(FINES_FOR_DEADLINE[e][j] * z_j))
        objective = lp_solver.Objective()
        for i in range(NUM_DECISION_VARIABLES[e]):
            objective.SetCoefficient(y_e[i], float(VS_COEFFS_ELEMENT_FUNCTIONAL[e][i]))

        for i in range(NUM_AGGREGATED_PRODUCTS[e]):
            objective.SetCoefficient(z_e[i], float(-VS_FINES_FOR_DEADLINE[e][i]))

        objective.SetMaximization()

        status = lp_solver.Solve()

        y_e_solved = [y_e[i].solution_value() for i in range(NUM_DECISION_VARIABLES[e])]
        z_e_solved = [z_e[i].solution_value() for i in range(NUM_AGGREGATED_PRODUCTS[e])]
        t_0_e_solved = [t_0_e[i].solution_value() for i in range(NUM_AGGREGATED_PRODUCTS[e])]

        yield e, lp_solver.Objective().Value(), y_e_solved, z_e_solved, t_0_e_solved if status == pywraplp.Solver.OPTIMAL else None


if __name__ == "__main__":
    center_data = (
        ("NUM_ELEMENTS", format_tensor(NUM_ELEMENTS)),
        ("NUM_CONSTRAINTS", format_tensor(NUM_CONSTRAINTS[e])),
        ("NUM_DECISION_VARIABLES", format_tensor(NUM_DECISION_VARIABLES[e])),
        ("NUM_AGGREGATED_PRODUCTS", format_tensor(NUM_AGGREGATED_PRODUCTS[e])),
        ("NUM_SOFT_DEADLINE_PRODUCTS", format_tensor(NUM_SOFT_DEADLINE_PRODUCTS[e])),
        ("FREE_ORDER", format_tensor(FREE_ORDER)),
        ("DELTA", format_tensor(DELTA)),
        ("VS_COEFFS_CENTER_FUNCTIONAL", format_tensor(VS_COEFFS_CENTER_FUNCTIONAL[e].tolist())),
    )

    print(tabulate(center_data, headers=["Parameter", "Value"],
                   tablefmt="grid", numalign="right", stralign="left"))

    center_objective = 0
    for e, objective, y_e, z_e, t_0_e in center_model():
        print(f"\nInput data for {e = }:")

        input_data = (
            ("VS_AGGREGATED_PLAN_TIMES", format_tensor(VS_AGGREGATED_PLAN_TIMES[e].tolist())),
            ("VS_RESOURCE_CONSTRAINTS", format_tensor(VS_RESOURCE_CONSTRAINTS[e].tolist())),
            ("VS_DIRECTIVE_TERMS", format_tensor(VS_DIRECTIVE_TERMS[e].tolist())),
            ("VS_NUM_DIRECTIVE_PRODUCTS", format_tensor(VS_NUM_DIRECTIVE_PRODUCTS[e].tolist())),
            ("VS_COEFFS_ELEMENT_FUNCTIONAL", format_tensor(VS_COEFFS_ELEMENT_FUNCTIONAL[e].tolist())),
            ("VS_FINES_FOR_DEADLINE", format_tensor(VS_FINES_FOR_DEADLINE[e].tolist())),
            ("MS_AGGREGATED_PLAN_COSTS", format_tensor(MS_AGGREGATED_PLAN_COSTS[e].tolist())),
            ("VS_AGGREGATED_PLAN_TIMES", format_tensor(VS_AGGREGATED_PLAN_TIMES[e].tolist())),
        )

        solution_data = (
            ("y_e", format_tensor(y_e)),
            ("z_e", format_tensor(z_e)),
            ("t_0_e", format_tensor(t_0_e)),
        )

        print(tabulate(input_data, headers=["Parameter", "Value"],
                       tablefmt="grid", numalign="right", stralign="left"))

        print(f"\nSolution for {e = }")
        print(tabulate(solution_data, headers=["Variable", "Value"],
                       tablefmt="grid", numalign="right", stralign="left"))

        print(f"\nELEMENT QUALITY FUNCTIONALITY = {format_tensor(objective)}")

        center_objective += sum(VS_COEFFS_CENTER_FUNCTIONAL[e][i] * y_e[i] for i in range(NUM_DECISION_VARIABLES[e])
                                ) - sum(VS_FINES_FOR_DEADLINE[e][j] * z_e[j] for j in range(NUM_AGGREGATED_PRODUCTS[e]))

    print(f"\nCENTER QUALITY FUNCTIONALITY = {format_tensor(center_objective)}")
