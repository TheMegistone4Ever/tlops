from typing import Any

from solvers.base import BaseSolver


class CenterCriteria7Solver(BaseSolver):
    """Implementation of the 7th optimization criteria for the center."""

    def setup_variables(self) -> None:
        raise NotImplementedError("Criteria 7 is not implemented")

    def setup_constraints(self) -> None:
        raise NotImplementedError("Criteria 7 is not implemented")

    def setup_objective(self) -> None:
        raise NotImplementedError("Criteria 7 is not implemented")

    def get_solution(self) -> Any:
        raise NotImplementedError("Criteria 7 is not implemented")