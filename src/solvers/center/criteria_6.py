from typing import Any

from solvers.base import BaseSolver


class CenterCriteria6Solver(BaseSolver):
    """Implementation of the 6th optimization criteria for the center."""

    def setup_variables(self) -> None:
        raise NotImplementedError("Criteria 6 is not implemented")

    def setup_constraints(self) -> None:
        raise NotImplementedError("Criteria 6 is not implemented")

    def setup_objective(self) -> None:
        raise NotImplementedError("Criteria 6 is not implemented")

    def get_solution(self) -> Any:
        raise NotImplementedError("Criteria 6 is not implemented")