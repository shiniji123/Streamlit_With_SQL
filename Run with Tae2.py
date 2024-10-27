import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
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
            messagebox.showerror("Database Error", f"Cannot connect to database: {err}")

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


# คลาสสำหรับส่วนติดต่อผู้ใช้
class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Student Enrollment System")
        self.geometry("800x500")
        self.db_manager = None
        self.user_role = None  # 'Admin' or 'Student'
        self.user_id = None  # 'admin_id' or 'student_id'
        self.create_widgets()

    def create_widgets(self):
        self.login_screen()

    def login_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

        label_title = tk.Label(self, text="ระบบลงทะเบียนนักศึกษา", font=("Arial", 20))
        label_title.pack(pady=20)

        frame = tk.Frame(self)
        frame.pack(pady=10)

        label_role = tk.Label(frame, text="เข้าสู่ระบบในฐานะ")
        label_role.grid(row=0, column=0, padx=5, pady=5)

        self.role_var = tk.StringVar(value="Student")
        radio_student = tk.Radiobutton(frame, text="Student", variable=self.role_var, value="Student")
        radio_student.grid(row=0, column=1, padx=5, pady=5)
        radio_admin = tk.Radiobutton(frame, text="Admin", variable=self.role_var, value="Admin")
        radio_admin.grid(row=0, column=2, padx=5, pady=5)

        label_id = tk.Label(frame, text="User ID")
        label_id.grid(row=1, column=0, padx=5, pady=5)

        self.entry_id = tk.Entry(frame)
        self.entry_id.grid(row=1, column=1, padx=5, pady=5)

        label_password = tk.Label(frame, text="Password")
        label_password.grid(row=2, column=0, padx=5, pady=5)

        self.entry_password = tk.Entry(frame, show='*')
        self.entry_password.grid(row=2, column=1, padx=5, pady=5)

        btn_login = tk.Button(self, text="เข้าสู่ระบบ", command=self.login)
        btn_login.pack(pady=10)

    def login(self):
        user_id = self.entry_id.get()
        password = self.entry_password.get()
        self.user_role = self.role_var.get()

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
            messagebox.showinfo("เข้าสู่ระบบสำเร็จ", f"ยินดีต้อนรับคุณ {result[1]} {result[2]}")
            self.user_id = user_id
            if self.user_role == 'Admin':
                self.show_all_enrollments()
            else:
                self.show_enrollments()
        else:
            messagebox.showerror("ข้อผิดพลาด", "รหัสผู้ใช้หรือรหัสผ่านของคุณไม่ถูกต้อง")
            self.db_manager.close_connection()
            self.db_manager = None

    def show_enrollments(self):
        for widget in self.winfo_children():
            widget.destroy()

        label = tk.Label(self, text="ข้อมูลการลงทะเบียนของคุณ", font=("Arial", 16))
        label.pack(pady=10)

        columns = (
        'student_id', 'first_name', 'last_name', 'course_id', 'course_name', 'credits', 'semester', 'year', 'grade')
        tree = ttk.Treeview(self, columns=columns, show='headings')

        # กำหนดความกว้างของคอลัมน์ให้เหมาะสม
        tree.column('student_id', width=80, anchor='center')
        tree.column('first_name', width=100, anchor='center')
        tree.column('last_name', width=100, anchor='center')
        tree.column('course_id', width=80, anchor='center')
        tree.column('course_name', width=150, anchor='w')
        tree.column('credits', width=60, anchor='center')
        tree.column('semester', width=80, anchor='center')
        tree.column('year', width=60, anchor='center')
        tree.column('grade', width=60, anchor='center')

        for col in columns:
            tree.heading(col, text=col)

        query = '''
            SELECT s.student_id, s.first_name, s.last_name, c.course_id, c.course_name, c.credits, e.semester, e.year, e.grade
            FROM Students s
            JOIN Enrollments e ON s.student_id = e.student_id
            JOIN Courses c ON e.course_id = c.course_id
            WHERE s.student_id = %s
        '''
        self.db_manager.cursor.execute(query, (self.user_id,))
        results = self.db_manager.cursor.fetchall()

        for row in results:
            tree.insert('', tk.END, values=row)

        tree.pack(fill=tk.BOTH, expand=True)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        btn_add_course = tk.Button(btn_frame, text="Add รายวิชา", command=self.add_courses)
        btn_add_course.grid(row=0, column=0, padx=5)

        btn_logout = tk.Button(btn_frame, text="Logout", command=self.logout)
        btn_logout.grid(row=0, column=1, padx=5)

    def show_all_enrollments(self):
        for widget in self.winfo_children():
            widget.destroy()

        label = tk.Label(self, text="ข้อมูลการลงทะเบียนของนักศึกษาทุกคน", font=("Arial", 16))
        label.pack(pady=10)

        columns = (
        'student_id', 'first_name', 'last_name', 'course_id', 'course_name', 'credits', 'semester', 'year', 'grade')
        tree = ttk.Treeview(self, columns=columns, show='headings')

        # กำหนดความกว้างของคอลัมน์ให้เหมาะสม
        tree.column('student_id', width=80, anchor='center')
        tree.column('first_name', width=100, anchor='center')
        tree.column('last_name', width=100, anchor='center')
        tree.column('course_id', width=80, anchor='center')
        tree.column('course_name', width=150, anchor='w')
        tree.column('credits', width=60, anchor='center')
        tree.column('semester', width=80, anchor='center')
        tree.column('year', width=60, anchor='center')
        tree.column('grade', width=60, anchor='center')

        for col in columns:
            tree.heading(col, text=col)

        query = '''
            SELECT s.student_id, s.first_name, s.last_name, c.course_id, c.course_name, c.credits, e.semester, e.year, e.grade
            FROM Students s
            JOIN Enrollments e ON s.student_id = e.student_id
            JOIN Courses c ON e.course_id = c.course_id
        '''
        self.db_manager.cursor.execute(query)
        results = self.db_manager.cursor.fetchall()

        for row in results:
            tree.insert('', tk.END, values=row)

        tree.pack(fill=tk.BOTH, expand=True)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        btn_manage_data = tk.Button(btn_frame, text="Manage Data", command=self.manage_data)
        btn_manage_data.grid(row=0, column=0, padx=5)

        btn_logout = tk.Button(btn_frame, text="Logout", command=self.logout)
        btn_logout.grid(row=0, column=1, padx=5)

    def logout(self):
        self.user_id = None
        self.user_role = None
        if self.db_manager:
            self.db_manager.close_connection()
            self.db_manager = None
        self.login_screen()

    def add_courses(self):
        for widget in self.winfo_children():
            widget.destroy()

        label = tk.Label(self, text="เลือกวิชาที่ต้องการเพิ่ม (สูงสุด 3 วิชา)", font=("Arial", 16))
        label.pack(pady=10)

        columns = ('course_id', 'course_name', 'credits', 'department_id', 'instructor_id')
        tree = ttk.Treeview(self, columns=columns, show='headings')

        # กำหนดความกว้างของคอลัมน์
        tree.column('course_id', width=80, anchor='center')
        tree.column('course_name', width=200, anchor='w')
        tree.column('credits', width=80, anchor='center')
        tree.column('department_id', width=100, anchor='center')
        tree.column('instructor_id', width=100, anchor='center')

        for col in columns:
            tree.heading(col, text=col)

        # แสดงเฉพาะรายวิชาที่นักศึกษายังไม่ได้ลงทะเบียน
        query = '''
            SELECT * FROM Courses c
            WHERE c.course_id NOT IN (
                SELECT e.course_id FROM Enrollments e WHERE e.student_id = %s
            )
        '''
        self.db_manager.cursor.execute(query, (self.user_id,))
        results = self.db_manager.cursor.fetchall()

        for row in results:
            tree.insert('', tk.END, values=row)

        tree.pack(fill=tk.BOTH, expand=True)

        label_select = tk.Label(self, text="กรุณาใส่ course_id ที่ต้องการเพิ่ม (คั่นด้วยเครื่องหมายจุลภาค)")
        label_select.pack(pady=5)

        self.entry_courses = tk.Entry(self)
        self.entry_courses.pack()

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        btn_submit = tk.Button(btn_frame, text="Submit", command=self.submit_courses)
        btn_submit.grid(row=0, column=0, padx=5)

        if self.user_role == 'Admin':
            btn_back = tk.Button(btn_frame, text="ย้อนกลับ", command=self.show_all_enrollments)
        else:
            btn_back = tk.Button(btn_frame, text="ย้อนกลับ", command=self.show_enrollments)
        btn_back.grid(row=0, column=1, padx=5)

    def submit_courses(self):
        courses_input = self.entry_courses.get()
        course_ids = courses_input.split(',')
        course_ids = [cid.strip() for cid in course_ids]

        if len(course_ids) > 3:
            messagebox.showerror("ข้อผิดพลาด", "คุณสามารถเพิ่มรายวิชาได้สูงสุด 3 วิชา")
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
            messagebox.showerror("ข้อผิดพลาด",
                                 "รายวิชาต่อไปนี้ไม่สามารถเพิ่มได้: {}".format(', '.join(invalid_courses)))
            return

        confirmation = messagebox.askokcancel("ยืนยันการเพิ่มรายวิชา", "คุณแน่ใจหรือไม่ที่จะ Submit รายวิชานี้")

        if confirmation:
            for course_id in course_ids:
                # เพิ่มข้อมูลการลงทะเบียน
                self.db_manager.cursor.execute('''
                    INSERT INTO Enrollments (student_id, course_id, semester, year, enrollment_date, grade)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (self.user_id, course_id, 1, date.today().year, date.today(), None))
            self.db_manager.conn.commit()

            messagebox.showinfo("สำเร็จ", "เพิ่มรายวิชาเรียบร้อยแล้ว")
            if self.user_role == 'Admin':
                self.show_all_enrollments()
            else:
                self.show_enrollments()
        else:
            messagebox.showinfo("ยกเลิก", "การเพิ่มรายวิชาถูกยกเลิก")

    def manage_data(self):
        # หน้าจอสำหรับการจัดการข้อมูล (เพิ่ม, ลบ, แก้ไข) เฉพาะ Admin เท่านั้น
        for widget in self.winfo_children():
            widget.destroy()

        label = tk.Label(self, text="Manage Data", font=("Arial", 16))
        label.pack(pady=10)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        btn_add = tk.Button(btn_frame, text="Add Data", command=self.add_data_screen)
        btn_add.grid(row=0, column=0, padx=5)

        btn_update = tk.Button(btn_frame, text="Update Data", command=self.update_data_screen)
        btn_update.grid(row=0, column=1, padx=5)

        btn_delete = tk.Button(btn_frame, text="Delete Data", command=self.delete_data_screen)
        btn_delete.grid(row=0, column=2, padx=5)

        btn_back = tk.Button(self, text="ย้อนกลับ", command=self.show_all_enrollments)
        btn_back.pack(pady=10)

    def add_data_screen(self):
        # หน้าจอสำหรับเพิ่มข้อมูล
        for widget in self.winfo_children():
            widget.destroy()

        label = tk.Label(self, text="Add Data", font=("Arial", 16))
        label.pack(pady=10)

        label_table = tk.Label(self, text="Table Name:")
        label_table.pack()

        self.entry_table = tk.Entry(self)
        self.entry_table.pack()

        btn_load = tk.Button(self, text="Load Table", command=self.load_table_for_add)
        btn_load.pack(pady=5)

        btn_back = tk.Button(self, text="ย้อนกลับ", command=self.manage_data)
        btn_back.pack(pady=5)

    def load_table_for_add(self):
        table_name = self.entry_table.get()
        columns = self.db_manager.show_table_columns(table_name)
        if not columns:
            return

        # แสดงข้อมูลของตาราง
        for widget in self.winfo_children():
            if widget != self.entry_table and widget != self.entry_table.master:
                widget.destroy()

        label = tk.Label(self, text=f"Add Data to {table_name}", font=("Arial", 16))
        label.pack(pady=10)

        # แสดงข้อมูลในตาราง
        tree = ttk.Treeview(self, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor='center')

        query = f"SELECT * FROM {table_name}"
        self.db_manager.cursor.execute(query)
        results = self.db_manager.cursor.fetchall()

        for row in results:
            tree.insert('', tk.END, values=row)

        tree.pack(fill=tk.BOTH, expand=True)

        # สร้างฟิลด์สำหรับป้อนข้อมูลใหม่
        self.add_entries = {}
        frame_entries = tk.Frame(self)
        frame_entries.pack(pady=10)
        for idx, col in enumerate(columns):
            label_col = tk.Label(frame_entries, text=col)
            label_col.grid(row=0, column=idx, padx=5, pady=5)
            entry = tk.Entry(frame_entries)
            entry.grid(row=1, column=idx, padx=5, pady=5)
            self.add_entries[col] = entry

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        btn_submit = tk.Button(btn_frame, text="Add Data", command=lambda: self.add_data(table_name, columns))
        btn_submit.grid(row=0, column=0, padx=5)

        btn_back = tk.Button(btn_frame, text="ย้อนกลับ", command=self.add_data_screen)
        btn_back.grid(row=0, column=1, padx=5)

    def add_data(self, table_name, columns):
        values = []
        for col in columns:
            value = self.add_entries[col].get()
            values.append(value)
        try:
            self.db_manager.insert_data(table_name, columns, values)
            self.add_data_screen()  # กลับไปหน้าจอหลักของ Add Data
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_data_screen(self):
        # หน้าจอสำหรับแก้ไขข้อมูล
        for widget in self.winfo_children():
            widget.destroy()

        label = tk.Label(self, text="Update Data", font=("Arial", 16))
        label.pack(pady=10)

        label_table = tk.Label(self, text="Table Name:")
        label_table.pack()

        self.entry_table = tk.Entry(self)
        self.entry_table.pack()

        btn_load = tk.Button(self, text="Load Table", command=self.load_table_for_update)
        btn_load.pack(pady=5)

        btn_back = tk.Button(self, text="ย้อนกลับ", command=self.manage_data)
        btn_back.pack(pady=5)

    def load_table_for_update(self):
        table_name = self.entry_table.get()
        columns = self.db_manager.show_table_columns(table_name)
        if not columns:
            return

        # แสดงข้อมูลของตาราง
        for widget in self.winfo_children():
            if widget != self.entry_table and widget != self.entry_table.master:
                widget.destroy()

        label = tk.Label(self, text=f"Update Data in {table_name}", font=("Arial", 16))
        label.pack(pady=10)

        # แสดงข้อมูลในตาราง
        tree = ttk.Treeview(self, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor='center')

        query = f"SELECT * FROM {table_name}"
        self.db_manager.cursor.execute(query)
        results = self.db_manager.cursor.fetchall()

        for row in results:
            tree.insert('', tk.END, values=row)

        tree.pack(fill=tk.BOTH, expand=True)

        # สร้างฟิลด์สำหรับป้อนข้อมูลที่จะอัปเดต
        self.update_entries = {}
        frame_entries = tk.Frame(self)
        frame_entries.pack(pady=10)
        for idx, col in enumerate(columns):
            label_col = tk.Label(frame_entries, text=col)
            label_col.grid(row=0, column=idx, padx=5, pady=5)
            entry = tk.Entry(frame_entries)
            entry.grid(row=1, column=idx, padx=5, pady=5)
            self.update_entries[col] = entry

        label_condition = tk.Label(self, text="Conditions (เช่น column1=value1 AND column2=value2):")
        label_condition.pack(pady=5)

        self.entry_condition = tk.Entry(self)
        self.entry_condition.pack()

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        btn_submit = tk.Button(btn_frame, text="Update Data", command=lambda: self.update_data(table_name))
        btn_submit.grid(row=0, column=0, padx=5)

        btn_back = tk.Button(btn_frame, text="ย้อนกลับ", command=self.update_data_screen)
        btn_back.grid(row=0, column=1, padx=5)

    def update_data(self, table_name):
        updates = {}
        for col, entry in self.update_entries.items():
            value = entry.get()
            if value:
                updates[col] = value
        conditions_input = self.entry_condition.get()
        conditions = [cond.strip() for cond in conditions_input.split('AND')]
        try:
            self.db_manager.update_data(table_name, updates, conditions)
            self.update_data_screen()  # กลับไปหน้าจอหลักของ Update Data
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_data_screen(self):
        # หน้าจอสำหรับลบข้อมูล
        for widget in self.winfo_children():
            widget.destroy()

        label = tk.Label(self, text="Delete Data", font=("Arial", 16))
        label.pack(pady=10)

        label_table = tk.Label(self, text="Table Name:")
        label_table.pack()

        self.entry_table = tk.Entry(self)
        self.entry_table.pack()

        btn_load = tk.Button(self, text="Load Table", command=self.load_table_for_delete)
        btn_load.pack(pady=5)

        btn_back = tk.Button(self, text="ย้อนกลับ", command=self.manage_data)
        btn_back.pack(pady=5)

    def load_table_for_delete(self):
        table_name = self.entry_table.get()
        columns = self.db_manager.show_table_columns(table_name)
        if not columns:
            return

        # แสดงข้อมูลของตาราง
        for widget in self.winfo_children():
            if widget != self.entry_table and widget != self.entry_table.master:
                widget.destroy()

        label = tk.Label(self, text=f"Delete Data from {table_name}", font=("Arial", 16))
        label.pack(pady=10)

        # แสดงข้อมูลในตาราง
        tree = ttk.Treeview(self, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor='center')

        query = f"SELECT * FROM {table_name}"
        self.db_manager.cursor.execute(query)
        results = self.db_manager.cursor.fetchall()

        for row in results:
            tree.insert('', tk.END, values=row)

        tree.pack(fill=tk.BOTH, expand=True)

        label_condition = tk.Label(self, text="Condition (เช่น column=value):")
        label_condition.pack(pady=5)

        self.entry_condition = tk.Entry(self)
        self.entry_condition.pack()

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        btn_submit = tk.Button(btn_frame, text="Delete Data", command=lambda: self.delete_data(table_name))
        btn_submit.grid(row=0, column=0, padx=5)

        btn_back = tk.Button(btn_frame, text="ย้อนกลับ", command=self.delete_data_screen)
        btn_back.grid(row=0, column=1, padx=5)

    def delete_data(self, table_name):
        condition = self.entry_condition.get()
        try:
            self.db_manager.delete_data(table_name, condition)
            self.delete_data_screen()  # กลับไปหน้าจอหลักของ Delete Data
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_closing(self):
        if self.db_manager:
            self.db_manager.close_connection()
        self.destroy()


# สร้างและรันแอปพลิเคชัน
if __name__ == "__main__":
    app = Application()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
