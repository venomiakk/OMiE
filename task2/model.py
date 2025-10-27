class Model:
    def __init__(self):
        # Initialize model parameters
        #-3x1 - 2x2 -> min
        #
        #       4x2 <=16
        # 2x1 +  x2 <= 8
        # 2x1 + 2x2 <=14
        #
        #
        self.x1 = [0 , 2 , 2]
        self.x2 = [4, 1, 2]
        self.b = [16, 8, 14]
        self.c = [-3, -2]
        self.cb = [0, 0, 0]
        self.base = [2,3,4] # Indeksy zmiennych bazowych
        
        # ilosc ograniczen
        self.m = len(self.b)
        # ilosc zmiennych
        self.n = len(self.c)

    def create_coefficients_matrix(self):
        self.cof_matrix = []
        for i in range(len(self.x1)):
            row = []
            for j in range(len(self.x2)):
                if(i==j):
                    row.append(1)
                else:
                    row.append(0)
            self.cof_matrix.append(row)

    def create_matrix(self):
        self.matrix = []
        for i in range(self.m):
            row = []
            for j in range(self.n + self.m):
                if j == 0:
                    row.append(self.x1[i])
                elif j == 1:
                    row.append(self.x2[i])
                elif j - self.n == i:
                    row.append(1)
                else:
                    row.append(0)
                    
            self.matrix.append(row)

    def find_pivot(self, matrix):

        # Krok 1: Oblicz zj - cj dla każdej kolumny
        zj_cj = []
        for j in range(self.n + self.m):  # dla wszystkich zmiennych
            zj = 0
            # zj = suma(cb[i] * a[i][j]) dla wszystkich wierszy w bazie
            for i in range(self.m):
                zj += self.cb[i] * matrix[i][j]
            
            # cj dla zmiennych decyzyjnych lub 0 dla zmiennych slackowych
            if j < self.n:
                cj = self.c[j]
            else:
                cj = 0
            
            zj_cj.append(zj - cj)
        
        # Krok 2: Znajdź kolumnę pivotującą
        # Dla minimalizacji: wybierz największe dodatnie zj - cj
        pivot_col = None
        max_zj_cj = 0
        
        for j in range(len(zj_cj)):
            if zj_cj[j] > max_zj_cj:
                max_zj_cj = zj_cj[j]
                pivot_col = j
        
        # Jeśli wszystkie zj - cj <= 0, to rozwiązanie jest optymalne
        if pivot_col is None:
            return None, None
        
        # Krok 3: Oblicz ratios (b[i] / a[i][pivot_col]) i znajdź wiersz pivotujący
        pivot_row = None
        min_ratio = float('inf')
        
        for i in range(self.m):
            # Element w kolumnie pivotującej
            aij = matrix[i][pivot_col]
            
            # Ratio jest obliczane tylko dla dodatnich elementów
            if aij > 0:
                ratio = self.b[i] / aij
                if ratio < min_ratio:
                    min_ratio = ratio
                    pivot_row = i
        
        # Jeśli nie ma dodatnich elementów, problem jest nieograniczony
        if pivot_row is None:
            return None, None
        
        return pivot_row, pivot_col
    
    def pivot_operation(self, matrix, pivot_row, pivot_col):
        pivot_element = matrix[pivot_row][pivot_col]
        
        # Krok 1: Podziel wiersz pivotujący przez element pivotujący
        new_matrix = []
        pivot_row_new = []
        for j in range(len(matrix[pivot_row])):
            pivot_row_new.append(matrix[pivot_row][j] / pivot_element)
        
        # Krok 2: Zaktualizuj pozostałe wiersze
        for i in range(self.m):
            if i == pivot_row:
                new_matrix.append(pivot_row_new)
            else:
                new_row = []
                multiplier = matrix[i][pivot_col]
                for j in range(len(matrix[i])):
                    new_value = matrix[i][j] - multiplier * pivot_row_new[j]
                    new_row.append(new_value)
                new_matrix.append(new_row)
        
        # Krok 3: Zaktualizuj wartości b
        new_b = []
        b_pivot = self.b[pivot_row] / pivot_element
        for i in range(self.m):
            if i == pivot_row:
                new_b.append(b_pivot)
            else:
                new_b.append(self.b[i] - matrix[i][pivot_col] * b_pivot)
        self.b = new_b
        
        # Krok 4: Zaktualizuj bazę i cb
        self.base[pivot_row] = pivot_col
        if pivot_col < self.n:
            self.cb[pivot_row] = self.c[pivot_col]
        else:
            self.cb[pivot_row] = 0
        
        return new_matrix
    
    def solve(self):
        """
        Rozwiązuje problem programowania liniowego metodą simplex.
        
        Returns:
            tuple: (x1, x2, obj_value, solution_type)
        """
        # Inicjalizacja macierzy
        self.create_matrix()
        matrix = self.matrix
        
        max_iterations = 100
        iteration = 0
        
        print("Rozpoczynam rozwiązywanie metodą simplex...")
        print(f"Początkowa macierz:")
        self.print_tableau(matrix)
        
        while iteration < max_iterations:
            iteration += 1
            print(f"\n--- Iteracja {iteration} ---")
            
            # Znajdź element pivotujący
            pivot_row, pivot_col = self.find_pivot(matrix)
            
            # Sprawdź warunki zakończenia
            if pivot_row is None or pivot_col is None:
                print("Rozwiązanie optymalne znalezione!")
                break
            
            print(f"Element pivotujący: wiersz {pivot_row}, kolumna {pivot_col}")
            
            # Wykonaj operację pivotowania
            matrix = self.pivot_operation(matrix, pivot_row, pivot_col)
            
            print(f"Macierz po pivotowaniu:")
            self.print_tableau(matrix)
        
        if iteration >= max_iterations:
            print("Osiągnięto maksymalną liczbę iteracji!")
            return None, None, None, "MAX_ITERATIONS"
        
        # Odczytaj rozwiązanie
        x = [0] * (self.n + self.m)
        for i in range(self.m):
            if self.base[i] < len(x):
                x[self.base[i]] = self.b[i]
        
        x1 = x[0] if self.n > 0 else 0
        x2 = x[1] if self.n > 1 else 0
        
        # Oblicz wartość funkcji celu
        obj_value = sum(self.c[j] * x[j] for j in range(self.n))
        
        print(f"\nRozwiązanie:")
        print(f"x1 = {x1:.4f}")
        print(f"x2 = {x2:.4f}")
        print(f"Wartość funkcji celu = {obj_value:.4f}")
        
        return x1, x2, obj_value, "OPTIMAL"
    
    def print_tableau(self, matrix):
        """Wyświetla tablicę simplex."""
        print("\nBaza | ", end="")
        for j in range(self.n + self.m):
            print(f"x{j+1:2d}  ", end="")
        print(" | b")
        print("-" * (8 + 6 * (self.n + self.m) + 8))
        
        for i in range(self.m):
            print(f"x{self.base[i]+1:2d}   | ", end="")
            for j in range(len(matrix[i])):
                print(f"{matrix[i][j]:5.2f} ", end="")
            print(f"| {self.b[i]:5.2f}")
    
if __name__ == '__main__':
    model = Model()
    x1, x2, obj_value, solution_type = model.solve()
    print(f"Solution type: {solution_type}")
