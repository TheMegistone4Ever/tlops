# ui/tabs/configuration_tab.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QSpinBox, QComboBox, QPushButton, QGridLayout,
                             QDoubleSpinBox, QFrame)
from PyQt5.QtCore import Qt
from typing import Dict, List


class ElementWidget(QFrame):
    def __init__(self, element_num: int):
        super().__init__()
        self.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.element_num = element_num
        self.fields: Dict = {}
        self.criterion_combo: QComboBox = None
        self.criteria_specific: Dict = {}
        self.init_ui()

    def init_ui(self):
        layout = QGridLayout(self)

        # Element header
        header = QLabel(f"Element {self.element_num}")
        header.setStyleSheet("font-weight: bold")
        layout.addWidget(header, 0, 0, 1, 2)

        # Criterion dropdown
        criterion_label = QLabel("Criterion:")
        self.criterion_combo = QComboBox()
        self.criterion_combo.addItems(["Criterion 1", "Criterion 2"])
        for i in range(3, 9):
            self.criterion_combo.addItem(f"Criterion {i} (Not Implemented)")
            self.criterion_combo.model().item(i - 1).setEnabled(False)
        layout.addWidget(criterion_label, 1, 0)
        layout.addWidget(self.criterion_combo, 1, 1)

        # Common fields
        common_fields = {
            "num_decision_variables": ("Variables", (1, 1000)),
            "num_aggregated_products": ("Products", (1, 1000)),
            "num_soft_deadline_products": ("Soft Deadline", (1, 1000)),
            "num_constraints": ("Constraints", (1, 1000)),
            "num_directive_products": ("Directive Products", (1, 1000))  # Added this field
        }

        row = 2
        for field_name, (label_text, (min_val, max_val)) in common_fields.items():
            label = QLabel(f"{label_text}:")
            spinbox = QSpinBox()
            spinbox.setRange(min_val, max_val)
            # Set default value to match number of products for directive products
            if field_name == "num_directive_products":
                spinbox.setValue(self.fields["num_aggregated_products"].value() if "num_aggregated_products" in self.fields else 1)
                # Connect to update when products change
                if "num_aggregated_products" in self.fields:
                    self.fields["num_aggregated_products"].valueChanged.connect(spinbox.setValue)
            layout.addWidget(label, row, 0)
            layout.addWidget(spinbox, row, 1)
            self.fields[field_name] = spinbox
            row += 1

        # Rest of the code remains the same...

    def get_configuration(self) -> dict:
        config = {
            name: spinbox.value()
            for name, spinbox in self.fields.items()
        }

        config['criterion'] = self.criterion_combo.currentIndex() + 1

        # Add criteria-specific configuration
        if config['criterion'] == 2:
            delta_spinbox = self.criteria_specific[1].findChild(QDoubleSpinBox)
            if delta_spinbox:
                config['delta'] = delta_spinbox.value()

        return config


class ConfigurationTab(QWidget):
    def __init__(self):
        super().__init__()
        self.element_widgets: List[ElementWidget] = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Elements count input
        elements_layout = QHBoxLayout()
        elements_label = QLabel("Number of elements (N):")
        self.elements_spinbox = QSpinBox()
        self.elements_spinbox.setRange(1, 100)
        elements_layout.addWidget(elements_label)
        elements_layout.addWidget(self.elements_spinbox)
        elements_layout.addStretch()

        # Elements grid
        self.elements_grid = QGridLayout()

        # Next button
        self.next_button = QPushButton("Next")
        self.next_button.setEnabled(False)

        # Add to main layout
        layout.addLayout(elements_layout)
        layout.addLayout(self.elements_grid)
        layout.addStretch()
        layout.addWidget(self.next_button, alignment=Qt.AlignRight)

        # Connect signals
        self.elements_spinbox.valueChanged.connect(self.update_elements_grid)

    def update_elements_grid(self, n: int):
        # Clear existing grid
        for widget in self.element_widgets:
            widget.deleteLater()
        self.element_widgets.clear()

        # Add new elements
        for i in range(n):
            widget = ElementWidget(i + 1)
            self.elements_grid.addWidget(widget, i // 2, i % 2)
            self.element_widgets.append(widget)

        # Enable next button if we have elements
        self.next_button.setEnabled(n > 0)

    def get_configuration(self) -> List[dict]:
        return [widget.get_configuration() for widget in self.element_widgets]