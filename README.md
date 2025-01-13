# TLOPS (Two-Level Optimization Production System)

###### &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp; — by [Mykyta Kyselov (TheMegistone4Ever)](https://github.com/TheMegistone4Ever).

A sophisticated two-level optimization system for production planning with multiple optimization criteria and resource
constraints. This system implements various optimization strategies for coordinating production elements while
considering resource limitations, time constraints, and quality metrics.

## Table of Contents

1. [Introduction](#1-introduction)
    1. [Overview](#11-overview)
    2. [Key Features](#12-key-features)
2. [System Requirements](#2-system-requirements)
3. [Installation](#3-installation)
4. [Usage](#4-usage)
    1. [Basic Usage](#41-basic-usage)
    2. [Configuration](#42-configuration)
    3. [Running Different Criteria](#43-running-different-criteria)
5. [Project Structure](#5-project-structure)
6. [Components](#6-components)
    1. [Data Generation](#61-data-generation)
    2. [Models](#62-models)
    3. [Solvers](#63-solvers)
    4. [Utilities](#64-utilities)
7. [Contributing](#7-contributing)
8. [License](#8-license)

## 1. Introduction

### 1.1 Overview

TLOPS is a Python-based optimization system designed for complex production environments. It implements a two-level
optimization approach where a central coordinator manages multiple production elements, each with their own constraints
and objectives.

### 1.2 Key Features

- Multi-criteria optimization support (7 different criteria)
- Resource and time constraint handling
- Flexible production planning
- Deadline management with both soft and hard constraints
- Quality-oriented objective functions
- Automated test data generation

## 2. System Requirements

- Python 3.8+
- OR-Tools
- NumPy
- Tabulate

## 3. Installation

```bash
# Clone the repository
git clone https://github.com/TheMegistone4Ever/tlops.git
cd tlops

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install numpy ortools tabulate
```

## 4. Usage

### 4.1 Basic Usage

The system can be run using the main script:

```python
    python src/main.py
```

### 4.2 Configuration

System configuration is handled through the `SystemConfig` class. Modify the parameters in `src/data/config.py` to
adjust:

- Number of elements
- Decision variables
- Constraints
- Aggregated products
- Soft deadline products

### 4.3 Running Different Criteria

Currently, Criteria 1 and 2 are fully implemented:
class CenterCriteria1Solver:

```python
# Using Criteria 1
solver_1 = CenterCriteria1Solver(system_data)
solver_1.setup()
solver_1.print_results()

# Using Criteria 2
solver_2 = CenterCriteria2Solver(system_data, delta=[.1, .3, ...])
solver_2.setup()
solver_2.print_results()
```

## 5. Project Structure

```
src/
├── data/
│   ├── config.py          # System configuration
│   ├── generator.py       # Test data generation
├── models/
│   ├── center.py         # Center-related data structures
│   ├── element.py        # Element-related data structures
├── solvers/
│   ├── center/           # Center-level solvers
│   │   ├── criteria_*.py # Different optimization criteria
│   ├── element/          # Element-level solvers
│   │   ├── default.py    # Default element solver
│   ├── base.py          # Base solver class
├── utils/
│   ├── assertions.py     # Input validation
│   ├── formatters.py     # Output formatting
│   ├── validators.py     # Data validation
└── main.py              # Main execution script
```

## 6. Components

### 6.1 Data Generation

The `DataGenerator` class in `generator.py` creates random test data for the optimization system, including:

- Element-specific parameters
- Resource constraints
- Time constraints
- Production targets

### 6.2 Models

Two main data models:

- `CenterData`: Contains system-wide parameters and coordinates elements
- `ElementData`: Holds element-specific parameters and constraints

### 6.3 Solvers

Multiple solver implementations:

- Base solver (`BaseSolver`)
- Element solver (`ElementSolver`)
- Center criteria solvers (7 different optimization criteria)

### 6.4 Utilities

- `assertions.py`: Input validation functions
- `formatters.py`: Output formatting utilities
- `validators.py`: Data validation helpers

## 7. Contributing

Contributions are welcome! Areas for improvement:

1. Implementation of Criteria 3–7
2. Additional test cases
3. Performance optimizations
4. Documentation improvements

Please ensure that any contributions:

- Follow the existing code structure
- Include appropriate tests
- Update documentation as needed
- Pass all validation checks

## 8. License

The project is licensed under the [CC BY-NC 4.0 License](LICENSE.md).
