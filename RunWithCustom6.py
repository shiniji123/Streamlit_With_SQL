import customtkinter as tk
from tkinter import messagebox
from tkinter import ttk
import mysql.connector
from datetime import date


# ---------------------- Database Management ---------------------- #

class DatabaseManager:
    def __init__(self, role):
        self.conn = None
        self.cursor = None
        self.role = role
        self.connect_to_db()

    def connect_to_db(self):
        try:
            if self.role == 'Admin':
                self.conn = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="sesar123",
                    database="education_sector"
                )
            else:
                self.conn = mysql.connector.connect(
                    host="localhost",
                    user="student",
                    password="1234",
                    database="education_sector"
                )
            self.cursor = self.conn.cursor()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            messagebox.showerror("Database Error", f"Cannot connect to database: {err}")

    def close_connection(self):
        if self.conn and self.conn.is_connected():
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
            messagebox.showerror("Database Error", f"Error fetching columns: {err}")
            return []

    def insert_data(self, table_name, columns, values):
        try:
            columns_str = ','.join(columns)
            placeholders = ','.join(['%s'] * len(values))
            query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
            self.cursor.execute(query, values)
            self.conn.commit()
            print(f"1 record inserted successfully into {table_name}")
            messagebox.showinfo("Success", f"Data inserted into {table_name} successfully.")
        except mysql.connector.Error as error:
            print(f"Failed to insert data into MySQL table {table_name}: {error}")
            messagebox.showerror("Database Error", f"Failed to insert data: {error}")

    def delete_data(self, table_name, condition):
        try:
            query = f"DELETE FROM {table_name} WHERE {condition}"
            self.cursor.execute(query)
            self.conn.commit()
            print(f"Record(s) deleted successfully from {table_name} where {condition}")
            messagebox.showinfo("Success", f"Data deleted from {table_name} successfully.")
        except mysql.connector.Error as error:
            print(f"Failed to delete data from MySQL table {table_name}: {error}")
            messagebox.showerror("Database Error", f"Failed to delete data: {error}")

    def update_data(self, table_name, updates, conditions):
        try:
            set_clause = ', '.join([f"{column} = %s" for column in updates.keys()])
            condition_clause = ' AND '.join(conditions)
            query = f"UPDATE {table_name} SET {set_clause} WHERE {condition_clause}"
            self.cursor.execute(query, list(updates.values()))
            self.conn.commit()
            print(f"Record(s) updated successfully in {table_name} where {condition_clause}")
            messagebox.showinfo("Success", f"Data updated in {table_name} successfully.")
        except mysql.connector.Error as error:
            print(f"Failed to update data in MySQL table {table_name}: {error}")
            messagebox.showerror("Database Error", f"Failed to update data: {error}")

    def fetch_all_enrollments(self):
        try:
            query = '''
                SELECT s.student_id, s.first_name, s.last_name, c.course_id, c.course_name, c.credits, e.semester, e.year, e.grade
                FROM Students s
                JOIN Enrollments e ON s.student_id = e.student_id
                JOIN Courses c ON e.course_id = c.course_id
            '''
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except mysql.connector.Error as error:
            print(f"Error fetching enrollments: {error}")
            messagebox.showerror("Database Error", f"Error fetching enrollments: {error}")
            return []

    def fetch_student_enrollments(self, student_id):
        try:
            query = '''
                SELECT s.student_id, s.first_name, s.last_name, c.course_id, c.course_name, c.credits, e.semester, e.year, e.grade
                FROM Students s
                JOIN Enrollments e ON s.student_id = e.student_id
                JOIN Courses c ON e.course_id = c.course_id
                WHERE s.student_id = %s
            '''
            self.cursor.execute(query, (student_id,))
            return self.cursor.fetchall()
        except mysql.connector.Error as error:
            print(f"Error fetching student enrollments: {error}")
            messagebox.showerror("Database Error", f"Error fetching enrollments: {error}")
            return []

    def fetch_available_courses(self, student_id):
        try:
            query = '''
                SELECT * FROM Courses c
                WHERE c.course_id NOT IN (
                    SELECT e.course_id FROM Enrollments e WHERE e.student_id = %s
                )
            '''
            self.cursor.execute(query, (student_id,))
            return self.cursor.fetchall()
        except mysql.connector.Error as error:
            print(f"Error fetching available courses: {error}")
            messagebox.showerror("Database Error", f"Error fetching available courses: {error}")
            return []

    def authenticate_user(self, table, user_id, password):
        try:
            query = f"SELECT * FROM {table} WHERE {table[:-1].lower()}_id=%s AND {table[:-1].lower()}_password=%s"
            self.cursor.execute(query, (user_id, password))
            return self.cursor.fetchone()
        except mysql.connector.Error as error:
            print(f"Authentication error: {error}")
            messagebox.showerror("Database Error", f"Authentication error: {error}")
            return None


