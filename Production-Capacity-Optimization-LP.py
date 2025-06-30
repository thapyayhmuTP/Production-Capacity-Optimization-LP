# Model Implementation

#Loading Data from csv

import csv
import pandas as pd

# Load products
products = []
with open('products.csv', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        products.append({
            'id': int(row['product_id']),
            'name': row['name'],
            'profit': float(row['profit']),
            'material': row['material'],
            'material_qty': float(row['material_qty']),
            'time_per_unit': float(row['time_per_unit']),
            'line': row['line'],
            'demand': int(row['demand'])
        })

# Load material availability
material_available = {}
with open('material_limits.csv', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        material_available[row['material']] = float(row['available'])

# Load line capacity
line_capacity = {}
with open('line_capacity.csv', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        line_capacity[row['line']] = float(row['capacity_minutes'])

#Defining Model
from ortools.linear_solver import pywraplp

# Create solver
solver = pywraplp.Solver.CreateSolver("GLOP")

# Create variables
x = {}
for p in products:
    x[p['id']] = solver.NumVar(0, solver.infinity(), f"x_{p['id']}")

# Objective
solver.Maximize(solver.Sum(p['profit'] * x[p['id']] for p in products))

# Raw material constraints
for material in material_available:
    solver.Add(
        sum(p['material_qty'] * x[p['id']] for p in products if p['material'] == material)
        <= material_available[material]
    )

# Line capacity constraints
for line in line_capacity:
    solver.Add(
        sum(p['time_per_unit'] * x[p['id']] for p in products if p['line'] == line)
        <= line_capacity[line]
    )

# Demand constraints
for p in products:
    solver.Add(x[p['id']] <= p['demand'])


#Solve
status = solver.Solve()
if status == pywraplp.Solver.OPTIMAL:
    total_profit = 0
    print("\n Original Model's Optimal Plan:")
    print(f"{'Variable':<8} {'Product':<22} {'Optimal':>12} {'Profit':>12} {'Actual':>10} {'Unused':>10} {'Unused %':>10}")

    for p in products:
        pid = p['id']
        var = f"x{pid}"
        product = p['name']
        optimal = x[pid].solution_value()
        profit = optimal * p['profit']
        actual = p['demand']
        unused = actual - optimal
        unused_pct = (unused / actual) * 100 if actual > 0 else 0

        total_profit += profit

        print(f"{var:<8} {product:<22} {optimal:12,.2f} ${profit:11,.2f} {actual:10,.0f} {unused:10,.2f} {unused_pct:9.2f}%")

    print(f"\n{'':<8} {'Total Profit:':<22} {'':>12} ${total_profit:11,.2f}")
else:
    print("No optimal solution found.")

#For models comparison
x_original_values = {}
for p in products:
    pid = p['id']
    x_original_values[pid] = x[pid].solution_value()

# # Model Extension

#Load extended csv

# Load material perishability status and cost
products_ext = {}
with open('products_ext.csv', newline='') as f:
    reader = csv.DictReader(f)
    products_ext = {
        row['name'].strip(): {
            'perishable': row['perishable'].strip().lower(),  # yes/no
            'Cost': float(row['cost'])
        }
        for row in reader
    }
for p in products:
    ext = products_ext.get(p['name'])
    if ext:
        p['perishable'] = ext['perishable']
        p['Cost'] = ext['Cost']

#Defining Model
from ortools.linear_solver import pywraplp

# Create solver
solver = pywraplp.Solver.CreateSolver("GLOP")

# Create variables
x = {}
for p in products:
    x[p['id']] = solver.NumVar(0, solver.infinity(), f"x_{p['id']}")

# Build Objective: total profit
total_profit = solver.Sum(p['profit'] * x[p['id']] for p in products)


# Spoilage penalty for perishable products
leftover = {}
spoilage_penalty_terms = []

for p in products:
    if p['perishable'].strip().lower() == 'yes' and 'Cost' in p:
        material = p['material'].strip().lower()
        product_id = p['id']

        # Define leftover variable
        var_name = f"{material}leftover{product_id}"
        leftover_var = solver.NumVar(0, solver.infinity(), var_name)
        leftover[(material, product_id)] = leftover_var

        # Add constraint: leftover = available - used
        used = p['material_qty'] * x[product_id]
        solver.Add(leftover_var == material_available[material] - used)

        # Add spoilage cost term
        spoilage_penalty_terms.append(p['Cost'] * leftover_var)

# Combine spoilage penalty
spoilage_penalty = solver.Sum(spoilage_penalty_terms)

# Objective: maximize weighted profit minus weighted spoilage penalty
objective = total_profit - ((0.05) * spoilage_penalty)
solver.Maximize(objective)

# Raw material constraints
for material in material_available:
    solver.Add(
        sum(
            p['material_qty'] * x[p['id']]
            for p in products if p['material'].strip().lower() == material
        ) <= material_available[material]
    )

# Line capacity constraints
for line in line_capacity:
    solver.Add(
        sum(
            p['time_per_unit'] * x[p['id']]
            for p in products if p['line'] == line
        ) <= line_capacity[line]
    )

# Demand constraints
for p in products:
    solver.Add(x[p['id']] <= p['demand'])

# Minimum production for perishables (5% of demand)
min_ratio = 0.05
for p in products:
    if p['perishable'].strip().lower() == 'yes':
        solver.Add(x[p['id']] >= min_ratio * p['demand'])

#Solve
status = solver.Solve()

if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
    total_profit = 0
    print("\n\n Extended Model's Optimal Plan:")
    print(f"{'Variable':<10} {'Product':<22} {'Optimal Production':>18} {'Profit':>12}")
    
    for p in products:
        pid = p['id']
        var = f"x_{pid}"
        product = p['name']
        optimal = x[pid].solution_value()
        profit = optimal * p['profit']
        total_profit += profit
        
        print(f"{var:<10} {product:<22} {optimal:18,.2f} ${profit:11,.2f}")
    
    print(f"\n{'':<10} {'Total Profit (from production):':<35} {'':>18} ${total_profit:11,.2f}")
    
    # --- Dynamically detect perishable materials from enriched products list ---
    perishable_materials = set(
        p['material']
        for p in products
        if p.get('perishable', '').lower() == 'yes'
    )

    # --- Raw Material Spoilage (Only for perishable materials) ---
    print("\n\n Perishable Raw Material Spoilage Summary:")
    print(f"{'Material':<15} {'Available':>12} {'Used':>12} {'Leftover (Spoiled)':>20}")
    print("-" * 60)

    total_spoilage = 0  # in units (litres, kg, etc.)

    for material, available_qty in material_available.items():
        if material not in perishable_materials:
            continue  # Skip non-perishable materials

        used_qty = sum(
            x[p['id']].solution_value() * p['material_qty']
            for p in products if p['material'] == material
        )
        leftover_qty = available_qty - used_qty
        total_spoilage += leftover_qty

        print(f"{material:<15} {available_qty:12,.2f} {used_qty:12,.2f} {leftover_qty:20,.2f}")

    print("-" * 60)
    print(f"{'':<42} {'Total Spoiled (Perishable) Amount:':<18} {total_spoilage:,.2f} units")

    # --- Apply spoilage penalty (5% of spoiled perishable materials only)
    spoilage_penalty_ratio = 0.05
    spoilage_cost = total_spoilage * spoilage_penalty_ratio
    extended_profit = total_profit - spoilage_cost

    print(f"\n{'':<10} {'Extended Total Profit (after 5% spoilage penalty):':<50} ${extended_profit:12,.2f}")

else:
    print("No feasible or optimal solution found.")