from data.config import SystemConfig
from data.generator import DataGenerator
from solvers.center.criteria_1 import CenterCriteria1Solver
from solvers.center.criteria_2 import CenterCriteria2Solver


def main():
    # Initialize system configuration
    system_config = SystemConfig()

    # Generate test data
    data_generator = DataGenerator(system_config)
    system_data = data_generator.generate_system_data()

    # Create center solver for criteria 1
    solver_1 = CenterCriteria1Solver(system_data)
    solver_1.setup()
    solver_1.print_results()

    # Create center solver for criteria 2
    solver_2 = CenterCriteria2Solver(system_data, system_config.DELTA)
    solver_2.setup()
    solver_2.print_results()

if __name__ == "__main__":
    # TODO: Check all constraints. 2'nd priority

    main()