# ---------------------- GUI Frames ---------------------- #

class LoginFrame(tk.CTkFrame):
    def __init__(self, master, switch_frame_callback):
        super().__init__(master)
        self.master = master
        self.switch_frame_callback = switch_frame_callback
        self.create_widgets()

    def create_widgets(self):
        label_title = tk.CTkLabel(self, text="ระบบลงทะเบียนนักศึกษา", font=("Arial", 24))
        label_title.pack(pady=20)

        frame = tk.CTkFrame(self)
        frame.pack(pady=10)

        label_role = tk.CTkLabel(frame, text="เข้าสู่ระบบในฐานะ", font=("Arial", 18))
        label_role.grid(row=0, column=0, padx=5, pady=5)

        self.role_var = tk.StringVar(value="Student")
        radio_student = tk.CTkRadioButton(frame, text="Student", variable=self.role_var, value="Student",
                                          font=("Arial", 16))
        radio_student.grid(row=0, column=1, padx=5, pady=5)
        radio_admin = tk.CTkRadioButton(frame, text="Admin", variable=self.role_var, value="Admin", font=("Arial", 16))
        radio_admin.grid(row=0, column=2, padx=5, pady=5)

        label_id = tk.CTkLabel(frame, text="User ID", font=("Arial", 18))
        label_id.grid(row=1, column=0, padx=5, pady=5)

        self.entry_id = tk.CTkEntry(frame, font=("Arial", 16))
        self.entry_id.grid(row=1, column=1, padx=5, pady=5)

        label_password = tk.CTkLabel(frame, text="Password", font=("Arial", 18))
        label_password.grid(row=2, column=0, padx=5, pady=5)

        self.entry_password = tk.CTkEntry(frame, show='*', font=("Arial", 16))
        self.entry_password.grid(row=2, column=1, padx=5, pady=5)

        btn_login = tk.CTkButton(self, text="เข้าสู่ระบบ", command=self.login, font=("Arial", 16))
        btn_login.pack(pady=10)

        btn_fullscreen = tk.CTkButton(self, text="Full Screen", command=self.master.toggle_fullscreen,
                                      font=("Arial", 16))
        btn_fullscreen.pack(pady=5)

    def login(self):
        user_id = self.entry_id.get()
        password = self.entry_password.get()
        user_role = self.role_var.get()

        table = 'Admins' if user_role == 'Admin' else 'Students'
        db_manager = DatabaseManager(user_role)

        result = db_manager.authenticate_user(table, user_id, password)

        if result:
            messagebox.showinfo("เข้าสู่ระบบสำเร็จ", f"ยินดีต้อนรับคุณ {result[1]} {result[2]}")
            self.master.user_role = user_role
            self.master.user_id = user_id
            self.master.db_manager = db_manager
            if user_role == 'Admin':
                self.switch_frame_callback("AdminEnrollment")
            else:
                self.switch_frame_callback("StudentEnrollment")
        else:
            messagebox.showerror("ข้อผิดพลาด", "รหัสผู้ใช้หรือรหัสผ่านของคุณไม่ถูกต้อง")
            db_manager.close_connection()


