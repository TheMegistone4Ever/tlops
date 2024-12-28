import numpy as np

from models.center import CenterData, CenterConfig
from models.element import ElementData, ElementConfig
from utils.assertions import assert_positive, assert_valid_dimensions
from .config import SystemConfig


class DataGenerator:
    """Generates random test data for the optimization system."""

    def __init__(self, config: SystemConfig, seed: int = 1810):
        """Initialize the data generator with system configuration."""
        assert_positive(config.NUM_ELEMENTS, "NUM_ELEMENTS")
        for i, (n) in enumerate(config.NUM_DECISION_VARIABLES):
            assert_positive(n, f"NUM_DECISION_VARIABLES[{i}]")
        self.config = config
        np.random.seed(seed)

    def _generate_element_data(self, element_idx: int) -> ElementData:
        """Generate random data for a single element."""
        n = self.config.NUM_DECISION_VARIABLES[element_idx]
        m = self.config.NUM_CONSTRAINTS[element_idx]
        n1 = self.config.NUM_AGGREGATED_PRODUCTS[element_idx]

        coeffs_functional = np.random.randint(1, 10, (n))
        resource_constraints = np.random.randint(1, 10, (m)) * 100
        aggregated_plan_costs = np.random.randint(1, 5, (m, n))

        assert_valid_dimensions(
            [coeffs_functional, resource_constraints, aggregated_plan_costs],
            [(n,), (m,), (m, n)],
            ["coeffs_functional", "resource_constraints"]
        )

        element_config = ElementConfig(
            id=element_idx,
            num_decision_variables=n,
            num_aggregated_products=n1,
            num_soft_deadline_products=self.config.NUM_SOFT_DEADLINE_PRODUCTS[element_idx],
            num_constraints=m
        )

        element_data = ElementData(
            config=element_config,
            coeffs_functional=coeffs_functional,
            resource_constraints=resource_constraints,
            aggregated_plan_costs=aggregated_plan_costs,
            aggregated_plan_times=np.random.randint(1, 5, (n1)),
            directive_terms=np.random.randint(5, 25, (n1)) * 5,
            num_directive_products=np.random.randint(5, 10, (n1)),
            fines_for_deadline=np.random.randint(1, 10, (n1))
        )

        return element_data

    def generate_system_data(self) -> CenterData:
        """Generate complete system data."""
        elements_data = [
            self._generate_element_data(i)
            for i in range(self.config.NUM_ELEMENTS)
        ]

        center_coeffs = [
            np.random.randint(1, 3, (self.config.NUM_DECISION_VARIABLES[i]))
            for i in range(self.config.NUM_ELEMENTS)
        ]

        center_config = CenterConfig(
            num_elements=self.config.NUM_ELEMENTS,
            free_order=self.config.FREE_ORDER,
        )

        center_data = CenterData(
            config=center_config,
            coeffs_functional=center_coeffs,
            elements=elements_data
        )

        return center_data
