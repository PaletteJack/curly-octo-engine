import sys, os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTextEdit, QTableWidget, 
                             QTableWidgetItem, QTabWidget, QLineEdit, QLabel, QSplitter)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
import sqlite3
import pandas as pd
from haversine import haversine, Unit

def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        return relative_path

def get_db_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, 'db.sqlite')
    else:
        return 'db.sqlite'

class SchoolExplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Curly Octo Engine")
        self.setMinimumSize(1280, 720)
        icon = QIcon(get_resource_path("app_icon.ico"))
        self.setWindowIcon(icon)
        self.tabs = QTabWidget()
        tab_bar = self.tabs.tabBar()
        tab_bar.setFixedHeight(50)
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border-top: 1px solid black;
                background: #F8F4E8;
                top: 8px;
            }
            
            QTabBar::tab {
                border: 3px solid black;
                padding: 10px 20px;
                margin: 8px 8px 0px 8px;
                min-width: 80px;
                font-weight: bold;
                text-transform: uppercase;
                background-color: white;
            }
            
            QTabBar::tab:selected {
                background: #F5624D;
            }
            
            QTabBar::tab:hover {
                background: #CD231F;
                color: white;
            }
        """)
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.tabBar().setExpanding(False)
        self.tabs.setContentsMargins(10, 10, 10, 10)
        self.setCentralWidget(self.tabs)
        self.query_tab = QueryTab()
        self.find_schools_tab = FindSchoolsTab()
        self.tabs.addTab(self.find_schools_tab, "Find Schools")
        self.tabs.addTab(self.query_tab, "Query Data")

class QueryTab(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        left_panel.setFixedWidth(300)
        query_label = QLabel("QUERY")
        query_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 16px;
                margin-bottom: 10px;
            }
        """)
        left_layout.addWidget(query_label)
        self.query_text = QTextEdit()
        self.query_text.setPlaceholderText("Enter your SQL query here...")
        left_layout.addWidget(self.query_text)
        self.run_button = QPushButton("RUN")
        self.export_button = QPushButton("EXPORT")
        button_style = """
            QPushButton {
                padding: 10px;
                margin: 5px 0;
                width: 100%;
            }
        """
        self.run_button.setStyleSheet(button_style)
        self.export_button.setStyleSheet(button_style)
        left_layout.addWidget(self.run_button)
        left_layout.addWidget(self.export_button)
        left_layout.addStretch()
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)
        self.table = QTableWidget()
        right_layout.addWidget(self.table)
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel, stretch=1)
        self.run_button.clicked.connect(self.run_query)
        self.export_button.clicked.connect(self.export_query)

    def run_query(self):
        try:
            conn = sqlite3.connect(get_db_path())
            query = self.query_text.toPlainText()
            df = pd.read_sql_query(query, conn)
            conn.close()
            num_rows = len(df)
            num_cols = len(df.columns)
            self.table.setRowCount(num_rows)
            self.table.setColumnCount(num_cols)
            self.table.setHorizontalHeaderLabels(df.columns)
            for row_idx in range(num_rows):
                for col_idx in range(num_cols):
                    value = df.iloc[row_idx, col_idx]
                    if pd.isna(value):
                        value = ""
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
            self.table.resizeColumnsToContents()
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", str(e))

    def export_query(self):
        try:
            from PySide6.QtWidgets import QFileDialog
            filename, _ = QFileDialog.getSaveFileName(
                self, "Save CSV", "", "CSV Files (*.csv)")
            
            if filename:
                conn = sqlite3.connect(get_db_path())
                query = self.query_text.toPlainText()
                df = pd.read_sql_query(query, conn)
                conn.close()
                df.to_csv(filename, index=False)

        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", str(e))

