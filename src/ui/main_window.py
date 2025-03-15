# ui/main_window.py
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout
from .tabs.configuration_tab import ConfigurationTab
from .tabs.detailed_input_tab import DetailedInputTab
from .tabs.results_tab import ResultsTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Optimization Interface")
        self.setMinimumSize(800, 600)

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Create tab widget
        self.tab_widget = QTabWidget()

        # Initialize tabs
        self.config_tab = ConfigurationTab()
        self.detailed_tab = DetailedInputTab()
        self.results_tab = ResultsTab()

        # Add tabs to widget
        self.tab_widget.addTab(self.config_tab, "Configuration")
        self.tab_widget.addTab(self.detailed_tab, "Detailed Input")
        self.tab_widget.addTab(self.results_tab, "Results")

        # Connect signals
        self.config_tab.next_button.clicked.connect(self.on_next_clicked)
        self.detailed_tab.solve_button.clicked.connect(self.on_solve_clicked)

        layout.addWidget(self.tab_widget)

    def on_next_clicked(self):
        # Get configuration data from config tab
        config_data = self.config_tab.get_configuration()
        # Update detailed tab with configuration
        self.detailed_tab.update_inputs(config_data)
        # Switch to detailed input tab
        self.tab_widget.setCurrentIndex(1)

    def on_solve_clicked(self):
        self.tab_widget.setCurrentIndex(2)


# ui/tabs/configuration_tab.py (add this method)
def get_configuration(self):
    config_data = []

    for widget in self.element_widgets:
        # Get spinboxes and combo for this element
        spinboxes = widget.findChildren(QSpinBox)
        combo = widget.findChildren(QComboBox)[0]

        element_config = {
            'num_decision_variables': spinboxes[0].value(),
            'num_aggregated_products': spinboxes[1].value(),
            'num_soft_deadline_products': spinboxes[2].value(),
            'num_constraints': spinboxes[3].value(),
            'criterion': combo.currentIndex() + 1,
        }

        # Add criteria-specific configuration
        if element_config['criterion'] == 2:
            delta_spinbox = widget.findChildren(QDoubleSpinBox)[0]
            element_config['delta'] = delta_spinbox.value()

        config_data.append(element_config)

    return config_data
