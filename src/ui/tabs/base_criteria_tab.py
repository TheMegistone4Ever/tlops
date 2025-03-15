from PyQt5.QtWidgets import QWidget, QVBoxLayout


class BaseCriteriaTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

    def validate_inputs(self):
        raise NotImplementedError()

    def get_input_data(self):
        raise NotImplementedError()


# ui/criteria/criteria1_tab.py
from .base_criteria_tab import BaseCriteriaTab


class Criteria1Tab(BaseCriteriaTab):
    def __init__(self):
        super().__init__()
        # No additional inputs needed for Criteria 1

    def validate_inputs(self):
        return True

    def get_input_data(self):
        return {}