class FindSchoolsTab(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        left_panel.setFixedWidth(300)
        find_label = QLabel("FIND")
        find_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 16px;
                margin-bottom: 10px;
            }
        """)
        left_layout.addWidget(find_label)
        input_style = """
            QLineEdit {
                padding: 8px;
                margin: 5px 0;
            }
            QLabel {
                margin-top: 10px;
            }
        """
        lat_label = QLabel("Latitude:")
        self.lat_input = QLineEdit()
        self.lat_input.setStyleSheet(input_style)
        long_label = QLabel("Longitude:")
        self.long_input = QLineEdit()
        self.long_input.setStyleSheet(input_style)
        distance_label = QLabel("Max Distance (miles):")
        self.distance_input = QLineEdit()
        self.distance_input.setText("10")
        self.distance_input.setStyleSheet(input_style)
        for widget in [lat_label, self.lat_input, 
                      long_label, self.long_input,
                      distance_label, self.distance_input]:
            left_layout.addWidget(widget)
        self.find_button = QPushButton("FIND")
        self.export_button = QPushButton("EXPORT")
        
        button_style = """
            QPushButton {
                padding: 10px;
                margin: 5px 0;
                width: 100%;
            }
        """
        self.find_button.setStyleSheet(button_style)
        self.export_button.setStyleSheet(button_style)
        left_layout.addWidget(self.find_button)
        left_layout.addWidget(self.export_button)
        left_layout.addStretch()
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)
        self.table = QTableWidget()
        right_layout.addWidget(self.table)
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel, stretch=1)
        self.find_button.clicked.connect(self.find_schools)
        self.export_button.clicked.connect(self.export_schools)

    def find_schools(self):
        try:
            lat = float(self.lat_input.text())
            long = float(self.long_input.text())
            max_distance = float(self.distance_input.text())
            if lat < -90 or lat > 90:
                raise ValueError("Invalid latitude. Must be between -90 and 90.")
            if long < -180 or long > 180:
                raise ValueError("Invalid longitude. Must be between -180 and 180.")
            target_coor = (lat, long)
            conn = sqlite3.connect(get_db_path())
            query = """
            SELECT 
                school_name,
                education_agency_name,
                location_address_street_1,
                location_address_street_2,
                location_city,
                location_state,
                location_5_digit_zip_code as location_zip,
                county_name,
                grades_offered_lowest,
                grades_offered_highest,
                total_of_free_lunch_and_reducedprice_lunch_eligible,
                total_students_all_grades_includes_ae as total_students,
                total_elementarysecondary_students_excludes_ae as total_elementary,
                latitude,
                longitude
            FROM school_data
            """
            df = pd.read_sql_query(query, conn)
            conn.close()
            df['distance'] = df.apply(lambda row: haversine(
                target_coor,
                (float(row['latitude']), float(row['longitude'])),
                unit=Unit.MILES
            ), axis=1)
            nearby_schools = df[df['distance'] <= max_distance].copy()
            nearby_schools = nearby_schools.sort_values('distance')
            nearby_schools['distance'] = nearby_schools['distance'].round(2)
            self.table.clear()
            num_rows = len(nearby_schools)
            num_cols = len(nearby_schools.columns)
            self.table.setRowCount(num_rows)
            self.table.setColumnCount(num_cols)
            headers = list(nearby_schools.columns)
            self.table.setHorizontalHeaderLabels(headers)
            for row_idx in range(num_rows):
                for col_idx in range(num_cols):
                    value = nearby_schools.iloc[row_idx, col_idx]
                    if pd.isna(value):
                        value = ""
                    item = QTableWidgetItem(str(value))
                    self.table.setItem(row_idx, col_idx, item)
                    
            self.table.resizeColumnsToContents()
    
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", str(e))
            print(f"Error details: {str(e)}")

    def export_schools(self):
        try:
            from PySide6.QtWidgets import QFileDialog
            filename, _ = QFileDialog.getSaveFileName(
                self, "Save CSV", "", "CSV Files (*.csv)")
            
            if filename:
                lat = float(self.lat_input.text())
                long = float(self.long_input.text())
                max_distance = float(self.distance_input.text())
                if lat < -90 or lat > 90:
                    raise ValueError("Invalid latitude. Must be between -90 and 90.")
                if long < -180 or long > 180:
                    raise ValueError("Invalid longitude. Must be between -180 and 180.")
                conn = sqlite3.connect(get_db_path())
                query = """
                SELECT 
                    school_name,
                    education_agency_name,
                    location_address_street_1,
                    location_address_street_2,
                    location_city,
                    location_state,
                    location_5_digit_zip_code as location_zip,
                    county_name,
                    grades_offered_lowest,
                    grades_offered_highest,
                    total_of_free_lunch_and_reducedprice_lunch_eligible,
                    total_students_all_grades_includes_ae as total_students,
                    total_elementarysecondary_students_excludes_ae as total_elementary,
                    latitude,
                    longitude
                FROM school_data
                """
                df = pd.read_sql_query(query, conn)
                conn.close()
                target_coor = (lat, long)
                df['distance'] = df.apply(lambda row: haversine(
                    target_coor,
                    (float(row['latitude']), float(row['longitude'])),
                    unit=Unit.MILES
                ), axis=1)

                nearby_schools = df[df['distance'] <= max_distance].copy()
                nearby_schools = nearby_schools.sort_values('distance')
                nearby_schools['distance'] = nearby_schools['distance'].round(2)
                nearby_schools.to_csv(filename, index=False)
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", str(e))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    style_path = get_resource_path('styles.qss')
    with open(style_path, 'r') as style_file:
        style = style_file.read()
    app.setStyleSheet(style)
    window = SchoolExplorer()
    window.show()
    sys.exit(app.exec())