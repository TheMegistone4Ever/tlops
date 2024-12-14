def format_tensor(tensor):
    """
    Formats matrices and nested lists for better readability.
    Handles single lists, 2D lists, and numpy arrays.
    """

    if not isinstance(tensor, list):
        return str(round(tensor, 2)) if isinstance(tensor, (int, float)) and not isinstance(tensor, int) else str(
            tensor)

    if not isinstance(tensor, list) or not any(isinstance(item, list) for item in tensor):
        return "[" + ", ".join(
            str(round(row, 2)) if isinstance(row, (int, float)) and not isinstance(row, int) else str(row) for row in
            tensor) + "]"

    return "[\n    " + ",\n    ".join(
        str(round(row, 2)) if isinstance(row, (int, float)) and not isinstance(row, int) else str(row)
        for row in tensor
    ) + "\n]"
