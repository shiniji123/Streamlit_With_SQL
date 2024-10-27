import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
    QRadioButton, QButtonGroup, QVBoxLayout, QHBoxLayout, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QGridLayout, QGroupBox,
    QAbstractItemView
)
from PyQt5.QtCore import Qt
import mysql.connector
from datetime import date


# ฟังก์ชันสำหรับเชื่อมต่อฐานข้อมูลในฐานะ Admin
def connect_to_db_admin():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="sesar123",
        database="education_sector"
    )


# ฟังก์ชันสำหรับเชื่อมต่อฐานข้อมูลในฐานะ Student
def connect_to_db_student():
    return mysql.connector.connect(
        host="localhost",
        user="student",
        password="1234",
        database="education_sector"
    )


# คลาสสำหรับการเชื่อมต่อและจัดการฐานข้อมูล
class DatabaseManager:
    def __init__(self, role):
        self.conn = None
        self.cursor = None
        self.role = role
        self.connect_to_db()

    def connect_to_db(self):
        try:
            if self.role == 'Admin':
                self.conn = connect_to_db_admin()
            else:
                self.conn = connect_to_db_student()
            self.cursor = self.conn.cursor()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            QMessageBox.critical(None, "Database Error", f"Cannot connect to database: {err}")

    def close_connection(self):
        if self.conn.is_connected():
            self.cursor.close()
            self.conn.close()

    def show_table_columns(self, table_name):
        try:
            self.cursor.execute(f"DESCRIBE {table_name}")
            columns = self.cursor.fetchall()
            column_names = [column[0] for column in columns]
            return column_names
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            QMessageBox.critical(None, "Database Error", f"Error fetching columns: {err}")
            return []

    def insert_data(self, table_name, columns, values):
        try:
            columns_str = ','.join(columns)
            placeholders = ','.join(['%s'] * len(values))
            query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
            self.cursor.execute(query, values)
            self.conn.commit()
            print(f"1 record inserted successfully into {table_name}")
            QMessageBox.information(None, "Success", f"Data inserted into {table_name} successfully.")
        except mysql.connector.Error as error:
            print(f"Failed to insert data into MySQL table {table_name}: {error}")
            QMessageBox.critical(None, "Database Error", f"Failed to insert data: {error}")

    def delete_data(self, table_name, condition):
        try:
            query = f"DELETE FROM {table_name} WHERE {condition}"
            self.cursor.execute(query)
            self.conn.commit()
            print(f"Record(s) deleted successfully from {table_name} where {condition}")
            QMessageBox.information(None, "Success", f"Data deleted from {table_name} successfully.")
        except mysql.connector.Error as error:
            print(f"Failed to delete data from MySQL table {table_name}: {error}")
            QMessageBox.critical(None, "Database Error", f"Failed to delete data: {error}")

    def update_data(self, table_name, updates, conditions):
        try:
            set_clause = ', '.join([f"{column} = %s" for column in updates.keys()])
            condition_clause = ' AND '.join(conditions)
            query = f"UPDATE {table_name} SET {set_clause} WHERE {condition_clause}"
            self.cursor.execute(query, list(updates.values()))
            self.conn.commit()
            print(f"Record(s) updated successfully in {table_name} where {condition_clause}")
            QMessageBox.information(None, "Success", f"Data updated in {table_name} successfully.")
        except mysql.connector.Error as error:
            print(f"Failed to update data in MySQL table {table_name}: {error}")
            QMessageBox.critical(None, "Database Error", f"Failed to update data: {error}")


