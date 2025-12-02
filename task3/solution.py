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

        print("Is balanced:", sum(demand) == sum(supply))
        for row in self.costs:
            for value in row:
                print(value, end=' ')
            print("\n") 

        print("-----------")

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

        def find_min_position():
            min_cost = float('inf')
            min_pos = (-1, -1)
            for i in range(len(supply)):
                for j in range(len(demand)):
                    if costs[i][j] < min_cost and supply[i] > 0 and demand[j] > 0:
                        min_cost = costs[i][j]
                        min_pos = (i, j)
            return min_pos

        supply = self.supply[:]
        demand = self.demand[:]
        costs = [row [:] for row in self.costs]
        quantity = [[0 for _ in range(len(demand))] for _ in range(len(supply))]

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
        def find_min_position_column():
            min_cost = float('inf')
            position = -1
            for k in range(len(supply)):
                if column[k] < min_cost and demand[j] > 0 and supply[k] > 0:
                    min_cost = column[k]
                    position = k
            
            return position
            
        supply = self.supply[:]
        demand = self.demand[:]
        costs = [row [:] for row in self.costs]
        quantity = [[0 for _ in range(len(demand))] for _ in range(len(supply))]
        
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
        def find_min_position_row():
            min_cost = float('inf')
            position = -1
            for k in range(len(demand)):
                if row[k] < min_cost and supply[i] > 0 and demand[k] > 0:
                    min_cost = row[k]
                    position = k

            return position
        supply = self.supply[:]
        demand = self.demand[:]
        costs = [row [:] for row in self.costs]
        quantity = [[0 for _ in range(len(demand))] for _ in range(len(supply))]

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
        def abs_diff_col():
            diffs = []
            max_value = float('-inf')
            position = -1
            if j < len(demand) - 1:
                for k in range(len(supply)):
                    diffs.append(abs(costs[k][j] - costs[k][j+1]))
                for k in range(len(supply)):
                    if diffs[k] > max_value and demand[j] > 0 and supply[k] > 0:
                        max_value = diffs[k]
                        position = k
            else:
                for k in range(len(supply)):
                    if costs[k][j] > max_value and demand[j] > 0 and supply[k] > 0:
                        max_value = costs[k][j]
                        position = k
            return position
        
        supply = self.supply[:]
        demand = self.demand[:]
        costs = [row [:] for row in self.costs]
        quantity = [[0 for _ in range(len(demand))] for _ in range(len(supply))]

        for j in range(len(demand)):
            while True:
                i = abs_diff_col()
                if i == -1:
                    break
                
                if supply[i] < demand[j]:
                    quantity[i][j] = supply[i]
                    demand[j] -= supply[i]
                    supply[i] = 0
                    # costs[i] = [float('inf')] * len(demand)
                else:
                    quantity[i][j] = demand[j]
                    supply[i] -= demand[j]
                    demand[j] = 0
                    # for k in range(len(supply)):
                    #     costs[k][j] = float('inf')

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
    print("-----nw-------")
    print(model.north_west())
    print("-----min matrix-------")
    print(model.min_matrix())
    print("-----min col-------")
    print(model.min_col())
    print("-----min row-------")
    print(model.min_row())
    print("-----vam-------")
    print(model.vam())