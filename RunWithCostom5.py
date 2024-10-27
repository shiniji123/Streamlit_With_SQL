import customtkinter as tk
from tkinter import messagebox, ttk
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

    def execute_query(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error executing query: {err}")
            messagebox.showerror("Database Error", f"Error executing query: {err}")
            return []


# คลาสสำหรับการจัดการ GUI
class GUIManager:
    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.db_manager = None
        self.user_role = None
        self.user_id = None
        self.is_fullscreen = False
        self.create_widgets()

    def set_db_manager(self, db_manager):
        self.db_manager = db_manager

    def create_widgets(self):
        self.login_screen()

    def clear_widgets(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_cordinate = int((screen_width / 2) - (width / 2))
        y_cordinate = int((screen_height / 2) - (height / 2))
        self.root.geometry(f"{width}x{height}+{x_cordinate}+{y_cordinate}")

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)
        if not self.is_fullscreen:
            self.center_window(1000, 700)

    def login_screen(self):
        self.clear_widgets()

        label_title = tk.CTkLabel(self.root, text="ระบบลงทะเบียนนักศึกษา", font=("Arial", 24))
        label_title.pack(pady=20)

        frame = tk.CTkFrame(self.root)
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

        btn_login = tk.CTkButton(self.root, text="เข้าสู่ระบบ", command=self.app.login, font=("Arial", 16))
        btn_login.pack(pady=10)

        btn_fullscreen = tk.CTkButton(self.root, text="Full Screen", command=self.toggle_fullscreen, font=("Arial", 16))
        btn_fullscreen.pack(pady=5)

    def show_enrollments(self):
        self.clear_widgets()

        label = tk.CTkLabel(self.root, text="ข้อมูลการลงทะเบียนของคุณ", font=("Arial", 20))
        label.pack(pady=10)

        columns = (
            'student_id', 'first_name', 'last_name', 'course_id', 'course_name', 'credits', 'semester', 'year', 'grade')

        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 14))
        style.configure("Treeview", font=("Arial", 12), rowheight=30)
        tree = ttk.Treeview(self.root, columns=columns, show='headings', style="Treeview")

        # กำหนดความกว้างของคอลัมน์ให้เหมาะสม
        tree.column('student_id', width=100, anchor='center')
        tree.column('first_name', width=120, anchor='center')
        tree.column('last_name', width=120, anchor='center')
        tree.column('course_id', width=100, anchor='center')
        tree.column('course_name', width=200, anchor='w')
        tree.column('credits', width=80, anchor='center')
        tree.column('semester', width=100, anchor='center')
        tree.column('year', width=80, anchor='center')
        tree.column('grade', width=80, anchor='center')

        for col in columns:
            tree.heading(col, text=col)

        query = '''
            SELECT s.student_id, s.first_name, s.last_name, c.course_id, c.course_name, c.credits, e.semester, e.year, e.grade
            FROM Students s
            JOIN Enrollments e ON s.student_id = e.student_id
            JOIN Courses c ON e.course_id = c.course_id
            WHERE s.student_id = %s
        '''
        results = self.db_manager.execute_query(query, (self.user_id,))
        for row in results:
            tree.insert('', tk.END, values=row)

        tree.pack(fill=tk.BOTH, expand=True)

        btn_frame = tk.CTkFrame(self.root)
        btn_frame.pack(pady=10)

        btn_add_course = tk.CTkButton(btn_frame, text="Add รายวิชา", command=self.app.add_courses, font=("Arial", 16))
        btn_add_course.grid(row=0, column=0, padx=5)

        btn_logout = tk.CTkButton(btn_frame, text="Logout", command=self.app.logout, font=("Arial", 16))
        btn_logout.grid(row=0, column=1, padx=5)

    def show_all_enrollments(self):
        self.clear_widgets()

        label = tk.CTkLabel(self.root, text="ข้อมูลการลงทะเบียนของนักศึกษาทุกคน", font=("Arial", 20))
        label.pack(pady=10)

        columns = (
            'student_id', 'first_name', 'last_name', 'course_id', 'course_name', 'credits', 'semester', 'year', 'grade')

        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 14))
        style.configure("Treeview", font=("Arial", 12), rowheight=30)
        tree = ttk.Treeview(self.root, columns=columns, show='headings', style="Treeview")

        # กำหนดความกว้างของคอลัมน์ให้เหมาะสม
        tree.column('student_id', width=100, anchor='center')
        tree.column('first_name', width=120, anchor='center')
        tree.column('last_name', width=120, anchor='center')
        tree.column('course_id', width=100, anchor='center')
        tree.column('course_name', width=200, anchor='w')
        tree.column('credits', width=80, anchor='center')
        tree.column('semester', width=100, anchor='center')
        tree.column('year', width=80, anchor='center')
        tree.column('grade', width=80, anchor='center')

        for col in columns:
            tree.heading(col, text=col)

        query = '''
            SELECT s.student_id, s.first_name, s.last_name, c.course_id, c.course_name, c.credits, e.semester, e.year, e.grade
            FROM Students s
            JOIN Enrollments e ON s.student_id = e.student_id
            JOIN Courses c ON e.course_id = c.course_id
        '''
        results = self.db_manager.execute_query(query)
        for row in results:
            tree.insert('', tk.END, values=row)

        tree.pack(fill=tk.BOTH, expand=True)

        btn_frame = tk.CTkFrame(self.root)
        btn_frame.pack(pady=10)

        btn_manage_data = tk.CTkButton(btn_frame, text="Manage Data", command=self.app.manage_data, font=("Arial", 16))
        btn_manage_data.grid(row=0, column=0, padx=5)

        btn_logout = tk.CTkButton(btn_frame, text="Logout", command=self.app.logout, font=("Arial", 16))
        btn_logout.grid(row=0, column=1, padx=5)

    def add_courses_screen(self):
        self.clear_widgets()

        label = tk.CTkLabel(self.root, text="เลือกวิชาที่ต้องการเพิ่ม (สูงสุด 3 วิชา)", font=("Arial", 20))
        label.pack(pady=10)

        columns = ('course_id', 'course_name', 'credits', 'department_id', 'instructor_id')

        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 14))
        style.configure("Treeview", font=("Arial", 12), rowheight=30)
        tree = ttk.Treeview(self.root, columns=columns, show='headings', style="Treeview")

        # กำหนดความกว้างของคอลัมน์
        tree.column('course_id', width=100, anchor='center')
        tree.column('course_name', width=250, anchor='w')
        tree.column('credits', width=80, anchor='center')
        tree.column('department_id', width=120, anchor='center')
        tree.column('instructor_id', width=120, anchor='center')

        for col in columns:
            tree.heading(col, text=col)

        # แสดงเฉพาะรายวิชาที่นักศึกษายังไม่ได้ลงทะเบียน
        query = '''
            SELECT c.course_id, c.course_name, c.credits, c.department_id, c.instructor_id
            FROM Courses c
            WHERE c.course_id NOT IN (
                SELECT e.course_id FROM Enrollments e WHERE e.student_id = %s
            )
        '''
        results = self.db_manager.execute_query(query, (self.user_id,))
        for row in results:
            tree.insert('', tk.END, values=row)

        tree.pack(fill=tk.BOTH, expand=True)

        label_select = tk.CTkLabel(self.root, text="กรุณาใส่ course_id ที่ต้องการเพิ่ม (คั่นด้วยเครื่องหมายจุลภาค)",
                                   font=("Arial", 16))
        label_select.pack(pady=5)

        self.entry_courses = tk.CTkEntry(self.root, font=("Arial", 16))
        self.entry_courses.pack()

        btn_frame = tk.CTkFrame(self.root)
        btn_frame.pack(pady=10)

        btn_submit = tk.CTkButton(btn_frame, text="Submit", command=self.app.submit_courses, font=("Arial", 16))
        btn_submit.grid(row=0, column=0, padx=5)

        btn_back = tk.CTkButton(btn_frame, text="ย้อนกลับ", command=self.app.back_after_add_courses, font=("Arial", 16))
        btn_back.grid(row=0, column=1, padx=5)

    def manage_data_screen(self):
        self.clear_widgets()

        label = tk.CTkLabel(self.root, text="Manage Data", font=("Arial", 20))
        label.pack(pady=10)

        btn_frame = tk.CTkFrame(self.root)
        btn_frame.pack(pady=10)

        btn_add = tk.CTkButton(btn_frame, text="Add Data", command=self.app.add_data_screen, font=("Arial", 16))
        btn_add.grid(row=0, column=0, padx=5)

        btn_update = tk.CTkButton(btn_frame, text="Update Data", command=self.app.update_data_screen,
                                  font=("Arial", 16))
        btn_update.grid(row=0, column=1, padx=5)

        btn_delete = tk.CTkButton(btn_frame, text="Delete Data", command=self.app.delete_data_screen,
                                  font=("Arial", 16))
        btn_delete.grid(row=0, column=2, padx=5)

        btn_back = tk.CTkButton(self.root, text="ย้อนกลับ", command=self.app.show_all_enrollments, font=("Arial", 16))
        btn_back.pack(pady=10)

    # ฟังก์ชันอื่นๆ สำหรับ GUI สามารถเพิ่มได้ที่นี่ เช่น add_data_screen, update_data_screen, delete_data_screen เป็นต้น
    # เนื่องจาก GUIManager จะถูกเรียกผ่าน Application คลาส จึงทำให้ Application ควบคุมการทำงานได้


