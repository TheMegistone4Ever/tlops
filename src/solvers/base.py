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

    def setup(self):
        """Set up the optimization problem."""
        self.setup_variables()
        self.setup_constraints()
        self.setup_objective()

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

    # TODO: STUB, implement printing results
    def print_results(self) -> None:
        """Print the results of the optimization."""
        solution = self.solve()
        if solution:
            print(f"Optimal value: {solution[0]}")
            print(f"Solution: {solution[1]}")
        else:
            print("No solution found.")
