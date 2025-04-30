from typing import Any

from solvers.base import BaseSolver


class CenterCriteria8Solver(BaseSolver):
    """Implementation of the eight optimization criteria for the center."""

    def setup_variables(self) -> None:
        raise NotImplementedError("Criteria 8 is not implemented")

    def setup_constraints(self) -> None:
        raise NotImplementedError("Criteria 8 is not implemented")

    def setup_objective(self) -> None:
        raise NotImplementedError("Criteria 8 is not implemented")

    def get_solution(self) -> Any:
        raise NotImplementedError("Criteria 8 is not implemented")

    def print_results(self) -> None:
        pass