# คลาสสำหรับส่วนติดต่อผู้ใช้
class Application(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Enrollment System")
        self.setGeometry(100, 100, 800, 600)
        self.db_manager = None
        self.user_role = None  # 'Admin' or 'Student'
        self.user_id = None  # 'admin_id' or 'student_id'
        self.initUI()

    def initUI(self):
        self.login_screen()

    def login_screen(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        label_title = QLabel("ระบบลงทะเบียนนักศึกษา")
        label_title.setAlignment(Qt.AlignCenter)
        label_title.setStyleSheet("font-size: 24px;")

        # สร้างปุ่มเลือกบทบาท
        self.role_var = QButtonGroup()
        radio_student = QRadioButton("Student")
        radio_student.setChecked(True)
        radio_admin = QRadioButton("Admin")
        self.role_var.addButton(radio_student)
        self.role_var.addButton(radio_admin)

        hbox_role = QHBoxLayout()
        hbox_role.addWidget(QLabel("เข้าสู่ระบบในฐานะ"))
        hbox_role.addWidget(radio_student)
        hbox_role.addWidget(radio_admin)

        # สร้างฟิลด์สำหรับกรอก User ID และ Password
        self.entry_id = QLineEdit()
        self.entry_password = QLineEdit()
        self.entry_password.setEchoMode(QLineEdit.Password)

        form_layout = QVBoxLayout()
        form_layout.addLayout(hbox_role)
        form_layout.addWidget(QLabel("User ID"))
        form_layout.addWidget(self.entry_id)
        form_layout.addWidget(QLabel("Password"))
        form_layout.addWidget(self.entry_password)

        # ปุ่มเข้าสู่ระบบ
        btn_login = QPushButton("เข้าสู่ระบบ")
        btn_login.clicked.connect(self.login)

        vbox_main = QVBoxLayout()
        vbox_main.addWidget(label_title)
        vbox_main.addLayout(form_layout)
        vbox_main.addWidget(btn_login)
        vbox_main.setAlignment(btn_login, Qt.AlignCenter)

        central_widget.setLayout(vbox_main)
        self.show()

    def login(self):
        user_id = self.entry_id.text()
        password = self.entry_password.text()
        self.user_role = 'Admin' if self.role_var.buttons()[1].isChecked() else 'Student'

        if self.user_role == 'Admin':
            # เชื่อมต่อฐานข้อมูลในฐานะ Admin
            self.db_manager = DatabaseManager('Admin')
            query = "SELECT * FROM Admins WHERE admin_id=%s AND admin_password=%s"
        else:
            # เชื่อมต่อฐานข้อมูลในฐานะ Student
            self.db_manager = DatabaseManager('Student')
            query = "SELECT * FROM Students WHERE student_id=%s AND student_password=%s"

        self.db_manager.cursor.execute(query, (user_id, password))
        result = self.db_manager.cursor.fetchone()

        if result:
            QMessageBox.information(self, "เข้าสู่ระบบสำเร็จ", f"ยินดีต้อนรับคุณ {result[1]} {result[2]}")
            self.user_id = user_id
            if self.user_role == 'Admin':
                self.show_all_enrollments()
            else:
                self.show_enrollments()
        else:
            QMessageBox.warning(self, "ข้อผิดพลาด", "รหัสผู้ใช้หรือรหัสผ่านของคุณไม่ถูกต้อง")
            self.db_manager.close_connection()
            self.db_manager = None

    def show_enrollments(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        label = QLabel("ข้อมูลการลงทะเบียนของคุณ")
        label.setStyleSheet("font-size: 18px;")
        label.setAlignment(Qt.AlignCenter)

        table = QTableWidget()
        columns = ['student_id', 'first_name', 'last_name', 'course_id', 'course_name', 'credits', 'semester', 'year',
                   'grade']
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)

        query = '''
            SELECT s.student_id, s.first_name, s.last_name, c.course_id, c.course_name, c.credits, e.semester, e.year, e.grade
            FROM Students s
            JOIN Enrollments e ON s.student_id = e.student_id
            JOIN Courses c ON e.course_id = c.course_id
            WHERE s.student_id = %s
        '''
        self.db_manager.cursor.execute(query, (self.user_id,))
        results = self.db_manager.cursor.fetchall()

        table.setRowCount(len(results))
        for row_num, row_data in enumerate(results):
            for col_num, data in enumerate(row_data):
                table.setItem(row_num, col_num, QTableWidgetItem(str(data)))

        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        btn_add_course = QPushButton("Add รายวิชา")
        btn_add_course.clicked.connect(self.add_courses)

        btn_logout = QPushButton("Logout")
        btn_logout.clicked.connect(self.logout)

        hbox_buttons = QHBoxLayout()
        hbox_buttons.addWidget(btn_add_course)
        hbox_buttons.addWidget(btn_logout)

        vbox_main = QVBoxLayout()
        vbox_main.addWidget(label)
        vbox_main.addWidget(table)
        vbox_main.addLayout(hbox_buttons)

        central_widget.setLayout(vbox_main)
        self.show()

    def show_all_enrollments(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        label = QLabel("ข้อมูลการลงทะเบียนของนักศึกษาทุกคน")
        label.setStyleSheet("font-size: 18px;")
        label.setAlignment(Qt.AlignCenter)

        table = QTableWidget()
        columns = ['student_id', 'first_name', 'last_name', 'course_id', 'course_name', 'credits', 'semester', 'year',
                   'grade']
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)

        query = '''
            SELECT s.student_id, s.first_name, s.last_name, c.course_id, c.course_name, c.credits, e.semester, e.year, e.grade
            FROM Students s
            JOIN Enrollments e ON s.student_id = e.student_id
            JOIN Courses c ON e.course_id = c.course_id
        '''
        self.db_manager.cursor.execute(query)
        results = self.db_manager.cursor.fetchall()

        table.setRowCount(len(results))
        for row_num, row_data in enumerate(results):
            for col_num, data in enumerate(row_data):
                table.setItem(row_num, col_num, QTableWidgetItem(str(data)))

        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        btn_manage_data = QPushButton("Manage Data")
        btn_manage_data.clicked.connect(self.manage_data)

        btn_logout = QPushButton("Logout")
        btn_logout.clicked.connect(self.logout)

        hbox_buttons = QHBoxLayout()
        hbox_buttons.addWidget(btn_manage_data)
        hbox_buttons.addWidget(btn_logout)

        vbox_main = QVBoxLayout()
        vbox_main.addWidget(label)
        vbox_main.addWidget(table)
        vbox_main.addLayout(hbox_buttons)

        central_widget.setLayout(vbox_main)
        self.show()

    def logout(self):
        self.user_id = None
        self.user_role = None
        if self.db_manager:
            self.db_manager.close_connection()
            self.db_manager = None
        self.login_screen()

    def add_courses(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        label = QLabel("เลือกวิชาที่ต้องการเพิ่ม (สูงสุด 3 วิชา)")
        label.setStyleSheet("font-size: 18px;")
        label.setAlignment(Qt.AlignCenter)

        table = QTableWidget()
        columns = ['course_id', 'course_name', 'credits', 'department_id', 'instructor_id']
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)

        # แสดงเฉพาะรายวิชาที่นักศึกษายังไม่ได้ลงทะเบียน
        query = '''
            SELECT * FROM Courses c
            WHERE c.course_id NOT IN (
                SELECT e.course_id FROM Enrollments e WHERE e.student_id = %s
            )
        '''
        self.db_manager.cursor.execute(query, (self.user_id,))
        results = self.db_manager.cursor.fetchall()

        table.setRowCount(len(results))
        for row_num, row_data in enumerate(results):
            for col_num, data in enumerate(row_data):
                table.setItem(row_num, col_num, QTableWidgetItem(str(data)))

        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        label_select = QLabel("กรุณาใส่ course_id ที่ต้องการเพิ่ม (คั่นด้วยเครื่องหมายจุลภาค)")
        self.entry_courses = QLineEdit()

        btn_submit = QPushButton("Submit")
        btn_submit.clicked.connect(self.submit_courses)

        if self.user_role == 'Admin':
            btn_back = QPushButton("ย้อนกลับ")
            btn_back.clicked.connect(self.show_all_enrollments)
        else:
            btn_back = QPushButton("ย้อนกลับ")
            btn_back.clicked.connect(self.show_enrollments)

        hbox_buttons = QHBoxLayout()
        hbox_buttons.addWidget(btn_submit)
        hbox_buttons.addWidget(btn_back)

        vbox_main = QVBoxLayout()
        vbox_main.addWidget(label)
        vbox_main.addWidget(table)
        vbox_main.addWidget(label_select)
        vbox_main.addWidget(self.entry_courses)
        vbox_main.addLayout(hbox_buttons)

        central_widget.setLayout(vbox_main)
        self.show()

    def submit_courses(self):
        courses_input = self.entry_courses.text()
        course_ids = courses_input.split(',')
        course_ids = [cid.strip() for cid in course_ids]

        if len(course_ids) > 3:
            QMessageBox.critical(self, "ข้อผิดพลาด", "คุณสามารถเพิ่มรายวิชาได้สูงสุด 3 วิชา")
            return

        # ตรวจสอบว่ารายวิชาที่ป้อนเข้ามาอยู่ในรายการที่สามารถเพิ่มได้หรือไม่
        query = '''
            SELECT c.course_id FROM Courses c
            WHERE c.course_id NOT IN (
                SELECT e.course_id FROM Enrollments e WHERE e.student_id = %s
            )
        '''
        self.db_manager.cursor.execute(query, (self.user_id,))
        available_courses = [str(row[0]) for row in self.db_manager.cursor.fetchall()]

        invalid_courses = [cid for cid in course_ids if cid not in available_courses]

        if invalid_courses:
            QMessageBox.critical(self, "ข้อผิดพลาด",
                                 "รายวิชาต่อไปนี้ไม่สามารถเพิ่มได้: {}".format(', '.join(invalid_courses)))
            return

        confirmation = QMessageBox.question(self, "ยืนยันการเพิ่มรายวิชา", "คุณแน่ใจหรือไม่ที่จะ Submit รายวิชานี้",
                                            QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            try:
                for course_id in course_ids:
                    # เพิ่มข้อมูลการลงทะเบียน
                    self.db_manager.cursor.execute('''
                        INSERT INTO Enrollments (student_id, course_id, semester, year, enrollment_date, grade)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    ''', (self.user_id, course_id, 1, date.today().year, date.today(), None))
                self.db_manager.conn.commit()

                QMessageBox.information(self, "สำเร็จ", "เพิ่มรายวิชาเรียบร้อยแล้ว")
                if self.user_role == 'Admin':
                    self.show_all_enrollments()
                else:
                    self.show_enrollments()
            except mysql.connector.Error as error:
                QMessageBox.critical(self, "ข้อผิดพลาด", f"เกิดข้อผิดพลาดในการเพิ่มรายวิชา: {error}")
        else:
            QMessageBox.information(self, "ยกเลิก", "การเพิ่มรายวิชาถูกยกเลิก")

    def manage_data(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        label = QLabel("Manage Data")
        label.setStyleSheet("font-size: 18px;")
        label.setAlignment(Qt.AlignCenter)

        btn_add = QPushButton("Add Data")
        btn_add.clicked.connect(self.add_data_screen)

        btn_update = QPushButton("Update Data")
        btn_update.clicked.connect(self.update_data_screen)

        btn_delete = QPushButton("Delete Data")
        btn_delete.clicked.connect(self.delete_data_screen)

        btn_back = QPushButton("ย้อนกลับ")
        btn_back.clicked.connect(self.show_all_enrollments)

        hbox_buttons = QHBoxLayout()
        hbox_buttons.addWidget(btn_add)
        hbox_buttons.addWidget(btn_update)
        hbox_buttons.addWidget(btn_delete)

        vbox_main = QVBoxLayout()
        vbox_main.addWidget(label)
        vbox_main.addLayout(hbox_buttons)
        vbox_main.addWidget(btn_back)

        central_widget.setLayout(vbox_main)
        self.show()

    def add_data_screen(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        label = QLabel("Add Data")
        label.setStyleSheet("font-size: 18px;")
        label.setAlignment(Qt.AlignCenter)

        label_table = QLabel("Table Name:")
        self.entry_table = QLineEdit()

        btn_load = QPushButton("Load Table")
        btn_load.clicked.connect(self.load_table_for_add)

        btn_back = QPushButton("ย้อนกลับ")
        btn_back.clicked.connect(self.manage_data)

        vbox_main = QVBoxLayout()
        vbox_main.addWidget(label)
        vbox_main.addWidget(label_table)
        vbox_main.addWidget(self.entry_table)
        vbox_main.addWidget(btn_load)
        vbox_main.addWidget(btn_back)

        central_widget.setLayout(vbox_main)
        self.show()

    def load_table_for_add(self):
        table_name = self.entry_table.text()
        columns = self.db_manager.show_table_columns(table_name)
        if not columns:
            return

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        label = QLabel(f"Add Data to {table_name}")
        label.setStyleSheet("font-size: 18px;")
        label.setAlignment(Qt.AlignCenter)

        table = QTableWidget()
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)

        query = f"SELECT * FROM {table_name}"
        self.db_manager.cursor.execute(query)
        results = self.db_manager.cursor.fetchall()

        table.setRowCount(len(results))
        for row_num, row_data in enumerate(results):
            for col_num, data in enumerate(row_data):
                table.setItem(row_num, col_num, QTableWidgetItem(str(data)))

        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # สร้างฟิลด์สำหรับป้อนข้อมูลใหม่
        self.add_entries = {}
        form_layout = QGridLayout()
        for idx, col in enumerate(columns):
            label_col = QLabel(col)
            entry = QLineEdit()
            form_layout.addWidget(label_col, 0, idx)
            form_layout.addWidget(entry, 1, idx)
            self.add_entries[col] = entry

        btn_submit = QPushButton("Add Data")
        btn_submit.clicked.connect(lambda: self.add_data(table_name, columns))

        btn_back = QPushButton("ย้อนกลับ")
        btn_back.clicked.connect(self.add_data_screen)

        hbox_buttons = QHBoxLayout()
        hbox_buttons.addWidget(btn_submit)
        hbox_buttons.addWidget(btn_back)

        vbox_main = QVBoxLayout()
        vbox_main.addWidget(label)
        vbox_main.addWidget(table)
        vbox_main.addLayout(form_layout)
        vbox_main.addLayout(hbox_buttons)

        central_widget.setLayout(vbox_main)
        self.show()

    def add_data(self, table_name, columns):
        values = []
        for col in columns:
            value = self.add_entries[col].text()
            values.append(value)
        try:
            self.db_manager.insert_data(table_name, columns, values)
            self.add_data_screen()  # กลับไปหน้าจอหลักของ Add Data
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def update_data_screen(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        label = QLabel("Update Data")
        label.setStyleSheet("font-size: 18px;")
        label.setAlignment(Qt.AlignCenter)

        label_table = QLabel("Table Name:")
        self.entry_table = QLineEdit()

        btn_load = QPushButton("Load Table")
        btn_load.clicked.connect(self.load_table_for_update)

        btn_back = QPushButton("ย้อนกลับ")
        btn_back.clicked.connect(self.manage_data)

        vbox_main = QVBoxLayout()
        vbox_main.addWidget(label)
        vbox_main.addWidget(label_table)
        vbox_main.addWidget(self.entry_table)
        vbox_main.addWidget(btn_load)
        vbox_main.addWidget(btn_back)

        central_widget.setLayout(vbox_main)
        self.show()

    def load_table_for_update(self):
        table_name = self.entry_table.text()
        columns = self.db_manager.show_table_columns(table_name)
        if not columns:
            return

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        label = QLabel(f"Update Data in {table_name}")
        label.setStyleSheet("font-size: 18px;")
        label.setAlignment(Qt.AlignCenter)

        table = QTableWidget()
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)

        query = f"SELECT * FROM {table_name}"
        self.db_manager.cursor.execute(query)
        results = self.db_manager.cursor.fetchall()

        table.setRowCount(len(results))
        for row_num, row_data in enumerate(results):
            for col_num, data in enumerate(row_data):
                table.setItem(row_num, col_num, QTableWidgetItem(str(data)))

        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # สร้างฟิลด์สำหรับป้อนข้อมูลที่จะอัปเดต
        self.update_entries = {}
        form_layout = QGridLayout()
        for idx, col in enumerate(columns):
            label_col = QLabel(col)
            entry = QLineEdit()
            form_layout.addWidget(label_col, 0, idx)
            form_layout.addWidget(entry, 1, idx)
            self.update_entries[col] = entry

        label_condition = QLabel("Conditions (เช่น column1=value1 AND column2=value2):")
        self.entry_condition = QLineEdit()

        btn_submit = QPushButton("Update Data")
        btn_submit.clicked.connect(lambda: self.update_data(table_name))

        btn_back = QPushButton("ย้อนกลับ")
        btn_back.clicked.connect(self.update_data_screen)

        hbox_buttons = QHBoxLayout()
        hbox_buttons.addWidget(btn_submit)
        hbox_buttons.addWidget(btn_back)

        vbox_main = QVBoxLayout()
        vbox_main.addWidget(label)
        vbox_main.addWidget(table)
        vbox_main.addLayout(form_layout)
        vbox_main.addWidget(label_condition)
        vbox_main.addWidget(self.entry_condition)
        vbox_main.addLayout(hbox_buttons)

        central_widget.setLayout(vbox_main)
        self.show()

    def update_data(self, table_name):
        updates = {}
        for col, entry in self.update_entries.items():
            value = entry.text()
            if value:
                updates[col] = value
        conditions_input = self.entry_condition.text()
        conditions = [cond.strip() for cond in conditions_input.split('AND')]
        try:
            self.db_manager.update_data(table_name, updates, conditions)
            self.update_data_screen()  # กลับไปหน้าจอหลักของ Update Data
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_data_screen(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        label = QLabel("Delete Data")
        label.setStyleSheet("font-size: 18px;")
        label.setAlignment(Qt.AlignCenter)

        label_table = QLabel("Table Name:")
        self.entry_table = QLineEdit()

        btn_load = QPushButton("Load Table")
        btn_load.clicked.connect(self.load_table_for_delete)

        btn_back = QPushButton("ย้อนกลับ")
        btn_back.clicked.connect(self.manage_data)

        vbox_main = QVBoxLayout()
        vbox_main.addWidget(label)
        vbox_main.addWidget(label_table)
        vbox_main.addWidget(self.entry_table)
        vbox_main.addWidget(btn_load)
        vbox_main.addWidget(btn_back)

        central_widget.setLayout(vbox_main)
        self.show()

    def load_table_for_delete(self):
        table_name = self.entry_table.text()
        columns = self.db_manager.show_table_columns(table_name)
        if not columns:
            return

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        label = QLabel(f"Delete Data from {table_name}")
        label.setStyleSheet("font-size: 18px;")
        label.setAlignment(Qt.AlignCenter)

        table = QTableWidget()
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)

        query = f"SELECT * FROM {table_name}"
        self.db_manager.cursor.execute(query)
        results = self.db_manager.cursor.fetchall()

        table.setRowCount(len(results))
        for row_num, row_data in enumerate(results):
            for col_num, data in enumerate(row_data):
                table.setItem(row_num, col_num, QTableWidgetItem(str(data)))

        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        label_condition = QLabel("Condition (เช่น column=value):")
        self.entry_condition = QLineEdit()

        btn_submit = QPushButton("Delete Data")
        btn_submit.clicked.connect(lambda: self.delete_data(table_name))

        btn_back = QPushButton("ย้อนกลับ")
        btn_back.clicked.connect(self.delete_data_screen)

        hbox_buttons = QHBoxLayout()
        hbox_buttons.addWidget(btn_submit)
        hbox_buttons.addWidget(btn_back)

        vbox_main = QVBoxLayout()
        vbox_main.addWidget(label)
        vbox_main.addWidget(table)
        vbox_main.addWidget(label_condition)
        vbox_main.addWidget(self.entry_condition)
        vbox_main.addLayout(hbox_buttons)

        central_widget.setLayout(vbox_main)
        self.show()

    def delete_data(self, table_name):
        condition = self.entry_condition.text()
        try:
            self.db_manager.delete_data(table_name, condition)
            self.delete_data_screen()  # กลับไปหน้าจอหลักของ Delete Data
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def closeEvent(self, event):
        if self.db_manager:
            self.db_manager.close_connection()
        event.accept()


# สร้างและรันแอปพลิเคชัน
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Application()
    sys.exit(app.exec_())
