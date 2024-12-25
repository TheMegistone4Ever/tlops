from typing import Any, List

import numpy as np


def assert_positive(value: Any, name: str = "") -> None:
    """Assert that a value is positive."""
    assert float(value) > 0, f"Value {name} must be positive, got {value}"


def assert_non_negative(value: Any, name: str = "") -> None:
    """Assert that a value is non-negative."""
    assert float(value) >= 0, f"Value {name} must be non-negative, got {value}"


def assert_valid_dimensions(arrays: List[np.ndarray],
                            expected_dims: List[int | tuple[int]],
                            names: List[str]) -> None:
    """Assert that arrays have valid dimensions."""
    for arr, dim, name in zip(arrays, expected_dims, names):
        assert arr.shape == dim, \
            f"Array {name} has invalid dimensions. Expected {dim}, got {arr.shape}"
