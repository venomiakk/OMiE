from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QLineEdit, QPushButton, QLabel, QFrame, QSpinBox, QComboBox, QScrollArea
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QMovie
from model import Model

#TODO: refactor GUI layout
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Zadanie 1, Ćwiczenie 3')
        self.resize(1200, 1000)
        
        # Create scroll area for the entire window
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Number of constraints selector
        main_layout.addWidget(QLabel(''))  # Spacer
        constraint_count_header = QLabel('1. Wybierz liczbę ograniczeń:')
        constraint_count_header.setStyleSheet("font-size: 14px; font-weight: bold;")
        main_layout.addWidget(constraint_count_header)
        
        constraint_count_layout = QHBoxLayout()
        constraint_count_layout.addWidget(QLabel('Liczba ograniczeń:'))
        self.constraint_count_spin = QSpinBox()
        self.constraint_count_spin.setMinimum(1)
        self.constraint_count_spin.setMaximum(10)
        self.constraint_count_spin.setValue(3)
        self.constraint_count_spin.valueChanged.connect(self.update_constraint_inputs)
        constraint_count_layout.addWidget(self.constraint_count_spin)
        constraint_count_layout.addStretch()
        main_layout.addLayout(constraint_count_layout)

        # Table 2x3 (will be updated dynamically based on constraint count)
        table_header = QLabel('2. Ustaw współczynniki dla produktów (W1, W2):')
        table_header.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 15px;")
        main_layout.addWidget(table_header)
        
        table_info = QLabel('Wiersze reprezentują produkty W1 i W2. Kolumny K1, K2, ... reprezentują współczynniki dla każdego ograniczenia.')
        table_info.setStyleSheet("color: #666; font-size: 10px; margin-bottom: 5px;")
        main_layout.addWidget(table_info)
        
        self.table = QTableWidget(2, 3)
        self.table.setHorizontalHeaderLabels(['K1', 'K2', 'K3'])
        self.table.setVerticalHeaderLabels(['W1', 'W2'])
        self.table.setMinimumHeight(120)  # Minimum height to show both rows
        self.table.setMaximumHeight(150)  # Maximum height
        # Set column widths
        for i in range(3):
            self.table.setColumnWidth(i, 80)
        # Set default values for table cells (based on the task: W1=[1,1,4], W2=[6,2,1])
        default_table_values = [["1", "1", "4"], ["6", "2", "1"]]
        for i in range(2):
            for j in range(3):
                item = QTableWidgetItem(default_table_values[i][j])
                item.setFlags(item.flags() | Qt.ItemIsEditable)
                self.table.setItem(i, j, item)
        main_layout.addWidget(self.table)

        # Constraints configuration
        constraints_header = QLabel('3. Skonfiguruj ograniczenia:')
        constraints_header.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 15px;")
        main_layout.addWidget(constraints_header)
        
        constraints_info = QLabel('Dla każdego ograniczenia ustaw operator (<=, >=, ==) oraz wartość graniczną.')
        constraints_info.setStyleSheet("color: #666; font-size: 10px; margin-bottom: 5px;")
        main_layout.addWidget(constraints_info)
        
        self.constraints_frame = QFrame()
        self.constraints_frame.setFrameShape(QFrame.StyledPanel)
        self.constraints_layout = QVBoxLayout()
        self.constraints_frame.setLayout(self.constraints_layout)
        main_layout.addWidget(self.constraints_frame)
        
        # Store constraint input widgets
        self.constraint_inputs = []
        self.update_constraint_inputs()

        # Input fields for profits
        profits_header = QLabel('4. Ustaw zyski dla produktów:')
        profits_header.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 15px;")
        main_layout.addWidget(profits_header)
        
        input_layout = QHBoxLayout()
        self.input1 = QLineEdit()
        self.input1.setPlaceholderText('Zysk W1')
        self.input1.setText('20')  # Default value from task
        self.input1.setMaximumWidth(100)
        self.input2 = QLineEdit()
        self.input2.setPlaceholderText('Zysk W2')
        self.input2.setText('10')  # Default value from task (corrected to positive)
        self.input2.setMaximumWidth(100)
        input_layout.addWidget(QLabel('Zysk dla W1:'))
        input_layout.addWidget(self.input1)
        input_layout.addWidget(QLabel('   Zysk dla W2:'))
        input_layout.addWidget(self.input2)
        input_layout.addStretch()
        main_layout.addLayout(input_layout)

        # Plot type selector
        plot_type_header = QLabel('5. Wybierz typ wizualizacji:')
        plot_type_header.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 15px;")
        main_layout.addWidget(plot_type_header)
        
        plot_type_layout = QHBoxLayout()
        plot_type_layout.addWidget(QLabel('Rodzaj wykresu:'))
        self.plot_type_combo = QComboBox()
        self.plot_type_combo.addItems(['Oba (statyczny + animacja)', 'Tylko statyczny', 'Tylko animacja'])
        self.plot_type_combo.setMaximumWidth(250)
        plot_type_layout.addWidget(self.plot_type_combo)
        plot_type_layout.addStretch()
        main_layout.addLayout(plot_type_layout)

        # Button to run script
        self.run_button = QPushButton('Oblicz')
        self.run_button.clicked.connect(self.run_script)
        self.run_button.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px; margin-top: 10px;")
        main_layout.addWidget(self.run_button)

        # Space for plot and GIF side by side
        main_layout.addWidget(QLabel('Wykresy:'))
        self.plot_frame = QFrame()
        self.plot_frame.setFrameShape(QFrame.StyledPanel)
        self.plot_frame.setMinimumHeight(380)
        self.plot_frame.setMaximumHeight(480)
        self.plot_layout = QHBoxLayout()
        self.plot_frame.setLayout(self.plot_layout)
        main_layout.addWidget(self.plot_frame)

        scroll_widget.setLayout(main_layout)
        scroll.setWidget(scroll_widget)
        
        main_window_layout = QVBoxLayout()
        main_window_layout.addWidget(scroll)
        self.setLayout(main_window_layout)
    
    def clear_layout(self, layout):
        """Helper method to recursively clear a layout"""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())
    
    def update_constraint_inputs(self):
        """Update the constraint input fields based on the selected count"""
        # Clear existing inputs - properly delete both widgets and layouts
        while self.constraints_layout.count():
            item = self.constraints_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())
        
        self.constraint_inputs = []
        num_constraints = self.constraint_count_spin.value()
        
        # Update table columns
        self.table.setColumnCount(num_constraints)
        headers = [f'K{i+1}' for i in range(num_constraints)]
        self.table.setHorizontalHeaderLabels(headers)
        
        # Set column widths
        for i in range(num_constraints):
            self.table.setColumnWidth(i, 80)
        
        # Add new constraint rows with default values from task
        default_bounds = [60, 24, 8]  # Task constraints: K1≤60, K2≤24, K3≥8
        default_senses = ['<=', '<=', '>=']
        
        for i in range(num_constraints):
            # Create a frame for each constraint
            constraint_frame = QFrame()
            constraint_frame.setFrameShape(QFrame.Box)
            constraint_frame.setStyleSheet("QFrame { background-color: #f0f0f0; padding: 5px; margin: 2px; }")
            constraint_row = QHBoxLayout()
            constraint_row.setSpacing(10)
            
            # Constraint label
            label = QLabel(f'Ograniczenie {i+1}:')
            label.setMinimumWidth(100)
            label.setStyleSheet("font-weight: bold;")
            constraint_row.addWidget(label)
            
            # Formula display
            formula_label = QLabel(f'(K{i+1}ᵂ¹ × W1) + (K{i+1}ᵂ² × W2)')
            formula_label.setStyleSheet("color: #555; font-style: italic;")
            constraint_row.addWidget(formula_label)
            
            # Sense selector (<=, >=, ==)
            sense_combo = QComboBox()
            sense_combo.addItems(['<=', '>=', '=='])
            sense_combo.setCurrentText(default_senses[i] if i < len(default_senses) else '<=')
            sense_combo.setMaximumWidth(60)
            sense_combo.setStyleSheet("font-weight: bold; font-size: 14px;")
            constraint_row.addWidget(sense_combo)
            
            # Bound input
            bound_input = QLineEdit()
            bound_input.setPlaceholderText('Wartość')
            bound_input.setText(str(default_bounds[i] if i < len(default_bounds) else 10))
            bound_input.setMaximumWidth(80)
            bound_input.setAlignment(Qt.AlignRight)
            constraint_row.addWidget(bound_input)
            
            constraint_row.addStretch()
            constraint_frame.setLayout(constraint_row)
            
            self.constraints_layout.addWidget(constraint_frame)
            self.constraint_inputs.append({
                'bound': bound_input,
                'sense': sense_combo
            })
        
        # Ensure table has default values for new columns
        for i in range(2):
            for j in range(num_constraints):
                if not self.table.item(i, j):
                    item = QTableWidgetItem("1.0")
                    item.setFlags(item.flags() | Qt.ItemIsEditable)
                    self.table.setItem(i, j, item)


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
                val = self.table.item(i, j).text() if self.table.item(i, j) else "0.0"
                try:
                    row.append(float(val))
                except ValueError:
                    row.append(0.0)
            table_values.append(row)
        
        # Build constraints configuration from user inputs
        constraints_config = []
        for i, constraint_input in enumerate(self.constraint_inputs):
            if i < self.table.columnCount():
                try:
                    coef_w1 = table_values[0][i]
                    coef_w2 = table_values[1][i]
                    bound = float(constraint_input['bound'].text())
                    sense = constraint_input['sense'].currentText()
                    
                    constraints_config.append({
                        'coef_w1': coef_w1,
                        'coef_w2': coef_w2,
                        'bound': bound,
                        'sense': sense
                    })
                except (ValueError, IndexError) as e:
                    print(f"Error reading constraint {i+1}: {e}")
                    continue

        model = Model(data=table_values, income_w1=zysk_w1, income_w2=zysk_w2, constraints_config=constraints_config)
        x1, x2, obj_value, solution_type = model.solve()
        
        # Show info about solution type
        if solution_type == 'line':
            print(f"⚠️ Wykryto nieskończenie wiele rozwiązań optymalnych! Funkcja celu jest równoległa do ograniczenia.")
        elif solution_type == 'unbounded':
            print(f"⚠️ Problem nieograniczony - brak optymalnego rozwiązania!")
        else:
            print(f"✓ Znaleziono optymalne rozwiązanie (punkt): W1={x1:.2f}, W2={x2:.2f}, Wartość={obj_value:.2f}")
        
        # Get selected plot type
        plot_type = self.plot_type_combo.currentText()
        show_both = plot_type == 'Oba (statyczny + animacja)'
        
        # Adjust sizes based on number of plots
        if show_both:
            min_width, max_width = 520, 580
            min_height, max_height = 350, 420
        else:
            min_width, max_width = 650, 750  # Larger when showing only one
            min_height, max_height = 420, 500
        
        # Static plot
        if plot_type in ['Oba (statyczny + animacja)', 'Tylko statyczny']:
            fig = model.full_plot(x1, x2, obj_value, solution_type)
            canvas = FigureCanvas(fig)
            canvas.setMinimumSize(min_width, min_height)
            canvas.setMaximumSize(max_width, max_height)
            self.plot_layout.addWidget(canvas)
        
        # Animated GIF
        if plot_type in ['Oba (statyczny + animacja)', 'Tylko animacja']:
            model.animated_plot(x1, x2, obj_value, solution_type)
            gif_path = "animation.gif"
            gif_label = QLabel()
            gif_label.setAlignment(Qt.AlignCenter)
            gif_label.setScaledContents(False)  # Don't scale - use movie scaling
            movie = QMovie(gif_path)
            # Scale movie to fit the widget
            movie.setScaledSize(QSize(min_width, min_height))
            gif_label.setMovie(movie)
            movie.start()
            gif_label.setMinimumSize(min_width, min_height)
            gif_label.setMaximumSize(max_width, max_height)
            self.plot_layout.addWidget(gif_label)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
