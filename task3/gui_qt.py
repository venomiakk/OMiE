from PyQt5 import QtWidgets, QtCore
import sys

from solution import TransportSolution
from optimization import TransportOptimization


DEFAULT_COSTS = [
    [3, 4, 7, 1],
    [5, 1, 3, 2],
    [2, 4, 5, 4],
]
DEFAULT_SUPPLY = [100, 150, 100]
DEFAULT_DEMAND = [80, 120, 120, 30]


class TransportQtApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Problem transportowy")
        self._build_ui()

    def _build_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        control = QtWidgets.QHBoxLayout()
        control.addWidget(QtWidgets.QLabel("Liczba wierszy (podaż):"))
        self.rows_spin = QtWidgets.QSpinBox(value=len(DEFAULT_SUPPLY))
        self.rows_spin.setRange(1, 20)
        control.addWidget(self.rows_spin)

        control.addWidget(QtWidgets.QLabel("Liczba kolumn (popyt):"))
        self.cols_spin = QtWidgets.QSpinBox(value=len(DEFAULT_DEMAND))
        self.cols_spin.setRange(1, 20)
        control.addWidget(self.cols_spin)

        self.set_btn = QtWidgets.QPushButton("Ustaw rozmiar")
        self.set_btn.clicked.connect(self.build_tables)
        control.addWidget(self.set_btn)

        self.compute_btn = QtWidgets.QPushButton("Oblicz")
        self.compute_btn.clicked.connect(self.compute_all)
        control.addWidget(self.compute_btn)

        main_layout.addLayout(control)

        # Input area
        self.input_group = QtWidgets.QGroupBox("Dane: koszty / podaż / popyt")
        self.input_layout = QtWidgets.QGridLayout()
        self.input_group.setLayout(self.input_layout)
        main_layout.addWidget(self.input_group)

        # Scroll area for results
        self.results_area = QtWidgets.QScrollArea()
        self.results_widget = QtWidgets.QWidget()
        self.results_layout = QtWidgets.QVBoxLayout(self.results_widget)
        self.results_area.setWidgetResizable(True)
        self.results_area.setWidget(self.results_widget)
        main_layout.addWidget(self.results_area, 1)

        self.input_table = None

        self.build_tables()

    def build_tables(self):
        # clear layout
        while self.input_layout.count():
            item = self.input_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        m = max(1, self.rows_spin.value())
        n = max(1, self.cols_spin.value())

        # single input table: costs (m x n) + supply (last column) + demand (last row)
        if self.input_table:
            self.input_table.deleteLater()
        rows = m + 1  # extra row for demand
        cols = n + 1  # extra col for supply
        self.input_table = QtWidgets.QTableWidget(rows, cols)
        # horizontal headers: Z1..Zn, last column "Podaż"
        h_labels = [f"Z{j+1}" for j in range(n)] + ["Podaż"]
        v_labels = [f"H{i+1}" for i in range(m)] + ["Popyt"]
        self.input_table.setHorizontalHeaderLabels(h_labels)
        self.input_table.setVerticalHeaderLabels(v_labels)
        self.input_table.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)
        # allow table to expand and show contents; don't artificially cap maximum size
        self.input_table.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.input_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.input_table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        # fill costs
        for i in range(m):
            for j in range(n):
                item = QtWidgets.QTableWidgetItem()
                try:
                    item.setText(str(DEFAULT_COSTS[i][j]))
                except Exception:
                    item.setText('0')
                self.input_table.setItem(i, j, item)

        # fill supply in last column
        for i in range(m):
            item = QtWidgets.QTableWidgetItem()
            try:
                item.setText(str(DEFAULT_SUPPLY[i]))
            except Exception:
                item.setText('0')
            self.input_table.setItem(i, n, item)

        # fill demand in last row
        for j in range(n):
            item = QtWidgets.QTableWidgetItem()
            try:
                item.setText(str(DEFAULT_DEMAND[j]))
            except Exception:
                item.setText('0')
            self.input_table.setItem(m, j, item)

        # bottom-right cell empty
        self.input_layout.addWidget(self.input_table, 0, 0, rows, cols)

        # make input table show all content without inner scrollbars where possible
        self.input_table.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.input_table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # compute sizes and set minimum size only (do NOT set maximum) so table can expand
        self._adjust_table_size(self.input_table)

    def read_inputs(self):
        # reconstruct matrix from QTableWidgets
        m = max(1, self.rows_spin.value())
        n = max(1, self.cols_spin.value())
        costs = [[0] * n for _ in range(m)]
        try:
            # costs block
            for i in range(m):
                for j in range(n):
                    item = self.input_table.item(i, j)
                    if item is None or item.text().strip() == "":
                        raise ValueError("Empty cost cell")
                    costs[i][j] = int(item.text())
        except Exception:
            QtWidgets.QMessageBox.critical(self, "Błąd danych", "Koszty muszą być liczbami całkowitymi i nie mogą być puste")
            return None

        try:
            supply = []
            for i in range(m):
                item = self.input_table.item(i, n)
                if item is None or item.text().strip() == "":
                    raise ValueError("Empty supply cell")
                supply.append(int(item.text()))

            demand = []
            for j in range(n):
                item = self.input_table.item(m, j)
                if item is None or item.text().strip() == "":
                    raise ValueError("Empty demand cell")
                demand.append(int(item.text()))
        except Exception:
            QtWidgets.QMessageBox.critical(self, "Błąd danych", "Podaż i popyt muszą być liczbami całkowitymi i nie mogą być puste")
            return None

        return costs, demand, supply

    def compute_all(self):
        vals = self.read_inputs()
        if vals is None:
            return
        costs, demand, supply = vals

        model = TransportSolution(costs, demand[:], supply[:])

        methods = [
            ("Metoda północno-zachodniego kąta", model.north_west),
            ("Minimum z macierzy", model.min_matrix),
            ("Minimum z kolumn", model.min_col),
            ("Minimum z wierszy", model.min_row),
            ("VAM", model.vam),
        ]

        # clear previous results
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        for name, func in methods:
            try:
                res_cost, quantity = func()
            except Exception as e:
                res_cost, quantity = None, None
                print(f"Metoda {name} nie powiodła się:", e)

            opt_cost, opt_quantity = None, None
            if quantity is not None:
                try:
                    optimizer = TransportOptimization(quantity=quantity, costs=model.costs, supply=model.supply, demand=model.demand)
                    opt_cost, opt_quantity = optimizer.optimize()
                except Exception as e:
                    print(f"Optymalizacja dla {name} nie powiodła się:", e)

            self._add_result_block(name, res_cost, quantity, opt_cost, opt_quantity)

    def _add_result_block(self, name, cost, qty, opt_cost, opt_qty):
        group = QtWidgets.QGroupBox(name)
        h = QtWidgets.QHBoxLayout(group)

        left = QtWidgets.QVBoxLayout()
        left.addWidget(QtWidgets.QLabel(f"Koszt początkowy: {cost}" if cost is not None else "Błąd obliczeń"))
        if qty is not None:
            left.addWidget(self._make_table_widget(qty, title='Początkowe'))

        right = QtWidgets.QVBoxLayout()
        right.addWidget(QtWidgets.QLabel(f"Koszt zoptymalizowany: {opt_cost}" if opt_cost is not None else "Błąd optymalizacji"))
        if opt_qty is not None:
            right.addWidget(self._make_table_widget(opt_qty, title='Zoptymalizowane'))

        h.addLayout(left)
        h.addLayout(right)
        self.results_layout.addWidget(group)

    def _make_table_widget(self, matrix, title=None):
        widget = QtWidgets.QWidget()
        v = QtWidgets.QVBoxLayout(widget)
        if title:
            v.addWidget(QtWidgets.QLabel(title))
        m = len(matrix)
        n = len(matrix[0]) if m > 0 else 0
        table = QtWidgets.QTableWidget(m, n)
        # set headers Zx / Hx
        table.setHorizontalHeaderLabels([f"Z{j+1}" for j in range(n)])
        table.setVerticalHeaderLabels([f"H{i+1}" for i in range(m)])
        table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        for i in range(m):
            for j in range(n):
                item = QtWidgets.QTableWidgetItem(str(matrix[i][j]))
                table.setItem(i, j, item)
        # resize to content and set minimum size so individual table doesn't scroll internally
        table.resizeColumnsToContents()
        table.resizeRowsToContents()
        table.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # allow tables to expand (set minimum only)
        self._adjust_table_size(table)
        v.addWidget(table)
        return widget

    def _adjust_table_size(self, table: QtWidgets.QTableWidget):
        # ensure table expands to show all content without its own scrollbars
        table.resizeColumnsToContents()
        table.resizeRowsToContents()
        width = table.verticalHeader().width()
        for col in range(table.columnCount()):
            width += table.columnWidth(col)
        height = table.horizontalHeader().height()
        for row in range(table.rowCount()):
            height += table.rowHeight(row)
        # add some margins
        table.setMinimumSize(width + 8, height + 8)
        # do NOT set maximum size so table may expand with window


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = TransportQtApp()
    w.resize(900, 600)
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
