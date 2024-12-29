from data.config import SystemConfig
from data.generator import DataGenerator
from solvers.center.criteria_1 import CenterCriteria1Solver
from solvers.center.criteria_2 import CenterCriteria2Solver


def main():
    system_config = SystemConfig()
    data_generator = DataGenerator(system_config)
    system_data = data_generator.generate_system_data()

    solver_1 = CenterCriteria1Solver(system_data)
    solver_1.setup()
    solver_1.print_results()

    solver_2 = CenterCriteria2Solver(system_data, system_config.DELTA)
    solver_2.setup()
    solver_2.print_results()


if __name__ == "__main__":
    main()
