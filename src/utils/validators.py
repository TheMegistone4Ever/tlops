from typing import Any, List

import numpy as np


def validate_dimensions(arrays: List[np.ndarray], expected_dims: List[int]) -> bool:
    """Validate dimensions of numpy arrays against expected dimensions."""
    return all(arr.shape == dim for arr, dim in zip(arrays, expected_dims))


def validate_positive(value: Any) -> bool:
    """Validate that a value is positive."""
    return float(value) > 0 if isinstance(value, (int, float, np.number)) else False


def validate_non_negative(value: Any) -> bool:
    """Validate that a value is non-negative."""
    return float(value) >= 0 if isinstance(value, (int, float, np.number)) else False
