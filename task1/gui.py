from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QLineEdit, QPushButton, QLabel, QFrame
)
from PyQt5.QtCore import Qt
from model import Model

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Zadanie 1, Ćwiczenie 3')
        self.resize(800, 600)
        main_layout = QVBoxLayout()

        # Table 2x3
        self.table = QTableWidget(2, 3)
        self.table.setHorizontalHeaderLabels(['K1', 'K2', 'K3'])
        self.table.setVerticalHeaderLabels(['W1', 'W2'])
        # Set default values for table cells
        default_table_values = [["1.0", "1.0", "4.0"], ["6.0", "2.0", "1.0"]]
        for i in range(2):
            for j in range(3):
                item = QTableWidgetItem(default_table_values[i][j])
                item.setFlags(item.flags() | Qt.ItemIsEditable)
                self.table.setItem(i, j, item)
        main_layout.addWidget(QLabel('Tabela wartości:'))
        main_layout.addWidget(self.table)

        # Input fields
        input_layout = QHBoxLayout()
        self.input1 = QLineEdit()
        self.input1.setPlaceholderText('Zysk W1')
        self.input1.setText('20')  # Default value
        self.input2 = QLineEdit()
        self.input2.setPlaceholderText('Zysk W2')
        self.input2.setText('10')  # Default value
        input_layout.addWidget(QLabel('Zysk W1:'))
        input_layout.addWidget(self.input1)
        input_layout.addWidget(QLabel('Zysk W2:'))
        input_layout.addWidget(self.input2)
        main_layout.addLayout(input_layout)

        # Button to run script
        self.run_button = QPushButton('Oblicz')
        self.run_button.clicked.connect(self.run_script)
        main_layout.addWidget(self.run_button)

        # Space for plot
        main_layout.addWidget(QLabel('Wykres:'))
        self.plot_frame = QFrame()
        self.plot_frame.setFrameShape(QFrame.StyledPanel)
        self.plot_frame.setMinimumHeight(350)
        main_layout.addWidget(self.plot_frame)

        self.setLayout(main_layout)

    def run_script(self):
        
        # Remove previous plot widgets
        if self.plot_frame.layout():
            for i in reversed(range(self.plot_frame.layout().count())):
                widget = self.plot_frame.layout().itemAt(i).widget()
                if widget:
                    widget.setParent(None)
        else:
            self.plot_frame.setLayout(QVBoxLayout())

        # Read input fields
        zysk_w1 = float(self.input1.text()) if self.input1.text() else 0.0
        zysk_w2 = float(self.input2.text()) if self.input2.text() else 0.0

        # Read table values
        table_values = []
        for i in range(self.table.rowCount()):
            row = []
            for j in range(self.table.columnCount()):
                val = self.table.item(i, j).text()
                try:
                    row.append(float(val))
                except ValueError:
                    row.append(0.0)
            table_values.append(row)

        model = Model(table_values, zysk_w1, zysk_w2)
        model.solve()  # For debugging
        # Example: plot sum of each row as bar chart
        row_sums = [sum(row) for row in table_values]
        labels = [self.table.verticalHeaderItem(i).text() for i in range(self.table.rowCount())]

        fig = Figure(figsize=(5, 2.5))
        ax = fig.add_subplot(111)
        ax.bar(labels, row_sums, color=['blue', 'green'])
        ax.set_title(f'Suma wartości w wierszach\nZysk W1: {zysk_w1}, Zysk W2: {zysk_w2}')
        ax.set_xlabel('Wiersz')
        ax.set_ylabel('Suma')

        canvas = FigureCanvas(fig)
        self.plot_frame.layout().addWidget(canvas)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
