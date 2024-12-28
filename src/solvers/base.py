from abc import ABC, abstractmethod
from typing import Any, Tuple, Dict

from ortools.linear_solver import pywraplp


class BaseSolver(ABC):
    """Base class for all optimization solvers."""

    def __init__(self):
        self.solver = pywraplp.Solver.CreateSolver("GLOP")
        self.solved = False

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

    def setup(self):
        """Set up the optimization problem."""
        self.setup_variables()
        self.setup_constraints()
        self.setup_objective()

    def solve(self) -> Tuple[float, Any]:
        """Solve the optimization problem."""
        if not self.solved:
            status = self.solver.Solve()
            if status == pywraplp.Solver.OPTIMAL:
                return self.solver.Objective().Value(), self.get_solution()
            self.solved = True
        return float("inf"), dict()

    @abstractmethod
    def get_solution(self) -> Dict[str, Any]:
        """Extract the solution from the solver."""
        pass

    @abstractmethod
    def print_results(self) -> None:
        """Print the results of the optimization."""
        pass
