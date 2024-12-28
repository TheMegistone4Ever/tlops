from dataclasses import dataclass
from typing import List

import numpy as np

from .element import ElementData


@dataclass(frozen=True)
class CenterConfig:
    """Configuration data for the system center."""
    num_elements: int
    free_order: bool
    delta: float


@dataclass(frozen=True)
class CenterData:
    """Data container for center-specific optimization parameters."""
    config: CenterConfig
    coeffs_functional: List[np.ndarray]
    elements: List[ElementData]
