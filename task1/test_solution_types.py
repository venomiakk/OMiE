"""
Test różnych typów rozwiązań programowania liniowego
"""

from model import Model

print("="*70)
print("TEST 1: Rozwiązanie punktowe (standardowe zadanie Szkiełko)")
print("="*70)

data1 = [[1, 1, 4], [6, 2, 1]]
income_w1 = 20
income_w2 = 10
constraints1 = [
    {'coef_w1': 1, 'coef_w2': 6, 'bound': 60, 'sense': '<='},
    {'coef_w1': 1, 'coef_w2': 2, 'bound': 24, 'sense': '<='},
    {'coef_w1': 4, 'coef_w2': 1, 'bound': 8, 'sense': '>='}
]

model1 = Model(data1, income_w1, income_w2, constraints1)
x1, x2, obj, sol_type = model1.solve()
print(f"Typ rozwiązania: {sol_type}")
print(f"W1 = {x1:.2f}, W2 = {x2:.2f}, Wartość = {obj:.2f}")
print()

print("="*70)
print("TEST 2: Nieskończenie wiele rozwiązań (funkcja celu równoległa)")
print("="*70)

# Funkcja celu: 2x + 4y -> max
# Ograniczenie 1: x + 2y <= 10 (równoległe do funkcji celu!)
# Ograniczenie 2: x <= 8

data2 = [[1, 1], [2, 0]]  # Współczynniki nie używane gdy są w constraints
income_w1_2 = 2
income_w2_2 = 4
constraints2 = [
    {'coef_w1': 1, 'coef_w2': 2, 'bound': 10, 'sense': '<='},  # Równoległe!
    {'coef_w1': 1, 'coef_w2': 0, 'bound': 8, 'sense': '<='},
]

model2 = Model(data2, income_w1_2, income_w2_2, constraints2)
x1_2, x2_2, obj2, sol_type2 = model2.solve()
print(f"Typ rozwiązania: {sol_type2}")
print(f"W1 = {x1_2:.2f}, W2 = {x2_2:.2f}, Wartość = {obj2:.2f}")
print()

print("="*70)
print("TEST 3: Inny przykład z nieskończonością rozwiązań")
print("="*70)

# Funkcja celu: 3x + 6y -> max
# Ograniczenie 1: x + 2y <= 12 (równoległe! współczynniki 1:2 = 3:6)
# Ograniczenie 2: x >= 0, y >= 0 (automatyczne)

data3 = [[1, 1], [2, 0]]
income_w1_3 = 3
income_w2_3 = 6
constraints3 = [
    {'coef_w1': 1, 'coef_w2': 2, 'bound': 12, 'sense': '<='},  # Równoległe!
    {'coef_w1': 1, 'coef_w2': 0, 'bound': 10, 'sense': '<='},
]

model3 = Model(data3, income_w1_3, income_w2_3, constraints3)
x1_3, x2_3, obj3, sol_type3 = model3.solve()
print(f"Typ rozwiązania: {sol_type3}")
print(f"W1 = {x1_3:.2f}, W2 = {x2_3:.2f}, Wartość = {obj3:.2f}")
print()

print("="*70)
print("INSTRUKCJA: Jak stworzyć nieskończenie wiele rozwiązań w GUI")
print("="*70)
print("""
Aby otrzymać nieskończenie wiele rozwiązań optymalnych, funkcja celu 
musi być równoległa do jednego z ograniczeń.

PRZYKŁAD 1:
- Zysk W1: 2
- Zysk W2: 4
- Współczynniki:
  W1: [1, 1]
  W2: [2, 0]
- Ograniczenia:
  K1: 1*W1 + 2*W2 <= 10  (to jest równoległe do 2*W1 + 4*W2!)
  K2: 1*W1 + 0*W2 <= 8

PRZYKŁAD 2:
- Zysk W1: 3
- Zysk W2: 6
- Współczynniki:
  W1: [1, 1]
  W2: [2, 0]
- Ograniczenia:
  K1: 1*W1 + 2*W2 <= 12  (równoległe do 3*W1 + 6*W2!)
  K2: 1*W1 + 0*W2 <= 10

WARUNEK RÓWNOLEGŁOŚCI:
Jeśli funkcja celu to: a*x + b*y
I ograniczenie to: c*x + d*y <= e
To są równoległe gdy: a/b = c/d (lub a*d = b*c)
""")
print("="*70)
