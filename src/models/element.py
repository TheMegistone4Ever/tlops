from dataclasses import dataclass
from enum import IntEnum, auto

from numpy import ndarray


class ElementType(IntEnum):
    """Enumeration of element types in the system."""

    PARALLEL = auto()
    SEQUENTIAL = auto()


@dataclass(frozen=True)
class ElementConfig:
    """Configuration data for an element in the system."""

    id: int
    num_decision_variables: int
    num_aggregated_products: int
    num_soft_deadline_products: int
    num_constraints: int
    free_order: bool
    type: ElementType


@dataclass(frozen=True)
class ElementData:
    """Data container for element-specific optimization parameters."""

    config: ElementConfig
    coeffs_functional: ndarray
    resource_constraints: ndarray
    aggregated_plan_costs: ndarray
    aggregated_plan_times: ndarray
    directive_terms: ndarray
    num_directive_products: ndarray
    fines_for_deadline: ndarray
