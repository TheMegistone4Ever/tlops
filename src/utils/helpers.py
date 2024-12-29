from dataclasses import replace
from numbers import Number
from typing import Union, List, Any, Sequence, Optional

import numpy as np
from tabulate import tabulate

from models.element import ElementData


def tab_out(subscription: str, data: Sequence[Sequence[str]], headers: List[str] = ("Parameter", "Value")) -> None:
    print(f"\n{subscription}:")
    print(tabulate(data, headers=headers, tablefmt="grid", numalign="right", stralign="left"))


def format_tensor(tensor: Union[Number, List[Any], np.ndarray], indent: int = 4, precision: int = 2) -> str:
    """
    Formats n-dimensional tensors (nested lists/arrays) for better readability.

    Args:
        tensor: Input tensor (can be a number, list, nested list, or numpy array)
        indent: Number of spaces for each level of indentation
        precision: Number of decimal places for floating-point numbers

    Returns:
        str: Formatted string representation of the tensor

    Examples:
        >>> format_tensor(42)
        42
        >>> format_tensor([1, 2, 3])
        [1, 2, 3]
        >>> format_tensor([[1, 2], [3, 4]])
        [
            [1, 2],
            [3, 4]
        ]
    """

    # Convert numpy arrays to lists for consistent handling
    if isinstance(tensor, np.ndarray):
        tensor = tensor.tolist()

    def format_number(x: Number) -> str:
        """Helper function to format numbers with consistent precision"""
        if isinstance(x, float):
            return str(round(x, precision))
        return str(x)

    def is_nested(x: Any) -> bool:
        """Helper function to check if an object is a nested structure"""
        return isinstance(x, list) and any(isinstance(item, (list, np.ndarray)) for item in x)

    def format_recursive(x: Any, level: int = 0) -> str:
        """Recursively format nested structures"""
        # Base case: handle numbers
        if isinstance(x, Number):
            return format_number(x)

        # Handle non-nested lists
        if isinstance(x, list) and not is_nested(x):
            elements = [format_number(item) if isinstance(item, Number) else str(item) for item in x]
            return f"[{", ".join(elements)}]"

        # Handle nested structures
        if isinstance(x, list):
            spacer = " " * (level * indent)
            next_spacer = " " * ((level + 1) * indent)
            elements = [format_recursive(item, level + 1) for item in x]
            return f"[\n{next_spacer}" + f",\n{next_spacer}".join(elements) + f"\n{spacer}]"

        # Fall back to string representation for other types
        return str(x)

    return format_recursive(tensor)


def copy_element_with_coeffs(element: ElementData, coeffs_functional: Optional[np.ndarray] = None) -> ElementData:
    """Creates a copy of an ElementData instance with optionally modified coeffs_functional."""

    return element if coeffs_functional is None else replace(element, coeffs_functional=coeffs_functional)


if __name__ == "__main__":
    num_0d = 42
    list_1d = [1, 2, 3]
    list_2d = [[1, 2], [3, 4]]
    array_1d = np.array([1, 2, 3])
    array_2d = np.array([[1, 2], [3, 4]])
    tensor_3d_int = [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]
    tensor_3d_float = np.array(tensor_3d_int, dtype=float) + .123456789

    print(f"Number:\n{format_tensor(num_0d)}", end="\n\n")
    print(f"1D List:\n{format_tensor(list_1d)}", end="\n\n")
    print(f"2D List:\n{format_tensor(list_2d)}", end="\n\n")
    print(f"1D Array:\n{format_tensor(array_1d)}", end="\n\n")
    print(f"2D Array:\n{format_tensor(array_2d)}", end="\n\n")
    print(f"3D Tensor (int):\n{format_tensor(tensor_3d_int)}", end="\n\n")
    print(f"3D Tensor (float, 6 d.p.):\n{format_tensor(tensor_3d_float, precision=6)}", end="\n\n")