# คลาสหลักสำหรับแอปพลิเคชัน
class Application:
    def __init__(self):
        self.root = tk.CTk()
        tk.set_appearance_mode("light")  # เปลี่ยนโหมดสีตามต้องการ
        tk.set_default_color_theme("blue")
        self.root.title("Student Enrollment System")
        self.root.geometry("1000x700")
        self.center_window(1000, 700)  # จัดตำแหน่งหน้าต่างให้อยู่ตรงกลาง

        self.db_manager = None
        self.user_role = None  # 'Admin' or 'Student'
        self.user_id = None  # 'admin_id' or 'student_id'
        self.is_fullscreen = False  # สำหรับตรวจสอบสถานะ Full Screen

        self.gui_manager = GUIManager(self.root, self)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def center_window(self, width, height):
        # ฟังก์ชันสำหรับจัดตำแหน่งหน้าต่างให้อยู่ตรงกลางหน้าจอ
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_cordinate = int((screen_width / 2) - (width / 2))
        y_cordinate = int((screen_height / 2) - (height / 2))
        self.root.geometry(f"{width}x{height}+{x_cordinate}+{y_cordinate}")

    def run(self):
        self.root.mainloop()

    def login(self):
        user_id = self.gui_manager.entry_id.get()
        password = self.gui_manager.entry_password.get()
        self.user_role = self.gui_manager.role_var.get()

        if self.user_role == 'Admin':
            # เชื่อมต่อฐานข้อมูลในฐานะ Admin
            self.db_manager = DatabaseManager('Admin')
            query = "SELECT * FROM Admins WHERE admin_id=%s AND admin_password=%s"
        else:
            # เชื่อมต่อฐานข้อมูลในฐานะ Student
            self.db_manager = DatabaseManager('Student')
            query = "SELECT * FROM Students WHERE student_id=%s AND student_password=%s"

        self.gui_manager.set_db_manager(self.db_manager)
        self.db_manager.cursor.execute(query, (user_id, password))
        result = self.db_manager.cursor.fetchone()

        if result:
            messagebox.showinfo("เข้าสู่ระบบสำเร็จ", f"ยินดีต้อนรับคุณ {result[1]} {result[2]}")
            self.user_id = user_id
            if self.user_role == 'Admin':
                self.gui_manager.show_all_enrollments()
            else:
                self.gui_manager.show_enrollments()
        else:
            messagebox.showerror("ข้อผิดพลาด", "รหัสผู้ใช้หรือรหัสผ่านของคุณไม่ถูกต้อง")
            self.db_manager.close_connection()
            self.db_manager = None

    def logout(self):
        self.user_id = None
        self.user_role = None
        if self.db_manager:
            self.db_manager.close_connection()
            self.db_manager = None
        self.gui_manager.login_screen()

    def add_courses(self):
        self.gui_manager.add_courses_screen()

    def back_after_add_courses(self):
        if self.user_role == 'Admin':
            self.gui_manager.show_all_enrollments()
        else:
            self.gui_manager.show_enrollments()

    def submit_courses(self):
        courses_input = self.gui_manager.entry_courses.get()
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
        available_courses = [str(row[0]) for row in self.db_manager.execute_query(query, (self.user_id,))]

        invalid_courses = [cid for cid in course_ids if cid not in available_courses]

        if invalid_courses:
            messagebox.showerror("ข้อผิดพลาด",
                                 "รายวิชาต่อไปนี้ไม่สามารถเพิ่มได้: {}".format(', '.join(invalid_courses)))
            return

        confirmation = messagebox.askokcancel("ยืนยันการเพิ่มรายวิชา", "คุณแน่ใจหรือไม่ที่จะ Submit รายวิชานี้")

        if confirmation:
            for course_id in course_ids:
                # เพิ่มข้อมูลการลงทะเบียน
                try:
                    self.db_manager.cursor.execute('''
                        INSERT INTO Enrollments (student_id, course_id, semester, year, enrollment_date, grade)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    ''', (self.user_id, course_id, 1, date.today().year, date.today(), None))
                except mysql.connector.Error as error:
                    messagebox.showerror("Database Error", f"Failed to insert course {course_id}: {error}")
                    return
            self.db_manager.conn.commit()

            messagebox.showinfo("สำเร็จ", "เพิ่มรายวิชาเรียบร้อยแล้ว")
            if self.user_role == 'Admin':
                self.gui_manager.show_all_enrollments()
            else:
                self.gui_manager.show_enrollments()
        else:
            messagebox.showinfo("ยกเลิก", "การเพิ่มรายวิชาถูกยกเลิก")

    def manage_data(self):
        self.gui_manager.manage_data_screen()

    # ฟังก์ชันสำหรับ Add, Update, Delete Data Screen
    def add_data_screen(self):
        self.gui_manager.add_data_screen()

    def update_data_screen(self):
        self.gui_manager.update_data_screen()

    def delete_data_screen(self):
        self.gui_manager.delete_data_screen()

    def on_closing(self):
        if self.db_manager:
            self.db_manager.close_connection()
        self.root.destroy()


# สร้างและรันแอปพลิเคชัน
if __name__ == "__main__":
    app = Application()
    app.run()
