import sys
import os
import copy
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QMessageBox,
    QSpinBox,
    QFormLayout,
    QScrollArea,
    QRadioButton,
    QButtonGroup,
)

# Ensure we can import the local model.py in the same folder
sys.path.insert(0, os.path.dirname(__file__))
from model import Model


class SimplexGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Programowanie liniowe - Metoda Simplex")
        self.model = Model()

        # Snapshot initial model state so "Przeładuj model" can restore it
        self._initial_model = copy.deepcopy(self.model)

        self._build_ui()
        self.load_model_into_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        central.setLayout(layout)

        # Kontrolki wymiarów (liczba zmiennych i ograniczeń)
        dims_layout = QHBoxLayout()
        layout.addLayout(dims_layout)
        dims_layout.addWidget(QLabel("Liczba zmiennych (n):"))
        self.n_spin = QSpinBox()
        self.n_spin.setMinimum(1)
        self.n_spin.setMaximum(20)
        self.n_spin.valueChanged.connect(self.on_dims_changed)
        dims_layout.addWidget(self.n_spin)

        dims_layout.addWidget(QLabel("Liczba ograniczeń (m):"))
        self.m_spin = QSpinBox()
        self.m_spin.setMinimum(1)
        self.m_spin.setMaximum(50)
        self.m_spin.valueChanged.connect(self.on_dims_changed)
        dims_layout.addWidget(self.m_spin)

        # Wybór typu optymalizacji
        opt_layout = QHBoxLayout()
        layout.addLayout(opt_layout)
        opt_layout.addWidget(QLabel("Typ optymalizacji:"))
        
        self.opt_button_group = QButtonGroup()
        self.min_radio = QRadioButton("Minimalizacja")
        self.max_radio = QRadioButton("Maksymalizacja")
        self.min_radio.setChecked(True)  # Domyślnie minimalizacja
        
        self.opt_button_group.addButton(self.min_radio)
        self.opt_button_group.addButton(self.max_radio)
        
        opt_layout.addWidget(self.min_radio)
        opt_layout.addWidget(self.max_radio)
        opt_layout.addStretch()

        # Controls: table for coefficients and b
        top_row = QHBoxLayout()
        layout.addLayout(top_row)

        self.table = QTableWidget()

        # Put right-side controls in their own widget so we can set stretch/width
        right_widget = QWidget()
        right_col = QVBoxLayout()
        right_widget.setLayout(right_col)
        right_widget.setMinimumWidth(280)
        # Add table and right widget with stretch so right widget keeps space
        top_row.addWidget(self.table, 3)
        top_row.addWidget(right_widget, 1)

        # Objective coefficients area
        right_col.addWidget(QLabel("Współczynniki funkcji celu (c):"))
        # Use a form layout for aligned label+field rows
        self.c_edits = []
        self.c_container = QFormLayout()
        # Put form inside a scroll area in case n is large
        form_widget = QWidget()
        form_widget.setLayout(self.c_container)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(form_widget)
        right_col.addWidget(self.scroll)

        right_col.addWidget(QLabel("Indeksy bazowe (oddzielone przecinkami, 0-based):"))
        self.base_edit = QLineEdit()
        right_col.addWidget(self.base_edit)

        right_col.addWidget(QLabel("Wartości cb (oddzielone przecinkami):"))
        self.cb_edit = QLineEdit()
        right_col.addWidget(self.cb_edit)

        # Buttons
        btn_row = QHBoxLayout()
        layout.addLayout(btn_row)

        self.apply_btn = QPushButton("Zastosuj do modelu")
        self.apply_btn.clicked.connect(self.apply_ui_to_model)
        btn_row.addWidget(self.apply_btn)

        self.solve_btn = QPushButton("Rozwiąż")
        self.solve_btn.clicked.connect(self.solve_model)
        btn_row.addWidget(self.solve_btn)

        self.reset_btn = QPushButton("Przeładuj model")
        self.reset_btn.clicked.connect(self.reset_model)
        btn_row.addWidget(self.reset_btn)

        # Log / output
        layout.addWidget(QLabel("Wynik:"))
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)

    def load_model_into_ui(self):
        """Load current model values into the widgets."""
        m = self.model.m
        n = self.model.n

        # ustaw spinboxy zgodnie z modelem
        self.n_spin.blockSignals(True)
        self.m_spin.blockSignals(True)
        self.n_spin.setValue(n)
        self.m_spin.setValue(m)
        self.n_spin.blockSignals(False)
        self.m_spin.blockSignals(False)
        
        # Ustaw typ optymalizacji
        if hasattr(self.model, 'optimization_type'):
            if self.model.optimization_type == 'max':
                self.max_radio.setChecked(True)
            else:
                self.min_radio.setChecked(True)
        else:
            self.min_radio.setChecked(True)

        # Setup table with n variable columns + 1 for b
        self.table.clear()
        self.table.setRowCount(m)
        self.table.setColumnCount(n + 1)
        headers = [f"x{i+1}" for i in range(n)] + ["b"]
        self.table.setHorizontalHeaderLabels(headers)

        # Fill rows from model.x1, model.x2, ... (support generic variable lists if present)
        var_lists = []
        for var_idx in range(1, n + 1):
            attr = f"x{var_idx}"
            vals = getattr(self.model, attr, [0] * m)
            var_lists.append(vals)

        for i in range(m):
            for j in range(n):
                try:
                    val = float(var_lists[j][i])
                except Exception:
                    val = 0.0
                item = QTableWidgetItem(str(val))
                self.table.setItem(i, j, item)

            # b column
            try:
                bval = float(self.model.b[i])
            except Exception:
                bval = 0.0
            self.table.setItem(i, n, QTableWidgetItem(str(bval)))

        # Edycja współczynników c
        # Clear previous form rows
        # QFormLayout doesn't provide a direct clear, so remove children
        while self.c_container.rowCount() > 0:
            # remove last row
            row = self.c_container.rowCount() - 1
            item_label = self.c_container.itemAt(row, QFormLayout.LabelRole)
            item_field = self.c_container.itemAt(row, QFormLayout.FieldRole)
            if item_label:
                w = item_label.widget()
                if w:
                    w.deleteLater()
            if item_field:
                w2 = item_field.widget()
                if w2:
                    w2.deleteLater()
            # note: there's no direct removeRow in older PyQt, rely on re-creating layout below
            break
        # Recreate form: easier to replace form_widget
        # Create fresh form and widget
        self.c_container = QFormLayout()
        form_widget = QWidget()
        form_widget.setLayout(self.c_container)
        self.scroll.setWidget(form_widget)
        self.c_edits = []
        for j in range(n):
            lbl = QLabel(f"c{j+1}:")
            edit = QLineEdit(str(self.model.c[j] if j < len(self.model.c) else 0.0))
            self.c_container.addRow(lbl, edit)
            self.c_edits.append(edit)

        # base and cb
        self.base_edit.setText(
            ",".join(str(x) for x in getattr(self.model, "base", []))
        )
        self.cb_edit.setText(
            ",".join(str(x) for x in getattr(self.model, "cb", []))
        )

        self.append_log("Model załadowany do UI")

    def apply_ui_to_model(self):
        """Apply values from UI to the model instance."""
        m = self.model.m
        n = self.model.n
        try:
            # Ustaw typ optymalizacji
            if self.max_radio.isChecked():
                self.model.optimization_type = 'max'
            else:
                self.model.optimization_type = 'min'
            
            # Read table columns into x1..xn and b
            for j in range(1, n + 1):
                col_vals = []
                for i in range(m):
                    item = self.table.item(i, j - 1)
                    if item is None:
                        v = 0.0
                    else:
                        v = float(item.text())
                    col_vals.append(v)
                setattr(self.model, f"x{j}", col_vals)

            # b
            new_b = []
            for i in range(m):
                item = self.table.item(i, n)
                new_b.append(float(item.text()) if item is not None else 0.0)
            self.model.b = new_b

            # c
            new_c = []
            for edit in self.c_edits:
                new_c.append(float(edit.text()))
            self.model.c = new_c
            # Zachowaj oryginalne współczynniki przed przekształceniem
            if hasattr(self.model, 'c_original'):
                self.model.c_original = new_c.copy()

            # base
            base_text = self.base_edit.text().strip()
            if base_text:
                base_vals = [int(x.strip()) for x in base_text.split(",") if x.strip()]
                self.model.base = base_vals

            # cb
            cb_text = self.cb_edit.text().strip()
            if cb_text:
                cb_vals = [float(x.strip()) for x in cb_text.split(",") if x.strip()]
                self.model.cb = cb_vals

            # Upewnij się, że długości list odpowiadają nowym wymiarom
            self._ensure_model_shapes()

            self.append_log("Wartości zastosowane do modelu")
            QMessageBox.information(self, "Zastosowano", "Wartości zastosowane do modelu.")
        except Exception as e:
            QMessageBox.warning(self, "Błąd", f"Nie można zastosować wartości: {e}")
            self.append_log(f"Nie można zastosować wartości: {e}")

    def solve_model(self):
        """Apply values, run solver, and display result."""
        # First apply UI values to model
        self.apply_ui_to_model()
        opt_type_label = "Maksymalizacja" if self.model.optimization_type == 'max' else "Minimalizacja"
        self.append_log(f"Uruchamianie solvera (typ: {opt_type_label})...")
        try:
            x1, x2, obj_value, sol_type = self.model.solve()

            # Pokaż w polu tekstowym tylko tabele iteracji z modelu (jeżeli są)
            iterations = getattr(self.model, 'iteration_tableaus', None)
            if iterations:
                # ustaw cały tekst na serializowane tabele (oddzielone pustą linią)
                self.log.setPlainText('\n\n'.join(iterations))
            else:
                # fallback: dodaj podstawowe info
                self.append_log(f"Wynik: x1={x1}, x2={x2}, obj={obj_value}, typ={sol_type}")

            # Pokaż wszystkie zmienne decyzyjne w okienku wyniku
            sol_vec = getattr(self.model, 'solution_vector', None)
            n = getattr(self.model, 'n', 2)
            result_lines = []
            if sol_vec:
                for j in range(n):
                    # upewnij się, że sol_vec ma odpowiednią długość
                    val = sol_vec[j] if j < len(sol_vec) else 0.0
                    result_lines.append(f"x{j+1} = {val}")
            else:
                # fallback na wartości zwrócone bezpośrednio
                result_lines.append(f"x1 = {x1}")
                result_lines.append(f"x2 = {x2}")

            # Dodaj krótkie podsumowanie wartości celu
            result_lines.append(f"Funkcja celu = {obj_value}\nTyp rozwiązania: {sol_type}")

            # Doklej wynik pod tabelami (jeżeli tabele są pokazane - oddzieli je)
            if iterations:
                # dopisz do istniejącego tekstu
                self.log.append('\n'.join(result_lines))
            else:
                # zastąp log krótkim wynikiem
                self.log.append('\n'.join(result_lines))

            QMessageBox.information(
                self, 
                "Wynik", 
                f"Typ optymalizacji: {opt_type_label}\nTyp rozwiązania: {sol_type}\nWartość funkcji celu: {obj_value}"
            )
        except Exception as e:
            QMessageBox.warning(self, "Błąd solvera", str(e))
            self.append_log(f"Błąd solvera: {e}")

    def append_log(self, message: str):
        self.log.append(message)

    def on_dims_changed(self):
        """Wywołane gdy zmieni się liczba zmiennych lub ograniczeń (spinboxy)."""
        new_n = int(self.n_spin.value())
        new_m = int(self.m_spin.value())
        self.rebuild_model_structure(new_m, new_n)
        self.load_model_into_ui()

    def rebuild_model_structure(self, new_m: int, new_n: int):
        """Dostosowuje struktury w obiekcie Model do nowych wymiarów.

        - tworzy/usuwa listy x1..xn
        - dopasowuje długość list b, c, cb oraz base
        """
        # Zaktualizuj m i n
        self.model.m = new_m
        self.model.n = new_n

        # Dopasuj listy x1..xn
        for j in range(1, new_n + 1):
            name = f"x{j}"
            vals = getattr(self.model, name, None)
            if vals is None:
                # utwórz listę długości m
                setattr(self.model, name, [0.0] * new_m)
            else:
                # dopasuj długość
                if len(vals) < new_m:
                    vals = vals + [0.0] * (new_m - len(vals))
                elif len(vals) > new_m:
                    vals = vals[:new_m]
                setattr(self.model, name, vals)

        # Jeśli jest mniej zmiennych niż wcześniej, przytnij dodatkowe atrybuty
        # (nie krytyczne, pozostawiamy je, ale n steruje widocznością)

        # Dopasuj b
        b = getattr(self.model, "b", [])
        if len(b) < new_m:
            b = b + [0.0] * (new_m - len(b))
        else:
            b = b[:new_m]
        self.model.b = b

        # Dopasuj c
        c = getattr(self.model, "c", [])
        if len(c) < new_n:
            c = c + [0.0] * (new_n - len(c))
        else:
            c = c[:new_n]
        self.model.c = c
        
        # Dopasuj c_original
        if not hasattr(self.model, 'c_original'):
            self.model.c_original = c.copy()
        else:
            c_orig = self.model.c_original
            if len(c_orig) < new_n:
                c_orig = c_orig + [0.0] * (new_n - len(c_orig))
            else:
                c_orig = c_orig[:new_n]
            self.model.c_original = c_orig

        # Dopasuj base (domyślnie ustaw bazę na zmienne sztuczne/slackowe)
        base = getattr(self.model, "base", [])
        if len(base) < new_m:
            # ustaw domyślnie kolejne indeksy od new_n (0-based)
            base = [new_n + i for i in range(new_m)]
        else:
            base = base[:new_m]
        self.model.base = base

        # Dopasuj cb
        cb = getattr(self.model, "cb", [])
        if len(cb) < new_m:
            cb = cb + [0.0] * (new_m - len(cb))
        else:
            cb = cb[:new_m]
        self.model.cb = cb

    def _ensure_model_shapes(self):
        """Mała helperka, by po zastosowaniu wartości upewnić się, że
        listy w modelu mają poprawne rozmiary (na wypadek błędnych danych z UI)."""
        self.rebuild_model_structure(self.model.m, self.model.n)

    def reset_model(self):
        """Przywróć model i UI do stanu początkowego zapisanego przy starcie GUI."""
        # restore a deep copy of the initial model
        self.model = copy.deepcopy(self._initial_model)
        # ensure spinboxes reflect restored model and UI rebuilt
        try:
            self.n_spin.blockSignals(True)
            self.m_spin.blockSignals(True)
            self.n_spin.setValue(self.model.n)
            self.m_spin.setValue(self.model.m)
        finally:
            self.n_spin.blockSignals(False)
            self.m_spin.blockSignals(False)

        # Rebuild shapes and reload UI
        self.rebuild_model_structure(self.model.m, self.model.n)
        self.load_model_into_ui()
        self.append_log("Model przywrócony do stanu początkowego")


def main():
    app = QApplication(sys.argv)
    win = SimplexGUI()
    win.resize(800, 600)
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
