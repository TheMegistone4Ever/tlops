from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class SystemConfig:
    """System-wide configuration parameters."""

    NUM_ELEMENTS: int = 3  # K
    NUM_DECISION_VARIABLES: List[int] = field(default_factory=lambda: [6, 4, 3])  # n
    NUM_AGGREGATED_PRODUCTS: List[int] = field(default_factory=lambda: [5, 4, 2])  # n1 <= n
    NUM_SOFT_DEADLINE_PRODUCTS: List[int] = field(default_factory=lambda: [3, 4, 1])  # n2 <= n1
    NUM_CONSTRAINTS: List[int] = field(default_factory=lambda: [4, 2, 3])  # m
    FREE_ORDER: bool = True
    DELTA: float = 10.0  # For second criteria
