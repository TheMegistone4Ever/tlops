from dataclasses import dataclass
from typing import List

from numpy import ndarray

from .element import ElementData


@dataclass(frozen=True)
class CenterConfig:
    """Configuration data for the system center."""

    num_elements: int


@dataclass(frozen=True)
class CenterData:
    """Data container for center-specific optimization parameters."""

    config: CenterConfig
    coeffs_functional: List[ndarray]
    elements: List[ElementData]