# ---------------------- Student Enrollment Frame ---------------------- #

class StudentEnrollmentFrame(tk.CTkFrame):
    def __init__(self, master, switch_frame_callback):
        super().__init__(master)
        self.master = master
        self.switch_frame_callback = switch_frame_callback
        self.create_widgets()

    def create_widgets(self):
        label = tk.CTkLabel(self, text="ข้อมูลการลงทะเบียนของคุณ", font=("Arial", 20))
        label.pack(pady=10)

        columns = (
            'student_id', 'first_name', 'last_name', 'course_id', 'course_name', 'credits', 'semester', 'year', 'grade')

        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 14))
        style.configure("Treeview", font=("Arial", 12), rowheight=30)
        self.tree = ttk.Treeview(self, columns=columns, show='headings', style="Treeview")

        # Define column properties
        tree_columns = {
            'student_id': 100, 'first_name': 120, 'last_name': 120,
            'course_id': 100, 'course_name': 200, 'credits': 80,
            'semester': 100, 'year': 80, 'grade': 80
        }
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=tree_columns[col], anchor='center' if col != 'course_name' else 'w')

        self.tree.pack(fill=tk.BOTH, expand=True)

        self.populate_enrollments()

        btn_frame = tk.CTkFrame(self)
        btn_frame.pack(pady=10)

        btn_add_course = tk.CTkButton(btn_frame, text="Add รายวิชา",
                                      command=self.switch_frame_callback.bind(self, "AddCourses"), font=("Arial", 16))
        btn_add_course.grid(row=0, column=0, padx=5)

        btn_logout = tk.CTkButton(btn_frame, text="Logout", command=self.master.logout, font=("Arial", 16))
        btn_logout.grid(row=0, column=1, padx=5)

    def populate_enrollments(self):
        for row in self.master.db_manager.fetch_student_enrollments(self.master.user_id):
            self.tree.insert('', tk.END, values=row)


# ---------------------- Admin Enrollment Frame ---------------------- #

class AdminEnrollmentFrame(tk.CTkFrame):
    def __init__(self, master, switch_frame_callback):
        super().__init__(master)
        self.master = master
        self.switch_frame_callback = switch_frame_callback
        self.create_widgets()

    def create_widgets(self):
        label = tk.CTkLabel(self, text="ข้อมูลการลงทะเบียนของนักศึกษาทุกคน", font=("Arial", 20))
        label.pack(pady=10)

        columns = (
            'student_id', 'first_name', 'last_name', 'course_id', 'course_name', 'credits', 'semester', 'year', 'grade')

        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 14))
        style.configure("Treeview", font=("Arial", 12), rowheight=30)
        self.tree = ttk.Treeview(self, columns=columns, show='headings', style="Treeview")

        # Define column properties
        tree_columns = {
            'student_id': 100, 'first_name': 120, 'last_name': 120,
            'course_id': 100, 'course_name': 200, 'credits': 80,
            'semester': 100, 'year': 80, 'grade': 80
        }
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=tree_columns[col], anchor='center' if col != 'course_name' else 'w')

        self.tree.pack(fill=tk.BOTH, expand=True)

        self.populate_enrollments()

        btn_frame = tk.CTkFrame(self)
        btn_frame.pack(pady=10)

        btn_manage_data = tk.CTkButton(btn_frame, text="Manage Data",
                                       command=self.switch_frame_callback.bind(self, "ManageData"), font=("Arial", 16))
        btn_manage_data.grid(row=0, column=0, padx=5)

        btn_logout = tk.CTkButton(btn_frame, text="Logout", command=self.master.logout, font=("Arial", 16))
        btn_logout.grid(row=0, column=1, padx=5)

    def populate_enrollments(self):
        for row in self.master.db_manager.fetch_all_enrollments():
            self.tree.insert('', tk.END, values=row)


