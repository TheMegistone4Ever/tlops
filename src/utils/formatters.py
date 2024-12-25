def format_solution(obj_value: float, variables: dict) -> str:
    """Format optimization solution for display."""
    lines = [f"Objective Value: {obj_value:.4f}"]
    for name, value in variables.items():
        if isinstance(value, list):
            lines.append(f"{name}: [{', '.join(f'{v:.4f}' for v in value)}]")
        else:
            lines.append(f"{name}: {value:.4f}")
    return "\n".join(lines)
