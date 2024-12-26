import numpy as np

from constants import NUM_ELEMENTS, NUM_DECISION_VARIABLES, NUM_CONSTRAINTS, NUM_AGGREGATED_PRODUCTS

np.random.seed(1810)

# Data for linear programming problem

VS_COEFFS_ELEMENT_FUNCTIONAL = np.empty(NUM_ELEMENTS, dtype=np.ndarray)
VS_RESOURCE_CONSTRAINTS = np.empty(NUM_ELEMENTS, dtype=np.ndarray)
MS_AGGREGATED_PLAN_COSTS = np.empty(NUM_ELEMENTS, dtype=np.ndarray)

VS_AGGREGATED_PLAN_TIMES = np.empty(NUM_ELEMENTS, dtype=np.ndarray)
VS_DIRECTIVE_TERMS = np.empty(NUM_ELEMENTS, dtype=np.ndarray)
VS_NUM_DIRECTIVE_PRODUCTS = np.empty(NUM_ELEMENTS, dtype=np.ndarray)
VS_FINES_FOR_DEADLINE = np.empty(NUM_ELEMENTS, dtype=np.ndarray)

VS_COEFFS_CENTER_FUNCTIONAL = np.empty(NUM_ELEMENTS, dtype=np.ndarray)

for e in range(NUM_ELEMENTS):
    VS_COEFFS_ELEMENT_FUNCTIONAL[e] = np.random.randint(1, 10, (NUM_DECISION_VARIABLES[e]))
    VS_RESOURCE_CONSTRAINTS[e] = np.random.randint(1, 10, (NUM_CONSTRAINTS[e])) * 100
    MS_AGGREGATED_PLAN_COSTS[e] = np.random.randint(1, 5, (NUM_CONSTRAINTS[e], NUM_DECISION_VARIABLES[e]))

    VS_AGGREGATED_PLAN_TIMES[e] = np.random.randint(1, 5, (NUM_AGGREGATED_PRODUCTS[e]))
    VS_DIRECTIVE_TERMS[e] = np.random.randint(5, 25, (NUM_AGGREGATED_PRODUCTS[e])) * 5
    VS_NUM_DIRECTIVE_PRODUCTS[e] = np.random.randint(5, 10, (NUM_AGGREGATED_PRODUCTS[e]))
    VS_FINES_FOR_DEADLINE[e] = np.random.randint(1, 10, (NUM_AGGREGATED_PRODUCTS[e]))

    VS_COEFFS_CENTER_FUNCTIONAL[e] = np.random.randint(1, 3, (NUM_DECISION_VARIABLES[e]))
