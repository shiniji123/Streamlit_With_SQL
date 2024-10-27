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

# คลาสสำหรับการจัดการหน้าจอ Login
class LoginScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
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
        user_role = self.role_var.get()

        if user_role == 'Admin':
            db_manager = DatabaseManager('Admin')
            query = "SELECT * FROM Admins WHERE admin_id=%s AND admin_password=%s"
        else:
            db_manager = DatabaseManager('Student')
            query = "SELECT * FROM Students WHERE student_id=%s AND student_password=%s"

        db_manager.cursor.execute(query, (user_id, password))
        result = db_manager.cursor.fetchone()

        if result:
            messagebox.showinfo("เข้าสู่ระบบสำเร็จ", f"ยินดีต้อนรับคุณ {result[1]} {result[2]}")
            self.controller.show_enrollment_screen(user_role, user_id)
        else:
            messagebox.showerror("ข้อผิดพลาด", "รหัสผู้ใช้หรือรหัสผ่านของคุณไม่ถูกต้อง")
        db_manager.close_connection()

# คลาสสำหรับจัดการหน้าจอ Enrollment
class EnrollmentScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

    def show_enrollments(self, user_role, user_id):
        for widget in self.winfo_children():
            widget.destroy()

        label = tk.Label(self, text="ข้อมูลการลงทะเบียนของคุณ", font=("Arial", 16))
        label.pack(pady=10)

        columns = (
            'student_id', 'first_name', 'last_name', 'course_id', 'course_name', 'credits', 'semester', 'year', 'grade'
        )
        tree = ttk.Treeview(self, columns=columns, show='headings')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor='center')

        db_manager = DatabaseManager(user_role)
        query = '''
            SELECT s.student_id, s.first_name, s.last_name, c.course_id, c.course_name, c.credits, e.semester, e.year, e.grade
            FROM Students s
            JOIN Enrollments e ON s.student_id = e.student_id
            JOIN Courses c ON e.course_id = c.course_id
            WHERE s.student_id = %s
        '''
        db_manager.cursor.execute(query, (user_id,))
        results = db_manager.cursor.fetchall()

        for row in results:
            tree.insert('', tk.END, values=row)

        tree.pack(fill=tk.BOTH, expand=True)
        db_manager.close_connection()

        btn_logout = tk.Button(self, text="Logout", command=self.controller.show_login_screen)
        btn_logout.pack(pady=10)

# คลาสหลักสำหรับแอปพลิเคชัน
class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Student Enrollment System")
        self.geometry("800x500")
        self.frames = {}

        self.show_login_screen()

    def show_login_screen(self):
        frame = LoginScreen(self, self)
        frame.pack(fill="both", expand=True)
        self.frames['LoginScreen'] = frame

    def show_enrollment_screen(self, user_role, user_id):
        frame = EnrollmentScreen(self, self)
        frame.pack(fill="both", expand=True)
        frame.show_enrollments(user_role, user_id)
        self.frames['EnrollmentScreen'] = frame

# สร้างและรันแอปพลิเคชัน
if __name__ == "__main__":
    app = Application()
    app.mainloop()
