from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from pulp import *
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation

class Model:
    def __init__(self, data, income_w1, income_w2, constraints_config=None):
        self.resources_w1 = data[0]
        self.resources_w2 = data[1]
        self.income_w1 = income_w1
        self.income_w2 = income_w2
        
        # Default constraints configuration if not provided
        if constraints_config is None:
            self.constraints_config = [
                {'coef_w1': self.resources_w1[0], 'coef_w2': self.resources_w2[0], 'bound': 60, 'sense': '<='},
                {'coef_w1': self.resources_w1[1], 'coef_w2': self.resources_w2[1], 'bound': 24, 'sense': '<='},
                {'coef_w1': self.resources_w1[2], 'coef_w2': self.resources_w2[2], 'bound': 8, 'sense': '>='}
            ]
        else:
            self.constraints_config = constraints_config
        
        print(f"Model initialized with data: {self.resources_w1, self.resources_w2}, "
              f"income_w1: {income_w1}, income_w2: {income_w2}, constraints: {len(self.constraints_config)}")
    
    def solve(self):
        model = LpProblem("Maximize_Profit", LpMaximize)
        x1 = LpVariable('w1', lowBound=0)
        x2 = LpVariable('w2', lowBound=0)
        model += self.income_w1 * x1 + self.income_w2 * x2 # funkcja celu
        
        # Add constraints dynamically based on configuration
        for i, constraint in enumerate(self.constraints_config):
            coef_w1 = constraint['coef_w1']
            coef_w2 = constraint['coef_w2']
            bound = constraint['bound']
            sense = constraint['sense']
            
            if sense == '<=':
                model += coef_w1 * x1 + coef_w2 * x2 <= bound, f"constraint_{i+1}"
            elif sense == '>=':
                model += coef_w1 * x1 + coef_w2 * x2 >= bound, f"constraint_{i+1}"
            elif sense == '==':
                model += coef_w1 * x1 + coef_w2 * x2 == bound, f"constraint_{i+1}"
        
        model.solve()
        
        # Detect solution type
        solution_type = self.detect_solution_type(x1.varValue, x2.varValue, value(model.objective))
        
        return x1.varValue, x2.varValue, value(model.objective), solution_type
    
    def detect_solution_type(self, x1, x2, obj_value):
        """
        Detect if the optimal solution is a point or a line (infinite solutions).
        Returns: 'point', 'line', or 'unbounded'
        """
        # Check if we have multiple optimal vertices by testing nearby points
        tolerance = 1e-6
        
        # Test if objective function is parallel to a constraint
        # by checking if slightly moving along constraints changes objective
        
        # Find which constraints are active (binding) at the optimal point
        active_constraints = []
        for i, constraint in enumerate(self.constraints_config):
            coef_w1 = constraint['coef_w1']
            coef_w2 = constraint['coef_w2']
            bound = constraint['bound']
            sense = constraint['sense']
            
            # Calculate constraint value at optimal point
            constraint_value = coef_w1 * x1 + coef_w2 * x2
            
            # Check if constraint is active (within tolerance)
            if sense == '<=' and abs(constraint_value - bound) < tolerance:
                active_constraints.append(constraint)
            elif sense == '>=' and abs(constraint_value - bound) < tolerance:
                active_constraints.append(constraint)
            elif sense == '==' and abs(constraint_value - bound) < tolerance:
                active_constraints.append(constraint)
        
        # Check if objective function is parallel to ANY active constraint
        # This works for both: 2+ active constraints OR 1 active constraint
        if len(active_constraints) >= 1:
            obj_coef = [self.income_w1, self.income_w2]
            
            for constraint in active_constraints:
                const_coef = [constraint['coef_w1'], constraint['coef_w2']]
                
                # Check if vectors are parallel (cross product = 0)
                cross_product = obj_coef[0] * const_coef[1] - obj_coef[1] * const_coef[0]
                
                if abs(cross_product) < tolerance:
                    return 'line'
        
        # Check for unbounded solution
        if x1 is None or x2 is None or obj_value is None:
            return 'unbounded'
        
        return 'point'

    def full_plot(self, x1var, x2var, value, solution_type='point'):
        # Wykres ograniczeń
        x = np.linspace(0, 60, 200)
        
        fig = Figure(figsize=(6, 4.5))
        ax = fig.add_subplot(111)
        
        # Plot each constraint dynamically
        constraint_data = []
        for i, constraint in enumerate(self.constraints_config):
            coef_w1 = constraint['coef_w1']
            coef_w2 = constraint['coef_w2']
            bound = constraint['bound']
            sense = constraint['sense']
            
            # Calculate y values for the constraint line
            if coef_w2 != 0:
                y = (bound - coef_w1 * x) / coef_w2
            else:
                y = np.full_like(x, bound if coef_w1 == 0 else 0)
            
            constraint_data.append({'y': y, 'sense': sense})
            label = f"K{i+1}: {coef_w1}*x+{coef_w2}*y{sense}{bound}"
            ax.plot(x, y, label=label)
        
        # Fill feasible region - handle both <= and >= constraints
        # Start with the full upper area
        y_upper = np.full_like(x, 1000)  # Very large number
        y_lower = np.full_like(x, 0)      # Start from 0
        
        for data in constraint_data:
            if data['sense'] == '<=':
                # For <=: feasible region is BELOW the line
                y_upper = np.minimum(y_upper, data['y'])
            elif data['sense'] == '>=':
                # For >=: feasible region is ABOVE the line
                y_lower = np.maximum(y_lower, data['y'])
        
        # The feasible region is where y_lower <= y <= y_upper
        # Only plot where this is valid
        y_fill_lower = np.maximum(y_lower, 0)
        y_fill_upper = np.minimum(y_upper, 100)  # Cap at reasonable value
        
        # Only fill where lower <= upper (valid region)
        valid = y_fill_lower <= y_fill_upper
        if np.any(valid):
            ax.fill_between(x, y_fill_lower, y_fill_upper, where=valid, 
                           alpha=0.3, color='lightgreen', label='Obszar rozwiązań')
        
        # Mark optimal solution differently based on type
        if solution_type == 'line':
            # Find the optimal edge and draw it in red
            ax.scatter(x1var, x2var, color='red', s=100, zorder=5, marker='o', label="Rozwiązanie (prosta)")
            # Add text annotation
            ax.text(x1var, x2var + 0.5, 'Nieskończenie wiele\nrozwiązań optymalnych', 
                   ha='center', fontsize=9, bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        elif solution_type == 'unbounded':
            ax.text(30, 6, 'Problem nieograniczony!', ha='center', fontsize=12, 
                   bbox=dict(boxstyle='round', facecolor='red', alpha=0.7))
        else:
            ax.scatter(x1var, x2var, color='red', s=100, zorder=5, label="Optimum (punkt)")
        
        ax.set_xlim(0, 60)
        ax.set_ylim(0, 12)
        ax.set_xlabel('X1 (W1)')
        ax.set_ylabel('X2 (W2)')
        
        # Update title based on solution type
        if solution_type == 'line':
            title = f"Rozwiązanie: W1 = {x1var:.2f}, W2 = {x2var:.2f}, Wartość = {value:.2f}\n(Nieskończenie wiele rozwiązań optymalnych)"
        elif solution_type == 'unbounded':
            title = f"Problem nieograniczony (brak optymalnego rozwiązania)"
        else:
            title = f"Optimum: W1 = {x1var:.2f}, W2 = {x2var:.2f}, Wartość = {value:.2f}"
        
        ax.set_title(title, fontsize=10)
        ax.legend()
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig('full_plot.png', dpi=100)
        return fig

    def animated_plot(self, x1var, x2var, value, solution_type='point'):
        x = np.linspace(0, 60, 200)
        
        # Build constraints list dynamically
        constraints = []
        constraint_data = []
        for i, constraint in enumerate(self.constraints_config):
            coef_w1 = constraint['coef_w1']
            coef_w2 = constraint['coef_w2']
            bound = constraint['bound']
            sense = constraint['sense']
            
            # Calculate y values for the constraint line
            if coef_w2 != 0:
                y = (bound - coef_w1 * x) / coef_w2
            else:
                y = np.full_like(x, bound if coef_w1 == 0 else 0)
            
            constraint_data.append({'y': y, 'sense': sense})
            label = f"K{i+1}: {coef_w1}*x+{coef_w2}*y{sense}{bound}"
            constraints.append((x, y, label))

        fig = Figure(figsize=(5.5, 4))  # Smaller for better fit in GUI
        ax = fig.add_subplot(111)
        ax.set_xlim(0, 60)
        ax.set_ylim(0, 12)
        ax.set_xlabel('X1 (W1)')
        ax.set_ylabel('X2 (W2)')
        ax.set_title(f"Optimum: W1 = {x1var:.2f}, W2 = {x2var:.2f}, Wartość = {value:.2f}")

        def init():
            ax.clear()
            ax.set_xlim(0, 60)
            ax.set_ylim(0, 12)
            ax.set_xlabel('X1 (W1)')
            ax.set_ylabel('X2 (W2)')
            ax.set_title(f"Optimum: W1 = {x1var:.2f}, W2 = {x2var:.2f}, Wartość = {value:.2f}")
            ax.grid(True, alpha=0.3)
            return []

        def update(frame):
            ax.clear()
            ax.set_xlim(0, 60)
            ax.set_ylim(0, 12)
            ax.set_xlabel('X1 (W1)')
            ax.set_ylabel('X2 (W2)')
            ax.set_title(f"Optimum: W1 = {x1var:.2f}, W2 = {x2var:.2f}, Wartość = {value:.2f}")
            ax.grid(True, alpha=0.3)
            legend_labels = []
            
            # Draw constraints up to current frame
            for i in range(frame+1):
                if i < len(constraints):
                    l, = ax.plot(constraints[i][0], constraints[i][1], label=constraints[i][2])
                    legend_labels.append(constraints[i][2])
            
            # Fill feasible region after all constraints
            if frame >= len(constraints):
                # Handle both <= and >= constraints
                y_upper = np.full_like(x, 1000)
                y_lower = np.full_like(x, 0)
                
                for data in constraint_data:
                    if data['sense'] == '<=':
                        y_upper = np.minimum(y_upper, data['y'])
                    elif data['sense'] == '>=':
                        y_lower = np.maximum(y_lower, data['y'])
                
                y_fill_lower = np.maximum(y_lower, 0)
                y_fill_upper = np.minimum(y_upper, 100)
                
                valid = y_fill_lower <= y_fill_upper
                if np.any(valid):
                    ax.fill_between(x, y_fill_lower, y_fill_upper, where=valid,
                                   alpha=0.3, color='lightgreen')
                    legend_labels.append('Obszar rozwiązań')
            
            # Show optimum after all constraints
            if frame > len(constraints):
                if solution_type == 'line':
                    ax.scatter(x1var, x2var, color='red', s=100, zorder=5, marker='o', label="Rozwiązanie (prosta)")
                    legend_labels.append('Rozwiązanie (prosta)')
                else:
                    ax.scatter(x1var, x2var, color='red', s=100, zorder=5, label="Optimum")
                    legend_labels.append('Optimum')
            
            ax.legend(legend_labels)
            return []

        frames = len(constraints) + 2
        anim = FuncAnimation(fig, update, frames=frames, init_func=init, interval=1000, blit=False, repeat=False)
        fig.tight_layout()
        anim.save('animation.gif', writer='pillow', dpi=80)  # Lower DPI for smaller file
        return fig

if __name__ == '__main__':
    data = [[1.0, 1.0, 4.0], [6.0, 2.0, 1.0]]
    income_w1 = 20.0
    income_w2 = 10.0
    
    # Example with custom constraints configuration
    constraints_config = [
        {'coef_w1': 1.0, 'coef_w2': 6.0, 'bound': 60, 'sense': '<='},
        {'coef_w1': 1.0, 'coef_w2': 2.0, 'bound': 24, 'sense': '<='},
        {'coef_w1': 4.0, 'coef_w2': 1.0, 'bound': 8, 'sense': '>='}
    ]
    
    model = Model(data=data, income_w1=income_w1, income_w2=income_w2, constraints_config=constraints_config)
    x1, x2, obj_value, solution_type = model.solve()
    print(f"Solution type: {solution_type}")
    print(f"W1={x1}, W2={x2}, Objective={obj_value}")
    model.full_plot(x1, x2, obj_value, solution_type)
    model.animated_plot(x1, x2, obj_value, solution_type)