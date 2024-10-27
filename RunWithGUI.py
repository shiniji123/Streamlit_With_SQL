import customtkinter as tk
from tkinter import messagebox
import mysql.connector
from datetime import date
from tkinter import ttk

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

    def get_tables(self):
        try:
            self.cursor.execute("SHOW TABLES")
            tables = [table[0] for table in self.cursor.fetchall()]
            return tables
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            messagebox.showerror("Database Error", f"Error fetching tables: {err}")
            return []

    def insert_data(self, table_name, columns, values):
        try:
            columns_str = ', '.join(columns)
            placeholders = ', '.join(['%s'] * len(values))
            query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
            self.cursor.execute(query, values)
            self.conn.commit()
            print(f"1 record inserted successfully into {table_name}")
            messagebox.showinfo("Success", f"Data inserted into {table_name} successfully.")
        except mysql.connector.Error as error:
            print(f"Failed to insert data into MySQL table {table_name}: {error}")
            messagebox.showerror("Database Error", f"Failed to insert data: {error}")

    # ... (ฟังก์ชันอื่นๆ เหมือนเดิม)

# คลาสสำหรับส่วนติดต่อผู้ใช้
class Application(tk.CTk):
    def __init__(self):
        super().__init__()
        tk.set_appearance_mode("light")  # เปลี่ยนโหมดสีตามต้องการ
        tk.set_default_color_theme("blue")
        self.title("Student Enrollment System")
        self.geometry("1000x700")
        self.center_window(1000, 700)  # เรียกใช้ฟังก์ชันเพื่อจัดตำแหน่งหน้าต่างให้อยู่ตรงกลาง
        self.db_manager = None
        self.user_role = None  # 'Admin' or 'Student'
        self.user_id = None  # 'admin_id' or 'student_id'
        self.is_fullscreen = False  # สำหรับตรวจสอบสถานะ Full Screen
        self.create_widgets()

    def center_window(self, width, height):
        # ฟังก์ชันสำหรับจัดตำแหน่งหน้าต่างให้อยู่ตรงกลางหน้าจอ
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_cordinate = int((screen_width/2) - (width/2))
        y_cordinate = int((screen_height/2) - (height/2))
        self.geometry(f"{width}x{height}+{x_cordinate}+{y_cordinate}")

    def create_widgets(self):
        self.login_screen()

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        self.attributes("-fullscreen", self.is_fullscreen)
        if not self.is_fullscreen:
            self.center_window(1000, 700)

    def login_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

        label_title = tk.CTkLabel(self, text="ระบบลงทะเบียนนักศึกษา", font=("Arial", 24))
        label_title.pack(pady=20)

        frame = tk.CTkFrame(self)
        frame.pack(pady=10)

        label_role = tk.CTkLabel(frame, text="เข้าสู่ระบบในฐานะ", font=("Arial", 18))
        label_role.grid(row=0, column=0, padx=5, pady=5)

        self.role_var = tk.StringVar(value="Student")
        radio_student = tk.CTkRadioButton(frame, text="Student", variable=self.role_var, value="Student", font=("Arial", 16))
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

        btn_fullscreen = tk.CTkButton(self, text="Full Screen", command=self.toggle_fullscreen, font=("Arial", 16))
        btn_fullscreen.pack(pady=5)

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

        label = tk.CTkLabel(self, text="ข้อมูลการลงทะเบียนของคุณ", font=("Arial", 20))
        label.pack(pady=10)

        columns = (
            'student_id', 'first_name', 'last_name', 'course_id', 'course_name', 'credits', 'semester', 'year', 'grade')
        # customTkinter ไม่มี Treeview ต้องใช้ของ tkinter.ttk
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 14))
        style.configure("Treeview", font=("Arial", 12), rowheight=30)
        tree = ttk.Treeview(self, columns=columns, show='headings', style="Treeview")

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
        self.db_manager.cursor.execute(query, (self.user_id,))
        results = self.db_manager.cursor.fetchall()

        for row in results:
            tree.insert('', tk.END, values=row)

        tree.pack(fill=tk.BOTH, expand=True)

        btn_frame = tk.CTkFrame(self)
        btn_frame.pack(pady=10)

        btn_add_course = tk.CTkButton(btn_frame, text="Add รายวิชา", command=self.add_courses, font=("Arial", 16))
        btn_add_course.grid(row=0, column=0, padx=5)

        btn_logout = tk.CTkButton(btn_frame, text="Logout", command=self.logout, font=("Arial", 16))
        btn_logout.grid(row=0, column=1, padx=5)

    def show_all_enrollments(self):
        for widget in self.winfo_children():
            widget.destroy()

        label = tk.CTkLabel(self, text="ข้อมูลการลงทะเบียนของนักศึกษาทุกคน", font=("Arial", 20))
        label.pack(pady=10)

        columns = (
            'student_id', 'first_name', 'last_name', 'course_id', 'course_name', 'credits', 'semester', 'year', 'grade')
        from tkinter import ttk
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 14))
        style.configure("Treeview", font=("Arial", 12), rowheight=30)
        tree = ttk.Treeview(self, columns=columns, show='headings', style="Treeview")

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
        self.db_manager.cursor.execute(query)
        results = self.db_manager.cursor.fetchall()

        for row in results:
            tree.insert('', tk.END, values=row)

        tree.pack(fill=tk.BOTH, expand=True)

        btn_frame = tk.CTkFrame(self)
        btn_frame.pack(pady=10)

        btn_manage_data = tk.CTkButton(btn_frame, text="Manage Data", command=self.manage_data, font=("Arial", 16))
        btn_manage_data.grid(row=0, column=0, padx=5)

        btn_logout = tk.CTkButton(btn_frame, text="Logout", command=self.logout, font=("Arial", 16))
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

        label = tk.CTkLabel(self, text="เลือกวิชาที่ต้องการเพิ่ม (สูงสุด 3 วิชา)", font=("Arial", 20))
        label.pack(pady=10)

        columns = ('course_id', 'course_name', 'credits', 'department_id', 'instructor_id')
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 14))
        style.configure("Treeview", font=("Arial", 12), rowheight=30)
        tree = ttk.Treeview(self, columns=columns, show='headings', style="Treeview")

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

        label_select = tk.CTkLabel(self, text="กรุณาใส่ course_id ที่ต้องการเพิ่ม (คั่นด้วยเครื่องหมายจุลภาค)", font=("Arial", 16))
        label_select.pack(pady=5)

        self.entry_courses = tk.CTkEntry(self, font=("Arial", 16))
        self.entry_courses.pack()

        btn_frame = tk.CTkFrame(self)
        btn_frame.pack(pady=10)

        btn_submit = tk.CTkButton(btn_frame, text="Submit", command=self.submit_courses, font=("Arial", 16))
        btn_submit.grid(row=0, column=0, padx=5)

        if self.user_role == 'Admin':
            btn_back = tk.CTkButton(btn_frame, text="ย้อนกลับ", command=self.show_all_enrollments, font=("Arial", 16))
        else:
            btn_back = tk.CTkButton(btn_frame, text="ย้อนกลับ", command=self.show_enrollments, font=("Arial", 16))
        btn_back.grid(row=0, column=1, padx=5)

    def manage_data(self):
        # หน้าจอสำหรับการจัดการข้อมูล (เพิ่ม, ลบ, แก้ไข) เฉพาะ Admin เท่านั้น
        for widget in self.winfo_children():
            widget.destroy()

        label = tk.CTkLabel(self, text="Manage Data", font=("Arial", 20))
        label.pack(pady=10)

        btn_frame = tk.CTkFrame(self)
        btn_frame.pack(pady=10)

        btn_add = tk.CTkButton(btn_frame, text="Add Data", command=self.add_data_screen, font=("Arial", 16))
        btn_add.grid(row=0, column=0, padx=5)

        btn_update = tk.CTkButton(btn_frame, text="Update Data", command=self.update_data_screen, font=("Arial", 16))
        btn_update.grid(row=0, column=1, padx=5)

        btn_delete = tk.CTkButton(btn_frame, text="Delete Data", command=self.delete_data_screen, font=("Arial", 16))
        btn_delete.grid(row=0, column=2, padx=5)

        btn_back = tk.CTkButton(self, text="ย้อนกลับ", command=self.show_all_enrollments, font=("Arial", 16))
        btn_back.pack(pady=10)

    def add_data_screen(self):
        # หน้าจอสำหรับเพิ่มข้อมูล
        for widget in self.winfo_children():
            widget.destroy()

        label = tk.CTkLabel(self, text="Add Data", font=("Arial", 20))
        label.pack(pady=10)

        frame_select = tk.CTkFrame(self)
        frame_select.pack(pady=10)

        label_table = tk.CTkLabel(frame_select, text="เลือก Table:", font=("Arial", 16))
        label_table.grid(row=0, column=0, padx=5, pady=5)

        self.selected_table = tk.StringVar()
        tables = self.db_manager.get_tables()
        self.combobox_tables = ttk.Combobox(frame_select, values=tables, state="readonly", textvariable=self.selected_table, font=("Arial", 14))
        self.combobox_tables.grid(row=0, column=1, padx=5, pady=5)

        btn_load = tk.CTkButton(frame_select, text="Load Table", command=self.load_table_for_add, font=("Arial", 16))
        btn_load.grid(row=0, column=2, padx=5, pady=5)

        btn_back = tk.CTkButton(self, text="ย้อนกลับ", command=self.manage_data, font=("Arial", 16))
        btn_back.pack(pady=5)

    def load_table_for_add(self):
        table_name = self.selected_table.get()
        if not table_name:
            messagebox.showerror("Error", "กรุณาเลือก Table ที่ต้องการเพิ่มข้อมูล")
            return

        columns = self.db_manager.show_table_columns(table_name)
        if not columns:
            return

        # แสดงข้อมูลของตาราง
        for widget in self.winfo_children():
            widget.destroy()

        label = tk.CTkLabel(self, text=f"Add Data to {table_name}", font=("Arial", 20))
        label.pack(pady=10)

        # แสดงข้อมูลในตาราง
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 14))
        style.configure("Treeview", font=("Arial", 12), rowheight=30)
        tree = ttk.Treeview(self, columns=columns, show='headings', style="Treeview")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor='center', width=100)

        query = f"SELECT * FROM {table_name}"
        self.db_manager.cursor.execute(query)
        results = self.db_manager.cursor.fetchall()

        for row in results:
            tree.insert('', tk.END, values=row)

        tree.pack(fill=tk.BOTH, expand=True)

        # สร้างฟิลด์สำหรับป้อนข้อมูลใหม่
        self.add_entries = {}
        frame_entries = tk.CTkScrollableFrame(self, width=900, height=200)
        frame_entries.pack(pady=10, fill=tk.X, padx=10)

        for idx, col in enumerate(columns):
            label_col = tk.CTkLabel(frame_entries, text=col, font=("Arial", 14))
            label_col.grid(row=0, column=idx, padx=5, pady=5)
            entry = tk.CTkEntry(frame_entries, font=("Arial", 14))
            entry.grid(row=1, column=idx, padx=5, pady=5)
            self.add_entries[col] = entry

        btn_frame = tk.CTkFrame(self)
        btn_frame.pack(pady=10)

        btn_submit = tk.CTkButton(btn_frame, text="Add Data", command=lambda: self.add_data(table_name, columns), font=("Arial", 16))
        btn_submit.grid(row=0, column=0, padx=5)

        btn_back = tk.CTkButton(btn_frame, text="ย้อนกลับ", command=self.add_data_screen, font=("Arial", 16))
        btn_back.grid(row=0, column=1, padx=5)

    def add_data(self, table_name, columns):
        values = []
        for col in columns:
            value = self.add_entries[col].get()
            # คุณสามารถเพิ่มการตรวจสอบข้อมูลที่นี่
            values.append(value)
        try:
            self.db_manager.insert_data(table_name, columns, values)
            messagebox.showinfo("Success", f"เพิ่มข้อมูลใน {table_name} สำเร็จแล้ว")
            self.add_data_screen()  # กลับไปหน้าจอหลักของ Add Data
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ... (ฟังก์ชันอื่นๆ เหมือนเดิม)

    def on_closing(self):
        if self.db_manager:
            self.db_manager.close_connection()
        self.destroy()

# สร้างและรันแอปพลิเคชัน
if __name__ == "__main__":
    app = Application()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