# ---------------------- Add Courses Frame ---------------------- #

class AddCoursesFrame(tk.CTkFrame):
    def __init__(self, master, switch_frame_callback):
        super().__init__(master)
        self.master = master
        self.switch_frame_callback = switch_frame_callback
        self.create_widgets()

    def create_widgets(self):
        label = tk.CTkLabel(self, text="เลือกวิชาที่ต้องการเพิ่ม (สูงสุด 3 วิชา)", font=("Arial", 20))
        label.pack(pady=10)

        columns = ('course_id', 'course_name', 'credits', 'department_id', 'instructor_id')

        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 14))
        style.configure("Treeview", font=("Arial", 12), rowheight=30)
        self.tree = ttk.Treeview(self, columns=columns, show='headings', style="Treeview")

        # Define column properties
        tree_columns = {
            'course_id': 100, 'course_name': 250, 'credits': 80,
            'department_id': 120, 'instructor_id': 120
        }
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=tree_columns[col], anchor='center' if col != 'course_name' else 'w')

        self.tree.pack(fill=tk.BOTH, expand=True)

        self.populate_available_courses()

        label_select = tk.CTkLabel(self, text="กรุณาใส่ course_id ที่ต้องการเพิ่ม (คั่นด้วยเครื่องหมายจุลภาค)",
                                   font=("Arial", 16))
        label_select.pack(pady=5)

        self.entry_courses = tk.CTkEntry(self, font=("Arial", 16))
        self.entry_courses.pack()

        btn_frame = tk.CTkFrame(self)
        btn_frame.pack(pady=10)

        btn_submit = tk.CTkButton(btn_frame, text="Submit", command=self.submit_courses, font=("Arial", 16))
        btn_submit.grid(row=0, column=0, padx=5)

        btn_back = tk.CTkButton(btn_frame, text="ย้อนกลับ", command=lambda: self.switch_frame_callback(
            "StudentEnrollment" if self.master.user_role == 'Student' else "AdminEnrollment"), font=("Arial", 16))
        btn_back.grid(row=0, column=1, padx=5)

    def populate_available_courses(self):
        for row in self.master.db_manager.fetch_available_courses(self.master.user_id):
            self.tree.insert('', tk.END, values=row)

    def submit_courses(self):
        courses_input = self.entry_courses.get()
        course_ids = courses_input.split(',')
        course_ids = [cid.strip() for cid in course_ids]

        if len(course_ids) > 3:
            messagebox.showerror("ข้อผิดพลาด", "คุณสามารถเพิ่มรายวิชาได้สูงสุด 3 วิชา")
            return

        available_courses = [str(row[0]) for row in self.master.db_manager.fetch_available_courses(self.master.user_id)]

        invalid_courses = [cid for cid in course_ids if cid not in available_courses]

        if invalid_courses:
            messagebox.showerror("ข้อผิดพลาด",
                                 "รายวิชาต่อไปนี้ไม่สามารถเพิ่มได้: {}".format(', '.join(invalid_courses)))
            return

        confirmation = messagebox.askokcancel("ยืนยันการเพิ่มรายวิชา", "คุณแน่ใจหรือไม่ที่จะ Submit รายวิชานี้")

        if confirmation:
            try:
                for course_id in course_ids:
                    self.master.db_manager.cursor.execute('''
                        INSERT INTO Enrollments (student_id, course_id, semester, year, enrollment_date, grade)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    ''', (self.master.user_id, course_id, 1, date.today().year, date.today(), None))
                self.master.db_manager.conn.commit()

                messagebox.showinfo("สำเร็จ", "เพิ่มรายวิชาเรียบร้อยแล้ว")
                self.switch_frame_callback(
                    "StudentEnrollment" if self.master.user_role == 'Student' else "AdminEnrollment")
            except mysql.connector.Error as error:
                messagebox.showerror("Database Error", f"Failed to add courses: {error}")
        else:
            messagebox.showinfo("ยกเลิก", "การเพิ่มรายวิชาถูกยกเลิก")


