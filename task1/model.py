from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from pulp import *
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation

class Model:
    def __init__(self, data, income_w1, income_w2):
        self.resources_w1 = data[0]
        self.resources_w2 = data[1]
        self.income_w1 = income_w1
        self.income_w2 = income_w2
        print(f"Model initialized with data: {self.resources_w1, self.resources_w2}, "
              f"income_w1: {income_w1}, income_w2: {income_w2}")
    
    def solve(self):
        model = LpProblem("Maximize_Profit", LpMaximize)
        x1 = LpVariable('w1', lowBound=0)
        x2 = LpVariable('w2', lowBound=0)
        model += self.income_w1 * x1 + self.income_w2 * x2 # funkcja celu
        model += self.resources_w1[0] * x1 + self.resources_w2[0] * x2 <= 60  # ograniczenie 1
        model += self.resources_w1[1] * x1 + self.resources_w2[1] * x2 <= 24  # ograniczenie 2
        model += self.resources_w1[2] * x1 + self.resources_w2[2] * x2 >= 8   # ograniczenie 3
        model.solve()
        # print("Status:", LpStatus[model.status])
        # print("Optimal solution:")
        # for v in model.variables():
        #     print(f"  {v.name}: {v.varValue}")
        # print("Objective value:", value(model.objective))
        return x1.varValue, x2.varValue, value(model.objective)

    def full_plot(self, x1var, x2var, value):
        # Wykres ograniczeń
        x = np.linspace(0, 60, 200)
        y1 = (60 - x) / 6
        y2 = (24 - x) / 2
        y3 = 8 - 4*x

        fig = Figure(figsize=(5, 2.5))
        ax = fig.add_subplot(111)
        ax.plot(x, y1, label="K1: x+6y≤60")
        ax.plot(x, y2, label="K2: x+2y≤24")
        ax.plot(x, y3, label="K3: 4x+y≥8")
        y_fill = np.maximum(np.maximum(8 - 4*x, 0), 0)
        ax.fill_between(x, y_fill, np.minimum(y1, y2), alpha=0.3, color='lightgreen', label='Obszar rozwiązań')
        ax.scatter(x1var, x2var, color='red', label="Optimum")
        ax.set_xlim(0, 60)
        ax.set_ylim(0, 12)
        ax.set_xlabel('X1 (W1)')
        ax.set_ylabel('X2 (W2)')
        ax.set_title(f"Optimum: W1 = {x1var}, W2 = {x2var}, Wartość = {value}")
        ax.legend()
        fig.subplots_adjust(bottom=0.2)
        fig.savefig('full_plot.png')
        return fig

    def animated_plot(self, x1var, x2var, value):
        x = np.linspace(0, 60, 200)
        y1 = (60 - x) / 6
        y2 = (24 - x) / 2
        y3 = 8 - 4*x
        constraints = [
            (x, y1, "K1: x+6y≤60"),
            (x, y2, "K2: x+2y≤24"),
            (x, y3, "K3: 4x+y≥8")
        ]

        fig = Figure(figsize=(5, 2.5))
        ax = fig.add_subplot(111)
        ax.set_xlim(0, 60)
        ax.set_ylim(0, 12)
        ax.set_xlabel('X1 (W1)')
        ax.set_ylabel('X2 (W2)')
        ax.set_title(f"Optimum: W1 = {x1var}, W2 = {x2var}, Wartość = {value}")

        lines = []
        fill = None
        optimum = None

        def init():
            ax.clear()
            ax.set_xlim(0, 60)
            ax.set_ylim(0, 12)
            ax.set_xlabel('X1 (W1)')
            ax.set_ylabel('X2 (W2)')
            ax.set_title(f"Optimum: W1 = {x1var}, W2 = {x2var}, Wartość = {value}")
            return []

        def update(frame):
            ax.clear()
            ax.set_xlim(0, 60)
            ax.set_ylim(0, 12)
            ax.set_xlabel('X1 (W1)')
            ax.set_ylabel('X2 (W2)')
            ax.set_title(f"Optimum: W1 = {x1var}, W2 = {x2var}, Wartość = {value}")
            legend_labels = []
            # Draw constraints up to current frame
            for i in range(frame+1):
                if i < len(constraints):
                    l, = ax.plot(constraints[i][0], constraints[i][1], label=constraints[i][2])
                    legend_labels.append(constraints[i][2])
            # Fill feasible region after all constraints
            if frame >= len(constraints):
                y_fill = np.maximum(np.maximum(8 - 4*x, 0), 0)
                ax.fill_between(x, y_fill, np.minimum(y1, y2), alpha=0.3, color='lightgreen')
                legend_labels.append('Obszar rozwiązań')
            # Show optimum after all constraints
            if frame > len(constraints):
                ax.scatter(x1var, x2var, color='red', label="Optimum")
                legend_labels.append('Optimum')
            ax.legend(legend_labels)
            return []

        frames = len(constraints) + 2
        anim = FuncAnimation(fig, update, frames=frames, init_func=init, interval=1000, blit=False, repeat=False)
        fig.subplots_adjust(bottom=0.2)
        anim.save('animation.gif', writer='pillow')
        return fig

if __name__ == '__main__':
    data = [[1.0, 1.0, 4.0], [6.0, 2.0, 1.0]]
    income_w1 = 20.0
    income_w2 = 10.0
    model = Model(data=data, income_w1=income_w1, income_w2=income_w2)
    solution = model.solve()
    model.full_plot(*solution)
    model.animated_plot(*solution)