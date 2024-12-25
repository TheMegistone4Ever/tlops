import numpy as np
from typing import List
from models.element import ElementData
from models.center import CenterData
from .config import SystemConfig

class DataGenerator:
    """Generates random test data for the optimization system."""

    def __init__(self, config: SystemConfig, seed: int = 1810):
        """Initialize the data generator with system configuration."""
        self.config = config
        np.random.seed(seed)

    def _generate_element_data(self, element_idx: int) -> ElementData:
        """Generate random data for a single element."""
        n = self.config.NUM_DECISION_VARIABLES[element_idx]
        m = self.config.NUM_CONSTRAINTS[element_idx]
        n1 = self.config.NUM_AGGREGATED_PRODUCTS[element_idx]

        return ElementData(
            coeffs_functional=np.random.randint(1, 10, (n)),
            resource_constraints=np.random.randint(1, 10, (m)) * 100,
            aggregated_plan_costs=np.random.randint(1, 5, (m, n)),
            aggregated_plan_times=np.random.randint(1, 5, (n1)),
            directive_terms=np.random.randint(5, 25, (n1)) * 5,
            num_directive_products=np.random.randint(5, 10, (n1)),
            fines_for_deadline=np.random.randint(1, 10, (n1))
        )

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

        return CenterData(
            coeffs_functional=center_coeffs,
            elements=elements_data
        )
