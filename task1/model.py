import matplotlib.pyplot as plt

class Model:
    def __init__(self, data, income_w1, income_w2):
        self.data = data
        self.resources_w1 = data[0]
        self.resources_w2 = data[1]
        self.data = data
        self.income_w1 = income_w1
        self.income_w2 = income_w2
        print(f"Model initialized with data: {self.resources_w1, self.resources_w2}, "
              f"income_w1: {income_w1}, income_w2: {income_w2}")

    def solve(self):
        #TODO: change everything below
        # 1. restriction: k1 <= 60
        r1 = 60.0
        values_r1 = [
            [0, r1 / self.data[0][0]],
            [r1 / self.data[1][0], 0]
        ]
        # 2. restriciotn: k2 <= 24
        r2 = 24.0
        values_r2 = [
            [0, r2 / self.data[0][1]],
            [r2 / self.data[1][1], 0]
        ]
        # 3. restriction: k3 >= 8
        r3 = 8.0
        values_r3 = [
            [0, r3 / self.data[0][2]],
            [r3 / self.data[1][2], 0]
        ]
        plotable_data = [
            [values_r1, 'lt'],
            [values_r2, 'lt'],
            [values_r3, 'gt']
        ]
        self.test_plot(plotable_data)
        return None
    
    def test_plot(self, data):
        print(data)
        # ymax = 0
        for line in data:
            x = line[0][0]
            y = line[0][1]
            # ymax = ymax if ymax > max(y) else max(y)
            plt.plot(x, y)
            # TODO
            # plt.fill_between(x, y, ymax, alpha=0.5)
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.show()

if __name__ == '__main__':
    data = [[1.0, 1.0, 4.0], [6.0, 2.0, 1.0]]
    income_w1 = 20.0
    income_w2 = 10.0
    model = Model(data=data, income_w1=income_w1, income_w2=income_w2)
    model.solve()