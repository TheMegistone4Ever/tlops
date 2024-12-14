import numpy as np

from constants import NUM_ELEMENTS, NUM_DECISION_VARIABLES, NUM_CONSTRAINTS

np.random.seed(1810)

# Data for linear programming problem

VS_COEFFS_LINEAR_FUNCTIONAL = np.empty(NUM_ELEMENTS, dtype=np.ndarray)
VS_RESOURCE_CONSTRAINTS = np.empty(NUM_ELEMENTS, dtype=np.ndarray)
MS_AGGREGATED_PLAN_COSTS = np.empty(NUM_ELEMENTS, dtype=np.ndarray)

VS_AGGREGATED_PLAN_TIMES = np.empty(NUM_ELEMENTS, dtype=np.ndarray)
VS_DIRECTIVE_TERMS = np.empty(NUM_ELEMENTS, dtype=np.ndarray)
VS_NUM_DIRECTIVE_PRODUCTS = np.empty(NUM_ELEMENTS, dtype=np.ndarray)

for l in range(NUM_ELEMENTS):
    VS_COEFFS_LINEAR_FUNCTIONAL[l] = np.random.randint(1, 10, (NUM_DECISION_VARIABLES[l]))
    VS_RESOURCE_CONSTRAINTS[l] = np.random.randint(50, 1_000, (NUM_CONSTRAINTS[l]))
    MS_AGGREGATED_PLAN_COSTS[l] = np.random.randint(1, 5, (NUM_CONSTRAINTS[l], NUM_DECISION_VARIABLES[l]))

    VS_AGGREGATED_PLAN_TIMES[l] = np.random.randint(1, 5, (NUM_CONSTRAINTS[l]))
    VS_DIRECTIVE_TERMS[l] = np.random.randint(1, 100, (NUM_CONSTRAINTS[l]))
    VS_NUM_DIRECTIVE_PRODUCTS[l] = np.random.randint(1, 10, (NUM_CONSTRAINTS[l]))