# ---------------------- Manage Data Frame ---------------------- #

class ManageDataFrame(tk.CTkFrame):
    def __init__(self, master, switch_frame_callback):
        super().__init__(master)
        self.master = master
        self.switch_frame_callback = switch_frame_callback
        self.create_widgets()

    def create_widgets(self):
        label = tk.CTkLabel(self, text="Manage Data", font=("Arial", 20))
        label.pack(pady=10)

        btn_frame = tk.CTkFrame(self)
        btn_frame.pack(pady=10)

        btn_add = tk.CTkButton(btn_frame, text="Add Data", command=lambda: self.switch_frame_callback("AddData"),
                               font=("Arial", 16))
        btn_add.grid(row=0, column=0, padx=5)

        btn_update = tk.CTkButton(btn_frame, text="Update Data",
                                  command=lambda: self.switch_frame_callback("UpdateData"), font=("Arial", 16))
        btn_update.grid(row=0, column=1, padx=5)

        btn_delete = tk.CTkButton(btn_frame, text="Delete Data",
                                  command=lambda: self.switch_frame_callback("DeleteData"), font=("Arial", 16))
        btn_delete.grid(row=0, column=2, padx=5)

        btn_back = tk.CTkButton(self, text="ย้อนกลับ", command=lambda: self.switch_frame_callback("AdminEnrollment"),
                                font=("Arial", 16))
        btn_back.pack(pady=10)


# ---------------------- Add Data Frame ---------------------- #

class AddDataFrame(tk.CTkFrame):
    def __init__(self, master, switch_frame_callback):
        super().__init__(master)
        self.master = master
        self.switch_frame_callback = switch_frame_callback
        self.add_entries = {}
        self.table_name = None
        self.columns = []
        self.create_widgets_initial()

    def create_widgets_initial(self):
        for widget in self.winfo_children():
            widget.destroy()

        label = tk.CTkLabel(self, text="Add Data", font=("Arial", 20))
        label.pack(pady=10)

        label_table = tk.CTkLabel(self, text="Table Name:", font=("Arial", 16))
        label_table.pack()

        self.entry_table = tk.CTkEntry(self, font=("Arial", 16))
        self.entry_table.pack()

        btn_load = tk.CTkButton(self, text="Load Table", command=self.load_table_for_add, font=("Arial", 16))
        btn_load.pack(pady=5)

        btn_back = tk.CTkButton(self, text="ย้อนกลับ", command=lambda: self.switch_frame_callback("ManageData"),
                                font=("Arial", 16))
        btn_back.pack(pady=5)

    def load_table_for_add(self):
        self.table_name = self.entry_table.get()
        self.columns = self.master.db_manager.show_table_columns(self.table_name)
        if not self.columns:
            return

        # Clear existing widgets
        for widget in self.winfo_children():
            widget.destroy()

        label = tk.CTkLabel(self, text=f"Add Data to {self.table_name}", font=("Arial", 20))
        label.pack(pady=10)

        # Display existing data
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 14))
        style.configure("Treeview", font=("Arial", 12), rowheight=30)
        self.tree = ttk.Treeview(self, columns=self.columns, show='headings', style="Treeview")
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor='center', width=100)

        try:
            query = f"SELECT * FROM {self.table_name}"
            self.master.db_manager.cursor.execute(query)
            results = self.master.db_manager.cursor.fetchall()

            for row in results:
                self.tree.insert('', tk.END, values=row)
        except mysql.connector.Error as error:
            messagebox.showerror("Database Error", f"Failed to fetch data: {error}")

        self.tree.pack(fill=tk.BOTH, expand=True)

        # Entry fields for new data
        self.add_entries = {}
        frame_entries = tk.CTkFrame(self)
        frame_entries.pack(pady=10)
        for idx, col in enumerate(self.columns):
            label_col = tk.CTkLabel(frame_entries, text=col, font=("Arial", 14))
            label_col.grid(row=0, column=idx, padx=5, pady=5)
            entry = tk.CTkEntry(frame_entries, font=("Arial", 14))
            entry.grid(row=1, column=idx, padx=5, pady=5)
            self.add_entries[col] = entry

        btn_frame = tk.CTkFrame(self)
        btn_frame.pack(pady=10)

        btn_submit = tk.CTkButton(btn_frame, text="Add Data", command=self.add_data, font=("Arial", 16))
        btn_submit.grid(row=0, column=0, padx=5)

        btn_back = tk.CTkButton(btn_frame, text="ย้อนกลับ", command=self.create_widgets_initial, font=("Arial", 16))
        btn_back.grid(row=0, column=1, padx=5)

    def add_data(self):
        values = []
        for col in self.columns:
            value = self.add_entries[col].get()
            values.append(value)
        try:
            self.master.db_manager.insert_data(self.table_name, self.columns, values)
            self.load_table_for_add()  # Refresh the table view
        except Exception as e:
            messagebox.showerror("Error", str(e))


