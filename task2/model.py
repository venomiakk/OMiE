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
        
        # ilosc ograniczen
        self.m = len(self.b)
        # ilosc zmiennych
        self.n = len(self.c)
        
        # Początkowa baza: zmienne slack (indeksy od n do n+m-1)
        self.base = [self.n + i for i in range(self.m)]
        # Początkowe cb: wszystkie 0 (zmienne slack mają koszt 0)
        self.cb = [0.0] * self.m
        
        # Typ optymalizacji: 'min' lub 'max'
        self.optimization_type = 'min'
        
        # Przechowuje oryginalne współczynniki c przed przekształceniem
        self.c_original = self.c.copy()

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
        """
        Tworzy macierz ograniczeń dla algorytmu simplex.
        Macierz ma wymiary m x (n+m), gdzie:
        - pierwsze n kolumn to współczynniki zmiennych decyzyjnych
        - kolejne m kolumn to zmienne slack (macierz jednostkowa)
        """
        self.matrix = []
        for i in range(self.m):
            row = []
            # Dodaj współczynniki zmiennych decyzyjnych
            for j in range(self.n):
                var_name = f"x{j+1}"
                if hasattr(self, var_name):
                    var_list = getattr(self, var_name)
                    if i < len(var_list):
                        row.append(var_list[i])
                    else:
                        row.append(0)
                else:
                    row.append(0)
            
            # Dodaj zmienne slack (macierz jednostkowa)
            for j in range(self.m):
                if j == i:
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
        
        print(f"zj - cj: {[f'{val:.2f}' for val in zj_cj]}")
        
        # Krok 2: Znajdź kolumnę pivotującą
        # Dla minimalizacji: wybierz najbardziej UJEMNE cj - zj
        # Czyli wybierz najbardziej DODATNIE zj - cj
        # (ujemne cj-zj oznacza że zwiększenie zmiennej zmniejszy koszt)
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
        
        print(f"Kolumna pivotująca: {pivot_col} (x{pivot_col+1})")
        print(f"Ratios:")
        
        for i in range(self.m):
            # Element w kolumnie pivotującej
            aij = matrix[i][pivot_col]
            
            # Ratio jest obliczane tylko dla dodatnich elementów
            if aij > 0:
                ratio = self.b[i] / aij
                print(f"  Wiersz {i}: b[{i}]={self.b[i]:.2f} / a[{i}][{pivot_col}]={aij:.2f} = {ratio:.2f}")
                if ratio < min_ratio:
                    min_ratio = ratio
                    pivot_row = i
            else:
                print(f"  Wiersz {i}: a[{i}][{pivot_col}]={aij:.2f} <= 0, pominięto")
        
        # Jeśli nie ma dodatnich elementów, problem jest nieograniczony
        if pivot_row is None:
            print("UWAGA: Nie znaleziono dodatniego elementu - problem nieograniczony!")
            return -1, pivot_col
        
        print(f"Wybrany wiersz: {pivot_row} (min ratio = {min_ratio:.2f})")
        
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
        Algorytm ZAWSZE rozwiązuje problem MINIMALIZACJI.
        Dla maksymalizacji: mnoży współczynniki przez -1, rozwiązuje jako min, mnoży wynik przez -1.
        
        Returns:
            tuple: (x1, x2, obj_value, solution_type)
        """
        # Zachowaj oryginalne wartości c i cb
        original_c = self.c.copy()
        original_cb = self.cb.copy()
        original_base = self.base.copy()
        
        # POPRAWKA: Upewnij się że cb jest poprawnie ustawione dla początkowej bazy
        for i in range(self.m):
            if self.base[i] < self.n:
                # Zmienna decyzyjna w bazie
                self.cb[i] = self.c[self.base[i]]
            else:
                # Zmienna slack w bazie
                self.cb[i] = 0
        
        # Przekształć funkcję celu jeśli to MAKSYMALIZACJA
        if self.optimization_type == 'max':
            print("Przekształcam problem maksymalizacji do minimalizacji...")
            print(f"Oryginalne współczynniki c: {original_c}")
            # Mnożymy przez -1 aby zamienić max na min
            self.c = [-c for c in original_c]
            print(f"Przekształcone współczynniki c: {self.c}")
            # Zaktualizuj cb dla zmiennych bazowych
            for i in range(self.m):
                if self.base[i] < self.n:
                    self.cb[i] = self.c[self.base[i]]
                else:
                    self.cb[i] = 0
        
        # Inicjalizacja macierzy
        self.create_matrix()
        matrix = self.matrix

        # przygotuj miejsce na zapis iteracji (stringi tablic)
        self.iteration_tableaus = []
        
        max_iterations = 100
        iteration = 0
        
        print("Rozpoczynam rozwiązywanie metodą simplex (MINIMALIZACJA)...")
        print(f"Typ optymalizacji wybrany przez użytkownika: {self.optimization_type}")
        print(f"Współczynniki c (dla minimalizacji): {self.c}")
        print(f"Początkowa baza: {self.base} (cb={self.cb})")
        print(f"Początkowa macierz:")
        self.print_tableau(matrix)
        # zapisz początkową tablicę
        try:
            self.iteration_tableaus.append(self.tableau_to_string(matrix))
        except Exception:
            # w razie problemów z konwersją ignoruj
            pass
        
        while iteration < max_iterations:
            iteration += 1
            print(f"\n--- Iteracja {iteration} ---")
            
            # Znajdź element pivotujący
            pivot_row, pivot_col = self.find_pivot(matrix)
            
            # Sprawdź warunki zakończenia
            if pivot_row is None or pivot_col is None:
                print("Rozwiązanie optymalne znalezione!")
                break
            if pivot_row == -1:
                print("Problem jest nieograniczony (UNBOUNDED)!")
                # Przywróć oryginalne wartości
                self.c = original_c
                self.cb = original_cb
                return None, None, None, "UNBOUNDED"
            
            print(f"Element pivotujący: wiersz {pivot_row}, kolumna {pivot_col}")
            
            # Wykonaj operację pivotowania
            matrix = self.pivot_operation(matrix, pivot_row, pivot_col)
            
            print(f"Macierz po pivotowaniu:")
            self.print_tableau(matrix)
            # zapisz tablicę po pivotowaniu
            try:
                self.iteration_tableaus.append(self.tableau_to_string(matrix))
            except Exception:
                pass
        
        if iteration >= max_iterations:
            print("Osiągnięto maksymalną liczbę iteracji!")
            # Przywróć oryginalne wartości
            self.c = original_c
            self.cb = original_cb
            return None, None, None, "MAX_ITERATIONS"
        
        # Odczytaj rozwiązanie
        x = [0] * (self.n + self.m)
        for i in range(self.m):
            if self.base[i] < len(x):
                x[self.base[i]] = self.b[i]
        
        x1 = x[0] if self.n > 0 else 0
        x2 = x[1] if self.n > 1 else 0

        # Oblicz wartość funkcji celu używając przekształconych współczynników
        obj_value = sum(self.c[j] * x[j] for j in range(self.n))
        
        # Jeśli to była maksymalizacja, przekształć wynik z powrotem
        if self.optimization_type == 'max':
            obj_value = -obj_value
            print(f"\nPrzekształcam wynik z minimalizacji do maksymalizacji...")
            print(f"Wartość funkcji celu (po przekształceniu): {obj_value:.4f}")

        # Zapisz wektor rozwiązania i wartość celu w obiekcie (dla GUI)
        self.solution_vector = x
        self.solution_obj = obj_value
        
        # Przywróć oryginalne wartości c i cb
        self.c = original_c
        self.cb = original_cb
        
        print(f"\nRozwiązanie końcowe:")
        print(f"x1 = {x1:.4f}")
        print(f"x2 = {x2:.4f}")
        if self.optimization_type == 'max':
            print(f"Wartość funkcji celu (maksymalizacja) = {obj_value:.4f}")
        else:
            print(f"Wartość funkcji celu (minimalizacja) = {obj_value:.4f}")
        
        return x1, x2, obj_value, "OPTIMAL"
    
    def print_tableau(self, matrix):
        """Wyświetla tablicę simplex."""
        print("\nBaza | cb  |", end="")
        for j in range(self.n + self.m):
            print(f" x{j+1:2d}  ", end="")
        print(" | b")
        print("-" * (13 + 6 * (self.n + self.m) + 8))
        
        for i in range(self.m):
            base_var = self.base[i]
            print(f"x{base_var+1:2d}  | {self.cb[i]:4.1f} |", end="")
            for j in range(len(matrix[i])):
                print(f" {matrix[i][j]:5.2f}", end="")
            print(f" | {self.b[i]:6.2f}")
        
        # Oblicz i wyświetl wiersz zj-cj
        print("-" * (13 + 6 * (self.n + self.m) + 8))
        print("zj-cj|     |", end="")
        for j in range(self.n + self.m):
            zj = sum(self.cb[i] * matrix[i][j] for i in range(self.m))
            cj = self.c[j] if j < self.n else 0
            print(f" {zj-cj:5.2f}", end="")
        print(" |")

    def tableau_to_string(self, matrix):
        """Zwraca reprezentację tablicy simplex jako string (użyteczne do GUI)."""
        lines = []
        header = []
        header.append("Baza | cb  |")
        for j in range(self.n + self.m):
            header.append(f" x{j+1:2d}  ")
        header.append(" | b")
        lines.append("".join(header))
        sep = "-" * (13 + 6 * (self.n + self.m) + 8)
        lines.append(sep)

        for i in range(self.m):
            base_var = self.base[i]
            row = f"x{base_var+1:2d}  | {self.cb[i]:4.1f} |"
            for j in range(len(matrix[i])):
                row += f" {matrix[i][j]:5.2f}"
            row += f" | {self.b[i]:6.2f}"
            lines.append(row)

        lines.append(sep)
        zj_row = "zj-cj|     |"
        for j in range(self.n + self.m):
            zj = sum(self.cb[i] * matrix[i][j] for i in range(self.m))
            cj = self.c[j] if j < self.n else 0
            zj_row += f" {zj-cj:5.2f}"
        zj_row += " |"
        lines.append(zj_row)

        return "\n".join(lines)
    
if __name__ == '__main__':
    model = Model()
    x1, x2, obj_value, solution_type = model.solve()
    print(f"Solution type: {solution_type}")
