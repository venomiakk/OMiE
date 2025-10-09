import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import linprog

# Funkcja celu: max 20x1 - 10x2 → w scipy minimalizujemy, więc zmieniamy znaki
c = [-20, -10]
A = [[1, 6],
     [1, 2],
     [4, 1]]
b = [60, 24, -8]

res = linprog(c, A_ub=A, b_ub=b, bounds=(0, None))
print(res)

# Wykres ograniczeń
x = np.linspace(0, 60, 200)
y1 = (60 - x) / 6        # -x + 6y <= 60 → y <= (60 + x)/6
y2 = (24 - x) / 2        # x + 2y <= 24 → y <= (24 - x)/2
y3 = 8 - 4*x              # 4x + y >= 8 → y >= 8 - 4x

plt.plot(x, y1, label="K1: x+6y≤60")
plt.plot(x, y2, label="K2: x+2y≤24")
plt.plot(x, y3, label="K3: 4x+y≥8")

# Wypełnienie obszaru dopuszczalnego (przybliżone)
y_fill = np.maximum(np.maximum(8 - 4*x, 0), 0)
plt.fill_between(x, y_fill, np.minimum(y1, y2), alpha=0.3, color='lightgreen')

plt.scatter(res.x[0], res.x[1], color='red', label="Optimum")
plt.xlabel("x1 (W1)")
plt.ylabel("x2 (W2)")
plt.xlim(0, 60)
plt.ylim(0, 12)
plt.legend()
plt.grid(True)
plt.show()