# ---------------------- Update Data Frame ---------------------- #

class UpdateDataFrame(tk.CTkFrame):
    def __init__(self, master, switch_frame_callback):
        super().__init__(master)
        self.master = master
        self.switch_frame_callback = switch_frame_callback
        self.update_entries = {}
        self.table_name = None
        self.columns = []
        self.create_widgets_initial()

    def create_widgets_initial(self):
        for widget in self.winfo_children():
            widget.destroy()

        label = tk.CTkLabel(self, text="Update Data", font=("Arial", 20))
        label.pack(pady=10)

        label_table = tk.CTkLabel(self, text="Table Name:", font=("Arial", 16))
        label_table.pack()

        self.entry_table = tk.CTkEntry(self, font=("Arial", 16))
        self.entry_table.pack()

        btn_load = tk.CTkButton(self, text="Load Table", command=self.load_table_for_update, font=("Arial", 16))
        btn_load.pack(pady=5)

        btn_back = tk.CTkButton(self, text="ย้อนกลับ", command=lambda: self.switch_frame_callback("ManageData"),
                                font=("Arial", 16))
        btn_back.pack(pady=5)

    def load_table_for_update(self):
        self.table_name = self.entry_table.get()
        self.columns = self.master.db_manager.show_table_columns(self.table_name)
        if not self.columns:
            return

        # Clear existing widgets
        for widget in self.winfo_children():
            widget.destroy()

        label = tk.CTkLabel(self, text=f"Update Data in {self.table_name}", font=("Arial", 20))
        label.pack(pady=10)

        # Display existing data
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 14))
        style.configure("Treeview", font=("Arial", 12), rowheight=30)
        self.tree = ttk.Treeview(self, columns=self.columns, show='headings', style="Treeview")
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor='center', width=100)

        try:
            query = f"SELECT * FROM {self.table_name}"
            self.master.db_manager.cursor.execute(query)
            results = self.master.db_manager.cursor.fetchall()

            for row in results:
                self.tree.insert('', tk.END, values=row)
        except mysql.connector.Error as error:
            messagebox.showerror("Database Error", f"Failed to fetch data: {error}")

        self.tree.pack(fill=tk.BOTH, expand=True)

        # Entry fields for updates
        self.update_entries = {}
        frame_entries = tk.CTkFrame(self)
        frame_entries.pack(pady=10)
        for idx, col in enumerate(self.columns):
            label_col = tk.CTkLabel(frame_entries, text=col, font=("Arial", 14))
            label_col.grid(row=0, column=idx, padx=5, pady=5)
            entry = tk.CTkEntry(frame_entries, font=("Arial", 14))
            entry.grid(row=1, column=idx, padx=5, pady=5)
            self.update_entries[col] = entry

        label_condition = tk.CTkLabel(self, text="กรุณาระบุเงื่อนไข (เช่น student_id=6705177 AND course_id=10122):",
                                      font=("Arial", 16))
        label_condition.pack(pady=5)

        self.entry_condition = tk.CTkEntry(self, font=("Arial", 16))
        self.entry_condition.pack()

        btn_frame = tk.CTkFrame(self)
        btn_frame.pack(pady=10)

        btn_submit = tk.CTkButton(btn_frame, text="Update Data", command=self.update_data, font=("Arial", 16))
        btn_submit.grid(row=0, column=0, padx=5)

        btn_back = tk.CTkButton(btn_frame, text="ย้อนกลับ", command=self.create_widgets_initial, font=("Arial", 16))
        btn_back.grid(row=0, column=1, padx=5)

    def update_data(self):
        updates = {}
        for col, entry in self.update_entries.items():
            value = entry.get()
            if value:
                updates[col] = value
        conditions_input = self.entry_condition.get()
        if not conditions_input:
            messagebox.showerror("Error", "กรุณาระบุเงื่อนไขในการอัปเดตข้อมูล")
            return
        conditions = [cond.strip() for cond in conditions_input.split('AND')]
        try:
            self.master.db_manager.update_data(self.table_name, updates, conditions)
            self.load_table_for_update()  # Refresh the table view
        except Exception as e:
            messagebox.showerror("Error", str(e))


