# Production-Capacity-Optimization-LP
A linear programming model to optimize production capacities using Python and Google OR-Tools. Includes model extension for spoilage costs and comparison of optimal profit outcomes.

## Problem Statement
The company produces a range of goods across four production lines, each with defined time and material constraints. The objective is to **maximize total profit** by selecting the optimal production mix.
Two models are presented:
- **Original Model**: Focuses on pure profit maximization using basic cost and capacity constraints.
- **Extended Model**: Introduces a spoilage cost function for unused perishable materials to better reflect operational risk.

---

## Dataset Overview

Located in `/Data/` folder:
- `products.csv` – Profit and resource requirements for each product  
- `products_ext.csv` – Includes spoilage cost and perishability flags  
- `material_limits.csv` – Available quantity for each raw material  
- `line_capacity.csv` – Total working time per production line

---

## Model Formulation

### Objective
Maximize profit:
- **Original**: Profit = Revenue – Labor and Material Costs
- **Extended**: Profit = Revenue – Labor – Material – Spoilage Penalty

### Constraints
- Resource availability (raw materials)
- Labor time per production line
- Binary production status (product is either produced or not)
- Spoilage cost applied only to perishable items

---

## Python Implementation

The model is implemented in Python using:

- `ortools.linear_solver` (Google OR-Tools)
- Clean modular structure with:
  - `original_model()` – for baseline production planning
  - `extended_model()` – with perishability logic

---

## Results Summary

| Model           | Total Profit | Highlights                                                                 |
|----------------|--------------|----------------------------------------------------------------------------|
| Original        | $928,900.00  | Selected only the most profitable products and fully utilized resources    |
| Extended        | $838,342.71  | Included spoilage penalty on unused perishable materials (5% of leftover)  |

### Original Model
- Focused purely on maximizing profit
- Produced high-return items like **Full Cream Milk**, **Mineral Water**, **Pastries**, **Cookies**, and **Dry Sweets**
- Many low-profit or high-waste products (e.g., juices, bread) were not selected
- Result: Maximum profit but **zero consideration of spoilage**

### Extended Model
- Added a **5% spoilage penalty** for unused *perishable* raw materials (milk, orange, grape, apple)
- Included some previously ignored items (e.g., small production of juices, yogurt, cheese)
- Total spoiled material: **1,504,062.50 units**, leading to a penalty of **$75,203.12**
- Despite a lower total profit, the model reflects **more sustainable and risk-aware** planning

The extended model still favored products like **Full Cream Milk**, **Mineral Water**, and **Pastries**, but also diversified production to reduce spoilage and make better use of perishable inventory.

---

## Files Included

- `Production-Capacity-Optimization-LP.py` – Python script with full model logic
- `/Data/` – All input CSV files

---

## Reference

This project is based on the research paper:

Al-Mashhadani, A. K., Salman, M. S., & Abdul Ameer, R. Y. (2024).  
*Using the linear programming model in determining the potential production capacities by employing the parametric programming method.* 
Journal of Al-Qadisiyah for Computer Science and Mathematics, 16(4), 33–42.  
[https://doi.org/10.29304/jqcsm.2024.16.41799](https://doi.org/10.29304/jqcsm.2024.16.41799)

---

## Author

Tha Pyay Hmu
