

class TransportOptimization:
    def __init__(self, quantity, costs, supply, demand):
        self.quantity = quantity
        self.costs = costs
        self.supply = supply
        self.demand = demand

    def optimize(self, max_iter=1000):

        m = len(self.supply)
        n = len(self.demand)

        quantity = [row[:] for row in self.quantity]

        # tworzy zbiór współrzędnych (i, j) - zmienne bazowe
        def basics_set(q):
            basics = set()
            for i in range(m):
                for j in range(n):
                    if q[i][j] > 0:
                        basics.add((i, j))
            return basics

        # zapobieganie degeneracji przez dodanie zerowych przydziałów
        def ensure_degeneracy(q):
            basics = basics_set(q)
            needed = m + n - 1
            if len(basics) >= needed:
                return q

            cells = [(self.costs[i][j], i, j) for i in range(m) for j in range(n) if (i, j) not in basics]
            cells.sort()
            for _, i, j in cells:
                # !
                q[i][j] = 1e-10
                basics.add((i, j))
                if len(basics) >= needed:
                    break
            return q

        # quantity = ensure_degeneracy(quantity)

        # obliczanie potencjałów u i v dla zmiennych bazowych
        def compute_potentials(basics):
            u = [None] * m
            v = [None] * n
            # Punkt startowy - ustalamy pierwszy potencjał na 0
            u[0] = 0
            changed = True
            while changed:
                changed = False
                for (i, j) in basics:
                    if u[i] is not None and v[j] is None:
                        v[j] = self.costs[i][j] - u[i]
                        changed = True
                    elif v[j] is not None and u[i] is None:
                        u[i] = self.costs[i][j] - v[j]
                        changed = True
            return u, v

        # obliczanie oceny komórek niebazowych (wskaźniki optymalności)
        def compute_deltas(basics, u, v):
            deltas = [[None] * n for _ in range(m)]
            for i in range(m):
                for j in range(n):
                    if (i, j) in basics:
                        deltas[i][j] = None
                    else:
                        ui = 0 if u[i] is None else u[i]
                        vj = 0 if v[j] is None else v[j]
                        deltas[i][j] = self.costs[i][j] - (ui + vj)
            return deltas

        # wybranie pola z najniższą wartością wskaźnika optymalności
        def find_entering(deltas):
            min_val = 0
            pos = None
            for i in range(m):
                for j in range(n):
                    if deltas[i][j] is None:
                        continue
                    if deltas[i][j] < min_val:
                        min_val = deltas[i][j]
                        pos = (i, j)
            return pos, min_val

        # znajdowanie cyklu - start z pola entering i poruszanie się wzdłuż wierszy i kolumn zmiennych bazowych
        def find_cycle(start, basics):
            basics_all = set(basics)
            basics_all.add(start)

            # dla danej komórki, inne komórki w tym samym wierszu/kolumnie
            row_map = {i: [] for i in range(m)}
            col_map = {j: [] for j in range(n)}
            for (i, j) in basics_all:
                row_map[i].append((i, j))
                col_map[j].append((i, j))


            def backtrack(pos, visited, move_row):
                # move_row==True - ruch w wierszu, False - w kolumnie
                i, j = pos
                if move_row:
                    for (_, nj) in row_map[i]:
                        nxt = (i, nj)
                        if nxt == start and len(path) >= 4:
                            return True
                        if nxt in visited or nxt == pos:
                            continue
                        visited.add(nxt)
                        path.append(nxt)
                        if backtrack(nxt, visited, not move_row):
                            return True
                        path.pop()
                        visited.remove(nxt)
                else:
                    for (ni, _) in col_map[j]:
                        nxt = (ni, j)
                        if nxt == start and len(path) >= 4:
                            return True
                        if nxt in visited or nxt == pos:
                            continue
                        visited.add(nxt)
                        path.append(nxt)
                        if backtrack(nxt, visited, not move_row):
                            return True
                        path.pop()
                        visited.remove(nxt)
                return False

            # próba rozpoczęcia od ruchu w wierszu lub kolumnie
            path = [start]
            if backtrack(start, set([start]), True):
                return path[:]
            path = [start]
            if backtrack(start, set([start]), False):
                return path[:]
            return None

        # zastosowanie cyklu do aktualizacji przydziałów
        def apply_cycle(q, cycle):
            # identyfikacja pozycji minusowych
            minus_positions = []
            for idx, pos in enumerate(cycle):
                if idx % 2 == 1:
                    minus_positions.append(pos)
            # theta = min ilości na pozycjach minusowych
            theta = min(q[i][j] for (i, j) in minus_positions)
            # aktualizacja ilości wzdłuż cyklu
            for idx, (i, j) in enumerate(cycle):
                if idx % 2 == 0:
                    q[i][j] += theta
                else:
                    q[i][j] -= theta
            return q

        # !
        # quantity = ensure_degeneracy(quantity)
        # główna pętla optymalizacji
        it = 0
        while it < max_iter:
            # !
            # basics = basics_set(quantity)
            quantity = ensure_degeneracy(quantity)
            basics = basics_set(quantity)
            u, v = compute_potentials(basics)
            deltas = compute_deltas(basics, u, v)
            entering, val = find_entering(deltas)
            if entering is None:
                break
            cycle = find_cycle(entering, basics)
            if cycle is None:
                # !
                i_ent, j_ent = entering
                quantity[i_ent][j_ent] = 1e-10
                # !
                # basics.add(entering)
                it += 1
                continue
            # zastosowanie cyklu
            quantity = apply_cycle(quantity, cycle)
            it += 1

        total = 0
        for i in range(m):
            for j in range(n):
                if quantity[i][j] < 1e-9:
                    quantity[i][j] = 0
                total += quantity[i][j] * self.costs[i][j]
        self.quantity = quantity
        return total, quantity


if __name__ == "__main__":
    costs = [
        [3,4,7,1],
        [5,1,3,2],
        [2,4,5,4]
    ]
    supply = [100, 150, 100]
    demand = [80, 120, 120, 30]
    
    # costs = [
    # [10, 40, 50, 20],
    # [20, 60, 40, 60],
    # [30, 30, 30, 40]
    # ]
    # supply = [300, 450, 800]
    # demand = [630, 160, 170, 340]

    from solution import TransportSolution
    model = TransportSolution(costs, demand, supply)
    results, quantity = model.north_west()
    print(results)
    costs = model.costs
    supply = model.supply
    demand = model.demand
    optimization = TransportOptimization(quantity=quantity, costs=costs, supply=supply, demand=demand)
    print(optimization.optimize())