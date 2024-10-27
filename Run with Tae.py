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

    # ฟังก์ชันอื่นๆ เช่น show_table_columns, insert_data, delete_data, update_data
    # จะเหมือนกับที่เรามีอยู่แล้ว

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

    def insert_data(self, table_name, values):
        # ฟังก์ชันเหมือนเดิม
        pass

    def delete_data(self, table_name, condition):
        # ฟังก์ชันเหมือนเดิม
        pass

    def update_data(self, table_name, updates, condition):
        # ฟังก์ชันเหมือนเดิม
        pass


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

    # ฟังก์ชันสำหรับเพิ่ม, ลบ, แก้ไขข้อมูลจะเหมือนเดิม

    def add_data_screen(self):
        # หน้าจอสำหรับเพิ่มข้อมูล
        pass  # ฟังก์ชันเหมือนเดิม

    def add_data(self):
        # ฟังก์ชันเหมือนเดิม
        pass

    def update_data_screen(self):
        # หน้าจอสำหรับแก้ไขข้อมูล
        pass  # ฟังก์ชันเหมือนเดิม

    def update_data(self):
        # ฟังก์ชันเหมือนเดิม
        pass

    def delete_data_screen(self):
        # หน้าจอสำหรับลบข้อมูล
        pass  # ฟังก์ชันเหมือนเดิม

    def delete_data(self):
        # ฟังก์ชันเหมือนเดิม
        pass

    def on_closing(self):
        if self.db_manager:
            self.db_manager.close_connection()
        self.destroy()


# สร้างและรันแอปพลิเคชัน
if __name__ == "__main__":
    app = Application()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
