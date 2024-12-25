from abc import ABC, abstractmethod
from typing import Any, Optional, Tuple
from ortools.linear_solver import pywraplp


class BaseSolver(ABC):
    """Base class for all optimization solvers."""

    def __init__(self):
        self.solver = pywraplp.Solver.CreateSolver("GLOP")

    @abstractmethod
    def setup_variables(self) -> None:
        """Set up optimization variables."""
        pass

    @abstractmethod
    def setup_constraints(self) -> None:
        """Set up optimization constraints."""
        pass

    @abstractmethod
    def setup_objective(self) -> None:
        """Set up the objective function."""
        pass

    def solve(self) -> Optional[Tuple[float, Any]]:
        """Solve the optimization problem."""
        status = self.solver.Solve()
        if status == pywraplp.Solver.OPTIMAL:
            return self.solver.Objective().Value(), self.get_solution()
        return None

    @abstractmethod
    def get_solution(self) -> Any:
        """Extract the solution from the solver."""
        pass
