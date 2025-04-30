from PyQt5.QtWidgets import QLabel, QDoubleSpinBox
from .base_criteria_tab import BaseCriteriaTab


class Criteria2Tab(BaseCriteriaTab):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        delta_label = QLabel("Delta:")
        self.delta_input = QDoubleSpinBox()
        self.delta_input.setRange(0, 1)
        self.delta_input.setSingleStep(0.1)

        self.layout.addWidget(delta_label)
        self.layout.addWidget(self.delta_input)
        self.layout.addStretch()

    def validate_inputs(self):
        return True

    def get_input_data(self):
        return {"delta": self.delta_input.value()}