class TransportSolution:
    def __init__(self, costs, demand, supply):
        self.costs = costs
        self.demand = demand
        self.supply = supply
        if not sum(demand) == sum(supply):
            if sum(supply) < sum(demand):
                self.supply.append(sum(demand) - sum(supply))
                self.costs.append([0 for _ in range(len(demand))])
            else:
                self.demand.append(sum(supply) - sum(demand))
                for i in range(len(supply)):
                    self.costs[i].append(0)

        # print("Is balanced:", sum(demand) == sum(supply))
        # for row in self.costs:
        #     for value in row:
        #         print(value, end=' ')
        #     print("\n") 

        # print("-----------")

    def north_west(self):
        supply = self.supply[:]
        demand = self.demand[:]
        quantity = [[0 for _ in range(len(demand))] for _ in range(len(supply))]

        i, j = 0, 0
        while i < len(supply) and j < len(demand):
            if supply[i] < demand[j]:
                quantity[i][j] = supply[i]
                demand[j] -= supply[i]
                supply[i] = 0
                i += 1
            else:
                quantity[i][j] = demand[j]
                supply[i] -= demand[j]
                demand[j] = 0
                j += 1
    
        i, j = 0, 0
        result = 0
        for i in range(len(supply)):
            for j in range(len(demand)):
                result += quantity[i][j] * self.costs[i][j]

        return result, quantity

    def min_matrix(self):
        supply = self.supply[:]
        demand = self.demand[:]
        costs = [row [:] for row in self.costs]
        quantity = [[0 for _ in range(len(demand))] for _ in range(len(supply))]
        
        def find_min_position():
            min_cost = float('inf')
            min_pos = (-1, -1)
            for i in range(len(supply)):
                for j in range(len(demand)):
                    if costs[i][j] < min_cost and supply[i] > 0 and demand[j] > 0:
                        min_cost = costs[i][j]
                        min_pos = (i, j)
            return min_pos
        
        while True:
            i, j = find_min_position()
            if i == -1 and j == -1:
                break

            if supply[i] < demand[j]:
                quantity[i][j] = supply[i]
                demand[j] -= supply[i]
                supply[i] = 0
                costs[i] = [float('inf')] * len(demand)
            else:
                quantity[i][j] = demand[j]
                supply[i] -= demand[j]
                demand[j] = 0
                for k in range(len(supply)):
                    costs[k][j] = float('inf')
        
        i, j = 0, 0
        result = 0
        for i in range(len(supply)):
            for j in range(len(demand)):
                result += quantity[i][j] * self.costs[i][j]

        return result, quantity

    def min_col(self):      
        supply = self.supply[:]
        demand = self.demand[:]
        costs = [row [:] for row in self.costs]
        quantity = [[0 for _ in range(len(demand))] for _ in range(len(supply))]
        
        def find_min_position_column():
            min_cost = float('inf')
            position = -1
            for k in range(len(supply)):
                if column[k] < min_cost and demand[j] > 0 and supply[k] > 0:
                    min_cost = column[k]
                    position = k
            
            return position

        for j in range(len(demand)):
            column = []
            for i in range(len(supply)):
                column.append(costs[i][j])
            
            while True:
                i = find_min_position_column()
                if i == -1:
                    break

                if supply[i] < demand[j]:
                    quantity[i][j] = supply[i]
                    demand[j] -= supply[i]
                    supply[i] = 0
                    costs[i] = [float('inf')] * len(demand)
                else:
                    quantity[i][j] = demand[j]
                    supply[i] -= demand[j]
                    demand[j] = 0
                    for k in range(len(supply)):
                        costs[k][j] = float('inf')

        i, j = 0, 0
        result = 0
        for i in range(len(supply)):
            for j in range(len(demand)):
                result += quantity[i][j] * self.costs[i][j]

        return result, quantity

    def min_row(self):
        supply = self.supply[:]
        demand = self.demand[:]
        costs = [row [:] for row in self.costs]
        quantity = [[0 for _ in range(len(demand))] for _ in range(len(supply))]

        def find_min_position_row():
            min_cost = float('inf')
            position = -1
            for k in range(len(demand)):
                if row[k] < min_cost and supply[i] > 0 and demand[k] > 0:
                    min_cost = row[k]
                    position = k

            return position

        for i in range(len(supply)):
            row = costs[i]
            while True:
                j = find_min_position_row()
                if j == -1:
                    break

                if supply[i] < demand[j]:
                    quantity[i][j] = supply[i]
                    demand[j] -= supply[i]
                    supply[i] = 0
                    costs[i] = [float('inf')] * len(demand)
                else:
                    quantity[i][j] = demand[j]
                    supply[i] -= demand[j]
                    demand[j] = 0
                    for k in range(len(supply)):
                        costs[k][j] = float('inf')

        i, j = 0, 0
        result = 0
        for i in range(len(supply)):
            for j in range(len(demand)):
                result += quantity[i][j] * self.costs[i][j]

        return result, quantity

    def vam(self):
        supply = self.supply[:]
        demand = self.demand[:]
        costs = [row [:] for row in self.costs]
        quantity = [[0 for _ in range(len(demand))] for _ in range(len(supply))]

        def calculate_penalties():
            row_penalties = [0 for _ in range(len(supply))]
            col_penalties = [0 for _ in range(len(demand))]

            for i in range(len(supply)):
                if supply[i] <= 0:          # skip exhausted rows
                    row_penalties[i] = 0
                    continue
                valid_costs = [costs[i][j] for j in range(len(demand)) if demand[j] > 0]
                if len(valid_costs) >= 2:
                    sorted_costs = sorted(valid_costs)
                    row_penalties[i] = sorted_costs[1] - sorted_costs[0]
                elif len(valid_costs) == 1:
                    row_penalties[i] = valid_costs[0]

            for j in range(len(demand)):
                if demand[j] <= 0:         # skip exhausted columns
                    col_penalties[j] = 0
                    continue
                valid_costs = [costs[i][j] for i in range(len(supply)) if supply[i] > 0]
                if len(valid_costs) >= 2:
                    sorted_costs = sorted(valid_costs)
                    col_penalties[j] = sorted_costs[1] - sorted_costs[0]
                elif len(valid_costs) == 1:
                    col_penalties[j] = valid_costs[0]

            return row_penalties, col_penalties
        
        row_penalties, col_penalties = calculate_penalties()

        while True:
            max_row_penalty = max(row_penalties)
            max_col_penalty = max(col_penalties)

            if max_row_penalty == 0 and max_col_penalty == 0:
                break

            if max_row_penalty >= max_col_penalty:
                i = row_penalties.index(max_row_penalty)
                j = min((costs[i][k], k) for k in range(len(demand)) if demand[k] > 0)[1]
            else:
                j = col_penalties.index(max_col_penalty)
                i = min((costs[k][j], k) for k in range(len(supply)) if supply[k] > 0)[1]

            # jeśli wybrana pozycja ma supply==0 lub demand==0, ustaw penalizację na 0 i kontynuuj
            if supply[i] <= 0 or demand[j] <= 0:
                row_penalties[i] = 0
                col_penalties[j] = 0
                row_penalties, col_penalties = calculate_penalties()
                continue

            if supply[i] < demand[j]:
                quantity[i][j] = supply[i]
                demand[j] -= supply[i]
                supply[i] = 0
                costs[i] = [float('inf')] * len(demand)   # oznacz wyczerpany wiersz
            else:
                quantity[i][j] = demand[j]
                supply[i] -= demand[j]
                demand[j] = 0
                for k in range(len(supply)):
                    costs[k][j] = float('inf')             # oznacz wyczerpaną kolumnę

            row_penalties, col_penalties = calculate_penalties()
        i, j = 0, 0
        result = 0
        for i in range(len(supply)):
            for j in range(len(demand)):
                result += quantity[i][j] * self.costs[i][j]
        return result, quantity



if __name__ == "__main__":
    # costs = [
    #     [3,4,7,1],
    #     [5,1,3,2],
    #     [2,4,5,4]
    # ]
    # supply = [100, 150, 100]
    # demand = [80, 120, 120, 30]

    costs = [
        [10, 40, 50, 20],
        [20, 60, 40, 60],
        [30, 30, 30, 40]
    ]
    supply = [300, 450, 800]
    demand = [630, 160, 170, 340]
    model = TransportSolution(costs, demand, supply)
    # print("-----nw-------")
    # print(model.north_west())
    # print("-----min matrix-------")
    # print(model.min_matrix())
    # print("-----min col-------")
    # print(model.min_col())
    # print("-----min row-------")
    # print(model.min_row())
    print("-----vam-------")
    print(model.vam())
    print(model.supply)
    print(model.demand)