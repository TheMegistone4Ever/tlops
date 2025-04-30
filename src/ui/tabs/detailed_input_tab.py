# ui/tabs/detailed_input_tab.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTextEdit,
                             QPushButton, QGridLayout, QFrame, QScrollArea,
                             QGroupBox)
from PyQt5.QtCore import Qt


class MatrixInput(QFrame):
    def __init__(self, name, rows, cols, tooltip=""):
        super().__init__()
        self.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.name = name
        self.rows = rows
        self.cols = cols
        self.init_ui(tooltip)

    def init_ui(self, tooltip):
        layout = QVBoxLayout(self)

        # Header with tooltip
        header = QLabel(f"{self.name} ({self.rows}x{self.cols}):")
        if tooltip:
            header.setToolTip(tooltip)
        layout.addWidget(header)

        # Input field
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText(
            "Enter values in format:\nx11, x12, x13\nx21, x22, x23\n..."
        )
        layout.addWidget(self.text_edit)

    def validate(self):
        try:
            data = self.get_data()
            return (len(data) == self.rows and
                    all(len(row) == self.cols for row in data))
        except:
            return False

    def get_data(self):
        text = self.text_edit.toPlainText().strip()
        if not text:
            return []

        rows = text.split('\n')
        return [
            [float(x.strip()) for x in row.split(',')]
            for row in rows
        ]


class VectorInput(QFrame):
    def __init__(self, name, size, tooltip=""):
        super().__init__()
        self.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.name = name
        self.size = size
        self.init_ui(tooltip)

    def init_ui(self, tooltip):
        layout = QVBoxLayout(self)

        # Header with tooltip
        header = QLabel(f"{self.name} (size {self.size}):")
        if tooltip:
            header.setToolTip(tooltip)
        layout.addWidget(header)

        # Input field
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText(
            "Enter values in format:\nx1, x2, x3, ..."
        )
        self.text_edit.setMaximumHeight(70)
        layout.addWidget(self.text_edit)

    def validate(self):
        try:
            data = self.get_data()
            return len(data) == self.size
        except:
            return False

    def get_data(self):
        text = self.text_edit.toPlainText().strip()
        if not text:
            return []
        return [float(x.strip()) for x in text.split(',')]


class ElementInputGroup(QGroupBox):
    def __init__(self, element_num, config):
        super().__init__(f"Element {element_num}")
        self.config = config
        self.inputs = {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Create all required inputs for the element
        self.inputs['coeffs_functional'] = VectorInput(
            "Functional Coefficients",
            self.config['num_decision_variables'],
            "Coefficients for the functional part of the optimization"
        )

        self.inputs['resource_constraints'] = MatrixInput(
            "Resource Constraints",
            self.config['num_constraints'],
            self.config['num_decision_variables'],
            "Matrix of resource constraints coefficients"
        )

        self.inputs['aggregated_plan_costs'] = MatrixInput(
            "Aggregated Plan Costs",
            self.config['num_aggregated_products'],
            self.config['num_decision_variables'],
            "Matrix of costs for aggregated products"
        )

        self.inputs['aggregated_plan_times'] = MatrixInput(
            "Aggregated Plan Times",
            self.config['num_aggregated_products'],
            self.config['num_decision_variables'],
            "Matrix of times for aggregated products"
        )

        self.inputs['directive_terms'] = VectorInput(
            "Directive Terms",
            self.config['num_directive_products'],
            "Vector of directive terms"
        )

        self.inputs['num_directive_products'] = VectorInput(
            "Number of Directive Products",
            self.config['num_decision_variables'],
            "Vector specifying number of directive products"
        )

        self.inputs['fines_for_deadline'] = VectorInput(
            "Fines for Deadline",
            self.config['num_soft_deadline_products'],
            "Vector of fines for missing soft deadlines"
        )

        # Add all inputs to layout
        for input_widget in self.inputs.values():
            layout.addWidget(input_widget)

    def validate(self):
        return all(input_widget.validate() for input_widget in self.inputs.values())

    def get_data(self):
        return {name: input_widget.get_data()
                for name, input_widget in self.inputs.items()}


class DetailedInputTab(QWidget):
    def __init__(self):
        super().__init__()
        self.element_groups = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Scroll area for inputs
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Container for inputs
        self.input_container = QWidget()
        self.input_layout = QVBoxLayout(self.input_container)

        scroll.setWidget(self.input_container)
        layout.addWidget(scroll)

        # Solve button
        self.solve_button = QPushButton("Solve")
        self.solve_button.setEnabled(False)
        layout.addWidget(self.solve_button, alignment=Qt.AlignRight)

    def update_inputs(self, config_data):
        # Clear existing inputs
        while self.input_layout.count():
            item = self.input_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.element_groups.clear()

        # Add new inputs based on configuration
        for i, element_config in enumerate(config_data):
            group = ElementInputGroup(i + 1, element_config)
            self.element_groups.append(group)
            self.input_layout.addWidget(group)

        self.input_layout.addStretch()

        # Connect validation
        self.validate_all()

    def validate_all(self):
        valid = all(group.validate() for group in self.element_groups)
        self.solve_button.setEnabled(valid)
        return valid

    def get_input_data(self):
        return [group.get_data() for group in self.element_groups]