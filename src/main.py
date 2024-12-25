from data.config import SystemConfig
from data.generator import DataGenerator
from models.center import CenterConfig
from solvers.center.criteria_1 import CenterCriteria1Solver
from solvers.center.criteria_2 import CenterCriteria2Solver
from utils.formatters import format_solution


def main():
    # Initialize system configuration
    system_config = SystemConfig()

    # Generate test data
    data_generator = DataGenerator(system_config)
    system_data = data_generator.generate_system_data()

    # Create center solver for criteria 1
    solver_1 = CenterCriteria1Solver(system_data)
    solver_1.setup_variables()
    solver_1.setup_constraints()
    solver_1.setup_objective()
    result_1 = solver_1.solve()

    # Create center solver for criteria 2
    solver_2 = CenterCriteria2Solver(system_data, system_config.DELTA)
    solver_2.setup_variables()
    solver_2.setup_constraints()
    solver_2.setup_objective()
    result_2 = solver_2.solve()

    print("Results for different criteria:")
    print(f"Criteria 1: {result_1[0] if result_1 else 'No solution'}")
    print(f"Criteria 2: {result_2[0] if result_2 else 'No solution'}")


if __name__ == "__main__":
    main()
