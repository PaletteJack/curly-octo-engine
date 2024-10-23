import sys, os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTextEdit, QTableWidget, 
                             QTableWidgetItem, QTabWidget, QLineEdit, QLabel)
from PySide6.QtGui import QIcon
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
        return '../db.sqlite'

class SchoolExplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Curly Octo Engine")
        self.setMinimumSize(800, 600)
        icon = QIcon(get_resource_path("app_icon.ico"))
        self.setWindowIcon(icon)

        # Create tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Create tabs
        self.query_tab = QueryTab()
        self.find_schools_tab = FindSchoolsTab()

        # Add tabs
        self.tabs.addTab(self.query_tab, "Query Data")
        self.tabs.addTab(self.find_schools_tab, "Find Schools")

class QueryTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # Query text area
        self.query_text = QTextEdit()
        self.query_text.setPlaceholderText("Enter your SQL query here...")
        self.query_text.setText("SELECT school_name, location_city FROM school_data LIMIT 10")
        layout.addWidget(self.query_text)

        # Buttons
        button_layout = QHBoxLayout()
        self.run_button = QPushButton("Run Query")
        self.export_button = QPushButton("Export CSV")
        self.run_button.clicked.connect(self.run_query)
        self.export_button.clicked.connect(self.export_query)
        button_layout.addWidget(self.run_button)
        button_layout.addWidget(self.export_button)
        layout.addLayout(button_layout)

        # Results table
        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.setLayout(layout)

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
        layout = QVBoxLayout()

        # Input fields
        self.lat_input = QLineEdit()
        self.long_input = QLineEdit()
        self.distance_input = QLineEdit()
        self.distance_input.setText("10")  # Default max distance

        # Labels
        layout.addWidget(QLabel("Latitude:"))
        layout.addWidget(self.lat_input)
        layout.addWidget(QLabel("Longitude:"))
        layout.addWidget(self.long_input)
        layout.addWidget(QLabel("Max Distance (miles):"))
        layout.addWidget(self.distance_input)

        # Buttons
        button_layout = QHBoxLayout()
        self.find_button = QPushButton("Find Schools")
        self.export_button = QPushButton("Export Schools")
        self.find_button.clicked.connect(self.find_schools)
        self.export_button.clicked.connect(self.export_schools)
        button_layout.addWidget(self.find_button)
        button_layout.addWidget(self.export_button)
        layout.addLayout(button_layout)

        # Results table
        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.setLayout(layout)

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
    
            # Clear the table first
            self.table.clear()
            
            # Set up table dimensions
            num_rows = len(nearby_schools)
            num_cols = len(nearby_schools.columns)
            self.table.setRowCount(num_rows)
            self.table.setColumnCount(num_cols)
            
            # Set headers
            headers = list(nearby_schools.columns)
            self.table.setHorizontalHeaderLabels(headers)
            
            # Populate data
            for row_idx in range(num_rows):
                for col_idx in range(num_cols):
                    value = nearby_schools.iloc[row_idx, col_idx]
                    if pd.isna(value):  # Handle NaN values
                        value = ""
                    item = QTableWidgetItem(str(value))
                    self.table.setItem(row_idx, col_idx, item)
                    
            self.table.resizeColumnsToContents()
    
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", str(e))
            print(f"Error details: {str(e)}")  # Print to console for debugging

    def export_schools(self):
        try:
            from PySide6.QtWidgets import QFileDialog
            filename, _ = QFileDialog.getSaveFileName(
                self, "Save CSV", "", "CSV Files (*.csv)")
            
            if filename:
                # Reuse find_schools logic but save to CSV
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