# ---------------------- Delete Data Frame ---------------------- #

class DeleteDataFrame(tk.CTkFrame):
    def __init__(self, master, switch_frame_callback):
        super().__init__(master)
        self.master = master
        self.switch_frame_callback = switch_frame_callback
        self.table_name = None
        self.columns = []
        self.create_widgets_initial()

    def create_widgets_initial(self):
        for widget in self.winfo_children():
            widget.destroy()

        label = tk.CTkLabel(self, text="Delete Data", font=("Arial", 20))
        label.pack(pady=10)

        label_table = tk.CTkLabel(self, text="Table Name:", font=("Arial", 16))
        label_table.pack()

        self.entry_table = tk.CTkEntry(self, font=("Arial", 16))
        self.entry_table.pack()

        btn_load = tk.CTkButton(self, text="Load Table", command=self.load_table_for_delete, font=("Arial", 16))
        btn_load.pack(pady=5)

        btn_back = tk.CTkButton(self, text="ย้อนกลับ", command=lambda: self.switch_frame_callback("ManageData"),
                                font=("Arial", 16))
        btn_back.pack(pady=5)

    def load_table_for_delete(self):
        self.table_name = self.entry_table.get()
        self.columns = self.master.db_manager.show_table_columns(self.table_name)
        if not self.columns:
            return

        # Clear existing widgets
        for widget in self.winfo_children():
            widget.destroy()

        label = tk.CTkLabel(self, text=f"Delete Data from {self.table_name}", font=("Arial", 20))
        label.pack(pady=10)

        # Display existing data
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 14))
        style.configure("Treeview", font=("Arial", 12), rowheight=30)
        self.tree = ttk.Treeview(self, columns=self.columns, show='headings', style="Treeview")
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor='center', width=100)

        try:
            query = f"SELECT * FROM {self.table_name}"
            self.master.db_manager.cursor.execute(query)
            results = self.master.db_manager.cursor.fetchall()

            for row in results:
                self.tree.insert('', tk.END, values=row)
        except mysql.connector.Error as error:
            messagebox.showerror("Database Error", f"Failed to fetch data: {error}")

        self.tree.pack(fill=tk.BOTH, expand=True)

        label_condition = tk.CTkLabel(self, text="Condition (เช่น column=value):", font=("Arial", 16))
        label_condition.pack(pady=5)

        self.entry_condition = tk.CTkEntry(self, font=("Arial", 16))
        self.entry_condition.pack()

        btn_frame = tk.CTkFrame(self)
        btn_frame.pack(pady=10)

        btn_submit = tk.CTkButton(btn_frame, text="Delete Data", command=self.delete_data, font=("Arial", 16))
        btn_submit.grid(row=0, column=0, padx=5)

        btn_back = tk.CTkButton(btn_frame, text="ย้อนกลับ", command=self.create_widgets_initial, font=("Arial", 16))
        btn_back.grid(row=0, column=1, padx=5)

    def delete_data(self):
        condition = self.entry_condition.get()
        if not condition:
            messagebox.showerror("Error", "กรุณาระบุเงื่อนไขในการลบข้อมูล")
            return
        try:
            self.master.db_manager.delete_data(self.table_name, condition)
            self.load_table_for_delete()  # Refresh the table view
        except Exception as e:
            messagebox.showerror("Error", str(e))


