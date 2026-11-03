import sys,duckdb,csv
import pandas as pd
from pathlib import Path
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QLabel, QSplitter, QTabWidget, QHeaderView, QGridLayout,
                             QFrame, QHBoxLayout, QMessageBox, QSizePolicy, QDialogButtonBox, QSpinBox, QLineEdit,
                             QFormLayout, QDialog)
from PyQt5.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class ChartWidget(FigureCanvas):

    def __init__(self):
        self.figure = Figure(facecolor="#2b2b2b")
        self.ax = self.figure.add_subplot(111)
        super().__init__(self.figure)

    def clear(self):
        self.ax.clear()
        self.ax.set_facecolor("#3c3f41")


class AddEmployeeDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter un employé")
        layout = QFormLayout(self)
        self.name = QLineEdit()
        self.age = QSpinBox()
        self.age.setRange(18, 100)
        self.service = QLineEdit()
        self.salary = QSpinBox()
        self.salary.setRange(1000, 100000)
        layout.addRow("nom", self.name)
        layout.addRow("age", self.age)
        layout.addRow("service", self.service)
        layout.addRow("salary", self.salary)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

    def get_data(self):
        return {
            "nom": self.name.text(),
            "age": self.age.value(),
            "service": self.service.text(),
            "salary": self.salary.value()
        }

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("DuckDB Dashboard")
        self.resize(1400, 800)
        BASE_DIR = Path(__file__).parent
        icon_path = BASE_DIR / "icons" / "dashboard.png"
        self.setWindowIcon(QIcon(str(icon_path)))
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        title = QLabel("Dashboard Employés")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(""" font-size:24px; font-weight:bold; color:white; padding:10px; """)
        layout.addWidget(title)
        button_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("🔄 Recharger")
        self.refresh_btn.clicked.connect(self.load_data)
        self.add_btn = QPushButton("➕ Ajouter")
        self.add_btn.clicked.connect(self.add_employee)
        button_layout.addWidget(self.add_btn)
        self.quit_btn = QPushButton("❌ Quitter")
        self.quit_btn.clicked.connect(self.quit_application)

        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.quit_btn)
        self.quit_btn.setStyleSheet("""
            QPushButton { background:#d32f2f; color:white; border:none; padding:8px; border-radius:5px; font-weight:bold; }
            QPushButton:hover { background:#f44336; }
        """)
        splitter = QSplitter(Qt.Horizontal)
        #
        # TABLE
        #
        self.table = QTableWidget()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellChanged.connect(self.on_cell_changed)
        splitter.addWidget(self.table)
        #
        # TABS
        #
        self.tabs = QTabWidget()
        self.salary_chart = ChartWidget()
        self.service_chart = ChartWidget()
        self.pie_chart = ChartWidget()
        self.kpi_widget = QWidget()
        self.tabs.addTab(self.kpi_widget, "📊 KPI")
        self.tabs.addTab(self.salary_chart, "📈 salarys")
        self.tabs.addTab(self.service_chart, "🏢 Par service")
        self.tabs.addTab(self.pie_chart, "👥 Répartition")
        splitter.addWidget(self.tabs)
        splitter.setSizes([500, 900])
        layout.addWidget(splitter)
        layout.addLayout(button_layout)
        self.setStyleSheet("""
            QMainWindow { background:#2b2b2b; }
            QLabel { color:white; }
            QTableWidget { background:#3c3f41; color:white; gridline-color:#666; }
            QHeaderView::section { background:#4e9af1; color:white; padding:5px; border:none; }
            QPushButton { background:#4e9af1; color:white; border:none; padding:8px; border-radius:5px; }
            QPushButton:hover { background:#67abff; }
            QTabWidget::pane { border:1px solid #555; }
            QTabBar::tab { background:#3c3f41; color:white; padding:10px; min-width:150px; }
            QTabBar::tab:selected { background:#4e9af1; }
        """)
        self.create_kpi_tab()
        self.load_data()

    def populate_table(self, df):

        self.table.blockSignals(True)
        self.table.setRowCount(len(df))
        self.table.setColumnCount(len(df.columns))
        self.table.setHorizontalHeaderLabels(df.columns)
        for row in range(len(df)):
            for col in range(len(df.columns)):
                item = QTableWidgetItem(str(df.iloc[row, col]))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)
        self.table.resizeColumnsToContents()
        self.table.blockSignals(False)

    def on_cell_changed(self, row, col):
        print(f"Modification : ligne={row}, colonne={col}")
        self.save_table_to_csv()
        self.load_data()

    def save_table_to_csv(self):
        rows = self.table.rowCount()
        cols = self.table.columnCount()
        headers = [self.table.horizontalHeaderItem(col).text() for col in range(cols)]
        data = []
        for row in range(rows):
            row_data = []
            for col in range(cols):
                item = self.table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        df = pd.DataFrame(data, columns=headers)
        df.to_csv("employees.csv", sep=",", index=False)

    def add_employee(self):
        dialog = AddEmployeeDialog(self)
        if dialog.exec_():
            data = dialog.get_data()
            csv_file = "employees.csv"
            df = pd.read_csv(csv_file, sep=None, engine="python")
            df["id"] = pd.to_numeric(df["id"], errors="coerce")
            max_id = df["id"].max()
            new_id = (1 if pd.isna(max_id) else int(max_id) + 1)
            with open(csv_file, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([new_id, data["nom"], data["age"], data["service"], data["salary"]])
            self.load_data()

    def load_data(self):

        df = duckdb.sql(""" SELECT * FROM read_csv_auto('employees.csv') ORDER BY salary DESC """).df()
        # self.fill_table(df)
        self.populate_table(df)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.update_kpis()
        self.draw_salary_chart(df)
        self.draw_service_chart()
        self.draw_pie_chart()

    def fill_table(self, df):

        self.table.clear()
        self.table.setRowCount(len(df))
        self.table.setColumnCount(len(df.columns))
        self.table.setHorizontalHeaderLabels(df.columns)
        for row in range(len(df)):
            for col in range(len(df.columns)):
                item = QTableWidgetItem(str(df.iloc[row, col]))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)
        self.table.resizeColumnsToContents()

    def create_kpi_tab(self):

        layout = QGridLayout(self.kpi_widget)
        self.card_employees = QLabel()
        self.card_avg = QLabel()
        self.card_max = QLabel()
        self.card_min = QLabel()
        cards = [self.card_employees, self.card_avg, self.card_max, self.card_min]
        for card in cards:
            card.setAlignment(Qt.AlignCenter)
            card.setMinimumHeight(180)
            card.setStyleSheet("""
                QLabel { background:#3c3f41; color:white; border-radius:15px; font-size:20px; font-weight:bold; padding:20px; }
            """)
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.card_employees, 0, 0)
        layout.addWidget(self.card_avg, 0, 1)
        layout.addWidget(self.card_max, 1, 0)
        layout.addWidget(self.card_min, 1, 1)

    def update_kpis(self):
        stats = duckdb.sql("""
            SELECT COUNT(*) AS total, AVG(salary) AS avg_salary, MAX(salary) AS max_salary, MIN(salary) AS min_salary
            FROM read_csv_auto('employees.csv')
        """).fetchone()

        total, avg_salary, max_salary, min_salary = stats
        self.card_employees.setText(f"👥\nEmployés\n\n{total}")
        self.card_avg.setText(f"💰\nsalary moyen\n\n{avg_salary:.0f} €")
        self.card_max.setText(f"🚀\nsalary max\n\n{max_salary} €")
        self.card_min.setText(f"📉\nsalary min\n\n{min_salary} €")

    def draw_salary_chart(self, df):

        chart = self.salary_chart
        chart.clear()
        bars = chart.ax.bar(df["nom"], df["salary"], color="#4e9af1")
        chart.ax.set_title("salarys par employé", color="white")
        chart.ax.tick_params(colors="white")
        for bar in bars:
            value = int(bar.get_height())
            chart.ax.text(bar.get_x() + bar.get_width()/2, value, f"{value}€", ha="center", color="white")
        chart.draw()

    def draw_service_chart(self):

        df = duckdb.sql("""
                            SELECT service, AVG(salary) salary_moyen
                            FROM read_csv_auto('employees.csv')
                            GROUP BY service
                            ORDER BY salary_moyen DESC
                        """).df()
        chart = self.service_chart
        chart.clear()
        bars = chart.ax.bar(df["service"], df["salary_moyen"], color="#ff9800")
        chart.ax.set_title("salaire moyen par service", color="white")
        chart.ax.tick_params(colors="white")
        for bar in bars:
            value = int(bar.get_height())
            chart.ax.text(bar.get_x() + bar.get_width()/2, value, f"{value}€", ha="center", color="white")
        chart.draw()

    def draw_pie_chart(self):

        df = duckdb.sql(""" SELECT service, COUNT(*) nb FROM read_csv_auto('employees.csv') GROUP BY service """).df()
        chart = self.pie_chart
        chart.ax.clear()
        colors = ["#2196F3", "#4CAF50", "#FF9800", "#E91E63"]
        chart.ax.pie(df["nb"], labels=df["service"],colors=colors, autopct="%1.1f%%", startangle=90,
                               textprops={"color": "white", "fontsize": 12, "fontweight": "bold",},
                               labeldistance=1.15,
                               pctdistance=0.75
                            )
        chart.ax.set_title("Répartition des employés", color="white")
        chart.draw()

    def quit_application(self):

        msg = QMessageBox(self)
        msg.setWindowTitle("Confirmation")
        msg.setText("Voulez-vous vraiment quitter l'application ?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        msg.setStyleSheet("""
            QMessageBox { background-color: #2b2b2b; }
            QLabel { color: white; font-size: 14px; min-width: 350px; }
            QPushButton { background-color: #d32f2f; color: white; border-radius: 5px; padding: 8px; min-width: 100px; }
            QPushButton:hover { background-color: #f44336; }
        """)
        if msg.exec_() == QMessageBox.Yes:
            self.close()

if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())