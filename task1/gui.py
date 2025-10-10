from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QLineEdit, QPushButton, QLabel, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMovie
from model import Model

#TODO: refactor GUI layout
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Zadanie 1, Ćwiczenie 3')
        self.resize(1200, 800)
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

        # Space for plot and GIF side by side
        main_layout.addWidget(QLabel('Wykresy:'))
        self.plot_frame = QFrame()
        self.plot_frame.setFrameShape(QFrame.StyledPanel)
        self.plot_frame.setMinimumHeight(380)
        self.plot_layout = QHBoxLayout()
        self.plot_frame.setLayout(self.plot_layout)
        main_layout.addWidget(self.plot_frame)

        self.setLayout(main_layout)

    def run_script(self):
        # Remove previous plot widgets
        for i in reversed(range(self.plot_layout.count())):
            widget = self.plot_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

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

        model = Model(data=table_values, income_w1=zysk_w1, income_w2=zysk_w2)
        solution = model.solve()
        # Static plot
        fig = model.full_plot(*solution)
        canvas = FigureCanvas(fig)
        canvas.setMaximumSize(500, 380)
        self.plot_layout.addWidget(canvas)
        # Animated GIF
        model.animated_plot(*solution)
        gif_path = "animation.gif"
        gif_label = QLabel()
        gif_label.setAlignment(Qt.AlignCenter)
        movie = QMovie(gif_path)
        gif_label.setMovie(movie)
        movie.start()
        gif_label.setMaximumSize(500, 380)
        self.plot_layout.addWidget(gif_label)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
