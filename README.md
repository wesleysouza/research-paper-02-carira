# Carira: A Trade-off-Aware Placement Strategy for Resilient Smart City Applications

[![Conference](https://img.shields.io/badge/Paper_Accepted-IEEE_ISC2_2026-blue.svg)](https://dei.fe.up.pt/ieee-isc2-2026/)

## Overview

This repository contains the source code, datasets, and analysis scripts for the paper **"Carira: A Trade-off-Aware Placement Strategy for Resilient Smart City Applications"**, accepted at the [IEEE ISC2 2026](https://dei.fe.up.pt/ieee-isc2-2026/) conference.

The project leverages the [EdgeSimPy](https://github.com/EdgeSimPy/EdgeSimPy) simulator to evaluate placement strategies in edge computing environments, focusing on balancing trade-offs and ensuring resilience for smart city applications. 

## Installation

> **Note:** This project is built on top of the [EdgeSimPy](https://github.com/EdgeSimPy/EdgeSimPy) simulator. You will need to install a specific version of it directly from its GitHub repository to run our custom mobility models.

### 1. Install Required Libraries

To run the simulations, you need to install the required Python packages. 

Run the following commands in your terminal:

`pip install -q git+https://github.com/EdgeSimPy/EdgeSimPy.git`

`pip install torch openpyxl matplotlib seaborn jupyter`

### 2. Configure the Custom Mobility Model

This project relies on a custom Random Waypoint mobility model that must be integrated directly into the installed EdgeSimPy library. Follow these steps to configure it:

1. Locate the `random_waypoint_mobility.py` file provided in this project (inside the `mobility_model/` directory).
2. Copy this file into your Python environment's EdgeSimPy `mobility_models` directory. The path typically looks like this:
   `[your_virtual_env_directory]/lib/python3.x/site-packages/edge_sim_py/components/mobility_models/`
3. Open the `__init__.py` file located in that same `mobility_models` directory.
4. Add the import statement for the new model so it looks like the example below:

```python
# User mobility models
from .pathway import pathway
from .random_mobility import random_mobility
from .random_waypoint_mobility import random_waypoint_mobility # <-- Add this line
```

## Running the Simulation

Once the dependencies are installed and the mobility model is properly configured in EdgeSimPy, you can execute the simulation by running the main script:

`python main.py`

## Results and Analysis

After the simulation completes, you can analyze the generated data and visualize the trade-offs using the provided Jupyter Notebook.

1. Start Jupyter Notebook in your terminal:
   `jupyter notebook`
2. Open the `nb_results.ipynb` file in your browser and run the cells to generate the evaluation graphs and metrics.

---
*For more details on the methodology and findings, please refer to the accepted IEEE ISC2 2026 paper.*