# ---------------------- Main Application ---------------------- #

class Application(tk.CTk):
    def __init__(self):
        super().__init__()
        tk.set_appearance_mode("light")  # เปลี่ยนโหมดสีตามต้องการ
        tk.set_default_color_theme("blue")
        self.title("Student Enrollment System")
        self.geometry("1000x700")
        self.center_window(1000, 700)
        self.db_manager = None
        self.user_role = None  # 'Admin' or 'Student'
        self.user_id = None  # 'admin_id' or 'student_id'
        self.is_fullscreen = False  # สำหรับตรวจสอบสถานะ Full Screen

        self.frames = {}
        self.create_frames()
        self.show_frame("Login")

    def center_window(self, width, height):
        # ฟังก์ชันสำหรับจัดตำแหน่งหน้าต่างให้อยู่ตรงกลางหน้าจอ
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_cordinate = int((screen_width / 2) - (width / 2))
        y_cordinate = int((screen_height / 2) - (height / 2))
        self.geometry(f"{width}x{height}+{x_cordinate}+{y_cordinate}")

    def create_frames(self):
        for F in (LoginFrame, StudentEnrollmentFrame, AdminEnrollmentFrame, AddCoursesFrame,
                  ManageDataFrame, AddDataFrame, UpdateDataFrame, DeleteDataFrame):
            frame_name = F.__name__.replace("Frame", "")
            frame = F(self, self.switch_frame)
            self.frames[frame_name] = frame
            frame.place(relwidth=1, relheight=1)

    def show_frame(self, frame_name):
        frame = self.frames.get(frame_name)
        if frame:
            frame.tkraise()
            if frame_name in ["StudentEnrollment", "AdminEnrollment"]:
                self.refresh_treeview(frame)
        else:
            print(f"Frame '{frame_name}' does not exist.")

    def switch_frame(self, frame_name):
        self.show_frame(frame_name)

    def refresh_treeview(self, frame):
        if isinstance(frame, StudentEnrollmentFrame):
            for item in frame.tree.get_children():
                frame.tree.delete(item)
            for row in self.db_manager.fetch_student_enrollments(self.user_id):
                frame.tree.insert('', tk.END, values=row)
        elif isinstance(frame, AdminEnrollmentFrame):
            for item in frame.tree.get_children():
                frame.tree.delete(item)
            for row in self.db_manager.fetch_all_enrollments():
                frame.tree.insert('', tk.END, values=row)

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        self.attributes("-fullscreen", self.is_fullscreen)
        if not self.is_fullscreen:
            self.center_window(1000, 700)

    def logout(self):
        if self.db_manager:
            self.db_manager.close_connection()
        self.user_id = None
        self.user_role = None
        self.db_manager = None
        self.show_frame("Login")

    def on_closing(self):
        if self.db_manager:
            self.db_manager.close_connection()
        self.destroy()


# ---------------------- Run Application ---------------------- #

if __name__ == "__main__":
    app = Application()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
