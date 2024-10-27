import customtkinter as tk
from tkinter import messagebox
import mysql.connector
from datetime import date

# Function to connect to the database as Admin
def connect_to_db_admin():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="sesar123",
        database="education_sector"
    )

# Function to connect to the database as Student
def connect_to_db_student():
    return mysql.connector.connect(
        host="localhost",
        user="student",
        password="1234",
        database="education_sector"
    )

# Class for connecting and managing the database
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

# Class for the User Interface
class Application(tk.CTk):
    def __init__(self):
        super().__init__()
        tk.set_appearance_mode("light")  # Change appearance mode as desired
        tk.set_default_color_theme("blue")
        self.title("Student Enrollment System")
        self.geometry("1000x700")
        self.center_window(1000, 700)  # Call function to center the window
        self.db_manager = None
        self.user_role = None  # 'Admin' or 'Student'
        self.user_id = None  # 'admin_id' or 'student_id'
        self.is_fullscreen = False  # To check Full Screen status
        self.create_widgets()

    def center_window(self, width, height):
        # Function to center the window on the screen
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

        label_title = tk.CTkLabel(self, text="Student Enrollment System", font=("Arial", 24))
        label_title.pack(pady=20)

        frame = tk.CTkFrame(self)
        frame.pack(pady=10)

        label_role = tk.CTkLabel(frame, text="Login as", font=("Arial", 18))
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

        btn_login = tk.CTkButton(self, text="Login", command=self.login, font=("Arial", 16))
        btn_login.pack(pady=10)

        btn_fullscreen = tk.CTkButton(self, text="Full Screen", command=self.toggle_fullscreen, font=("Arial", 16))
        btn_fullscreen.pack(pady=5)

    def login(self):
        user_id = self.entry_id.get()
        password = self.entry_password.get()
        self.user_role = self.role_var.get()

        if self.user_role == 'Admin':
            # Connect to the database as Admin
            self.db_manager = DatabaseManager('Admin')
            query = "SELECT * FROM Admins WHERE admin_id=%s AND admin_password=%s"
        else:
            # Connect to the database as Student
            self.db_manager = DatabaseManager('Student')
            query = "SELECT * FROM Students WHERE student_id=%s AND student_password=%s"

        self.db_manager.cursor.execute(query, (user_id, password))
        result = self.db_manager.cursor.fetchone()

        if result:
            messagebox.showinfo("Login Successful", f"Welcome {result[1]} {result[2]}")
            self.user_id = user_id
            if self.user_role == 'Admin':
                self.show_all_enrollments()
            else:
                self.show_enrollments()
        else:
            messagebox.showerror("Error", "Your username or password is incorrect")
            self.db_manager.close_connection()
            self.db_manager = None

    def show_enrollments(self):
        for widget in self.winfo_children():
            widget.destroy()

        label = tk.CTkLabel(self, text="Your Enrollment Information", font=("Arial", 20))
        label.pack(pady=10)

        columns = (
            'student_id', 'first_name', 'last_name', 'course_id', 'course_name', 'credits', 'semester', 'year', 'grade')
        # customTkinter does not have Treeview, use tkinter.ttk
        from tkinter import ttk
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 14))
        style.configure("Treeview", font=("Arial", 12), rowheight=30)
        tree = ttk.Treeview(self, columns=columns, show='headings', style="Treeview")

        # Set appropriate column widths
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

        btn_add_course = tk.CTkButton(btn_frame, text="Add Courses", command=self.add_courses, font=("Arial", 16))
        btn_add_course.grid(row=0, column=0, padx=5)

        btn_logout = tk.CTkButton(btn_frame, text="Logout", command=self.logout, font=("Arial", 16))
        btn_logout.grid(row=0, column=1, padx=5)

    def show_all_enrollments(self):
        for widget in self.winfo_children():
            widget.destroy()

        label = tk.CTkLabel(self, text="All Student Enrollments", font=("Arial", 20))
        label.pack(pady=10)

        columns = (
            'student_id', 'first_name', 'last_name', 'course_id', 'course_name', 'credits', 'semester', 'year', 'grade')
        from tkinter import ttk
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 14))
        style.configure("Treeview", font=("Arial", 12), rowheight=30)
        tree = ttk.Treeview(self, columns=columns, show='headings', style="Treeview")

        # Set appropriate column widths
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

        label = tk.CTkLabel(self, text="Select Courses to Add (Maximum 3)", font=("Arial", 20))
        label.pack(pady=10)

        columns = ('course_id', 'course_name', 'credits', 'department_id', 'instructor_id')
        from tkinter import ttk
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 14))
        style.configure("Treeview", font=("Arial", 12), rowheight=30)
        tree = ttk.Treeview(self, columns=columns, show='headings', style="Treeview")

        # Set column widths
        tree.column('course_id', width=100, anchor='center')
        tree.column('course_name', width=250, anchor='w')
        tree.column('credits', width=80, anchor='center')
        tree.column('department_id', width=120, anchor='center')
        tree.column('instructor_id', width=120, anchor='center')

        for col in columns:
            tree.heading(col, text=col)

        # Show only courses that the student has not enrolled in
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

        label_select = tk.CTkLabel(self, text="Please enter the course_id(s) to add (separated by commas)", font=("Arial", 16))
        label_select.pack(pady=5)

        self.entry_courses = tk.CTkEntry(self, font=("Arial", 16))
        self.entry_courses.pack()

        btn_frame = tk.CTkFrame(self)
        btn_frame.pack(pady=10)

        btn_submit = tk.CTkButton(btn_frame, text="Submit", command=self.submit_courses, font=("Arial", 16))
        btn_submit.grid(row=0, column=0, padx=5)

        if self.user_role == 'Admin':
            btn_back = tk.CTkButton(btn_frame, text="Back", command=self.show_all_enrollments, font=("Arial", 16))
        else:
            btn_back = tk.CTkButton(btn_frame, text="Back", command=self.show_enrollments, font=("Arial", 16))
        btn_back.grid(row=0, column=1, padx=5)

    def submit_courses(self):
        courses_input = self.entry_courses.get()
        course_ids = courses_input.split(',')
        course_ids = [cid.strip() for cid in course_ids]

        if len(course_ids) > 3:
            messagebox.showerror("Error", "You can add a maximum of 3 courses")
            return

        # Check if the entered courses are available to add
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
            messagebox.showerror("Error",
                                 "The following courses cannot be added: {}".format(', '.join(invalid_courses)))
            return

        confirmation = messagebox.askokcancel("Confirm Course Addition", "Are you sure you want to submit these courses?")

        if confirmation:
            for course_id in course_ids:
                # Add enrollment data
                self.db_manager.cursor.execute('''
                    INSERT INTO Enrollments (student_id, course_id, semester, year, enrollment_date, grade)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (self.user_id, course_id, 1, date.today().year, date.today(), None))
            self.db_manager.conn.commit()

            messagebox.showinfo("Success", "Courses added successfully")
            if self.user_role == 'Admin':
                self.show_all_enrollments()
            else:
                self.show_enrollments()
        else:
            messagebox.showinfo("Cancelled", "Course addition has been cancelled")

    def manage_data(self):
        # Screen for managing data (Add, Delete, Update) Admin only
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

        btn_back = tk.CTkButton(self, text="Back", command=self.show_all_enrollments, font=("Arial", 16))
        btn_back.pack(pady=10)

    def add_data_screen(self):
        # Screen for adding data
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

        btn_back = tk.CTkButton(self, text="Back", command=self.manage_data, font=("Arial", 16))
        btn_back.pack(pady=5)

    def load_table_for_add(self):
        table_name = self.entry_table.get()
        columns = self.db_manager.show_table_columns(table_name)
        if not columns:
            return

        # Display table data
        for widget in self.winfo_children():
            if widget != self.entry_table and widget != self.entry_table.master:
                widget.destroy()

        label = tk.CTkLabel(self, text=f"Add Data to {table_name}", font=("Arial", 20))
        label.pack(pady=10)

        # Display table data
        from tkinter import ttk
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

        # Create fields for new data entry
        self.add_entries = {}
        frame_entries = tk.CTkFrame(self)
        frame_entries.pack(pady=10)
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

        btn_back = tk.CTkButton(btn_frame, text="Back", command=self.add_data_screen, font=("Arial", 16))
        btn_back.grid(row=0, column=1, padx=5)

    def add_data(self, table_name, columns):
        values = []
        for col in columns:
            value = self.add_entries[col].get()
            values.append(value)
        try:
            self.db_manager.insert_data(table_name, columns, values)
            self.add_data_screen()  # Return to main Add Data screen
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_data_screen(self):
        # Screen for updating data
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

        btn_back = tk.CTkButton(self, text="Back", command=self.manage_data, font=("Arial", 16))
        btn_back.pack(pady=5)

    def load_table_for_update(self):
        table_name = self.entry_table.get()
        columns = self.db_manager.show_table_columns(table_name)
        if not columns:
            return

        # Display table data
        for widget in self.winfo_children():
            if widget != self.entry_table and widget != self.entry_table.master:
                widget.destroy()

        label = tk.CTkLabel(self, text=f"Update Data in {table_name}", font=("Arial", 20))
        label.pack(pady=10)

        # Display table data
        from tkinter import ttk
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

        # Create fields for data to update
        self.update_entries = {}
        frame_entries = tk.CTkFrame(self)
        frame_entries.pack(pady=10)
        for idx, col in enumerate(columns):
            label_col = tk.CTkLabel(frame_entries, text=col, font=("Arial", 14))
            label_col.grid(row=0, column=idx, padx=5, pady=5)
            entry = tk.CTkEntry(frame_entries, font=("Arial", 14))
            entry.grid(row=1, column=idx, padx=5, pady=5)
            self.update_entries[col] = entry

        label_condition = tk.CTkLabel(self, text="Please specify the condition (e.g., student_id=6705177 AND course_id=10122):", font=("Arial", 16))
        label_condition.pack(pady=5)

        self.entry_condition = tk.CTkEntry(self, font=("Arial", 16))
        self.entry_condition.pack()

        btn_frame = tk.CTkFrame(self)
        btn_frame.pack(pady=10)

        btn_submit = tk.CTkButton(btn_frame, text="Update Data", command=lambda: self.update_data(table_name), font=("Arial", 16))
        btn_submit.grid(row=0, column=0, padx=5)

        btn_back = tk.CTkButton(btn_frame, text="Back", command=self.update_data_screen, font=("Arial", 16))
        btn_back.grid(row=0, column=1, padx=5)

    def update_data(self, table_name):
        updates = {}
        for col, entry in self.update_entries.items():
            value = entry.get()
            if value:
                updates[col] = value
        conditions_input = self.entry_condition.get()
        if not conditions_input:
            messagebox.showerror("Error", "Please specify the condition for updating data")
            return
        conditions = [cond.strip() for cond in conditions_input.split('AND')]
        try:
            self.db_manager.update_data(table_name, updates, conditions)
            self.update_data_screen()  # Return to main Update Data screen
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_data_screen(self):
        # Screen for deleting data
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

        btn_back = tk.CTkButton(self, text="Back", command=self.manage_data, font=("Arial", 16))
        btn_back.pack(pady=5)

    def load_table_for_delete(self):
        table_name = self.entry_table.get()
        columns = self.db_manager.show_table_columns(table_name)
        if not columns:
            return

        # Display table data
        for widget in self.winfo_children():
            if widget != self.entry_table and widget != self.entry_table.master:
                widget.destroy()

        label = tk.CTkLabel(self, text=f"Delete Data from {table_name}", font=("Arial", 20))
        label.pack(pady=10)

        # Display table data
        from tkinter import ttk
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

        label_condition = tk.CTkLabel(self, text="Condition (e.g., column=value):", font=("Arial", 16))
        label_condition.pack(pady=5)

        self.entry_condition = tk.CTkEntry(self, font=("Arial", 16))
        self.entry_condition.pack()

        btn_frame = tk.CTkFrame(self)
        btn_frame.pack(pady=10)

        btn_submit = tk.CTkButton(btn_frame, text="Delete Data", command=lambda: self.delete_data(table_name), font=("Arial", 16))
        btn_submit.grid(row=0, column=0, padx=5)

        btn_back = tk.CTkButton(btn_frame, text="Back", command=self.delete_data_screen, font=("Arial", 16))
        btn_back.grid(row=0, column=1, padx=5)

    def delete_data(self, table_name):
        condition = self.entry_condition.get()
        if not condition:
            messagebox.showerror("Error", "Please specify the condition for deleting data")
            return
        try:
            self.db_manager.delete_data(table_name, condition)
            self.delete_data_screen()  # Return to main Delete Data screen
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_closing(self):
        if self.db_manager:
            self.db_manager.close_connection()
        self.destroy()

# Create and run the application
if __name__ == "__main__":
    app = Application()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
