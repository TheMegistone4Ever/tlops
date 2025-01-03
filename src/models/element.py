from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ElementConfig:
    """Configuration data for an element in the system."""

    id: int
    num_decision_variables: int
    num_aggregated_products: int
    num_soft_deadline_products: int
    num_constraints: int
    free_order: bool


@dataclass(frozen=True)
class ElementData:
    """Data container for element-specific optimization parameters."""

    config: ElementConfig
    coeffs_functional: np.ndarray
    resource_constraints: np.ndarray
    aggregated_plan_costs: np.ndarray
    aggregated_plan_times: np.ndarray
    directive_terms: np.ndarray
    num_directive_products: np.ndarray
    fines_for_deadline: np.ndarray
