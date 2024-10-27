import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import mysql.connector
from datetime import date

def connect_to_db_admin():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="sesar123",
        database="education_sector"
    )

def connect_to_db_student():
    return mysql.connector.connect(
        host="localhost",
        user="student",
        password="1234",
        database="education_sector"
    )

# เชื่อมต่อกับฐานข้อมูล MySQL
conn = connect_to_db_student()
cursor = conn.cursor()

# ฟังก์ชันสำหรับตรวจสอบรหัสนักศึกษาและรหัสผ่าน
def login():
    student_id = entry_id.get()
    student_password = entry_password.get()

    query = "SELECT * FROM Students WHERE student_id=%s AND student_password=%s"
    cursor.execute(query, (student_id, student_password))
    result = cursor.fetchone()

    if result:
        messagebox.showinfo("เข้าสู่ระบบสำเร็จ", "ยินดีต้อนรับคุณ {} {}".format(result[1], result[2]))
        show_enrollments(student_id)
    else:
        messagebox.showerror("ข้อผิดพลาด", "รหัสนักศึกษาหรือรหัสผ่านของคุณไม่ถูกต้อง")


# ฟังก์ชันสำหรับแสดงข้อมูลการลงทะเบียน
def show_enrollments(student_id):
    for widget in root.winfo_children():
        widget.destroy()

    label = tk.Label(root, text="ข้อมูลการลงทะเบียนของคุณ", font=("Arial", 16))
    label.pack(pady=10)

    columns = (
    'student_id', 'first_name', 'last_name', 'course_id', 'course_name', 'credits', 'semester', 'year', 'grade')
    tree = ttk.Treeview(root, columns=columns, show='headings')

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
    cursor.execute(query, (student_id,))
    results = cursor.fetchall()

    for row in results:
        tree.insert('', tk.END, values=row)

    tree.pack(fill=tk.BOTH, expand=True)

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=10)

    btn_add_course = tk.Button(btn_frame, text="Add รายวิชา", command=lambda: add_courses(student_id))
    btn_add_course.grid(row=0, column=0, padx=5)

    btn_clear = tk.Button(btn_frame, text="Clear", command=clear_screen)
    btn_clear.grid(row=0, column=1, padx=5)


# ฟังก์ชันสำหรับล้างหน้าจอ
def clear_screen():
    for widget in root.winfo_children():
        widget.destroy()
    main_screen()


# ฟังก์ชันสำหรับเพิ่มรายวิชา
def add_courses(student_id):
    for widget in root.winfo_children():
        widget.destroy()

    label = tk.Label(root, text="เลือกวิชาที่ต้องการเพิ่ม (สูงสุด 3 วิชา)", font=("Arial", 16))
    label.pack(pady=10)

    columns = ('course_id', 'course_name', 'credits', 'department_id', 'instructor_id')
    tree = ttk.Treeview(root, columns=columns, show='headings')

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
    cursor.execute(query, (student_id,))
    results = cursor.fetchall()

    for row in results:
        tree.insert('', tk.END, values=row)

    tree.pack(fill=tk.BOTH, expand=True)

    label_select = tk.Label(root, text="กรุณาใส่ course_id ที่ต้องการเพิ่ม (คั่นด้วยเครื่องหมายจุลภาค)")
    label_select.pack(pady=5)

    entry_courses = tk.Entry(root)
    entry_courses.pack()

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=10)

    btn_submit = tk.Button(btn_frame, text="Submit", command=lambda: submit_courses(student_id, entry_courses.get()))
    btn_submit.grid(row=0, column=0, padx=5)

    btn_back = tk.Button(btn_frame, text="ย้อนกลับ", command=lambda: show_enrollments(student_id))
    btn_back.grid(row=0, column=1, padx=5)


# ฟังก์ชันสำหรับยืนยันการเพิ่มรายวิชา
def submit_courses(student_id, courses_input):
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
    cursor.execute(query, (student_id,))
    available_courses = [str(row[0]) for row in cursor.fetchall()]

    invalid_courses = [cid for cid in course_ids if cid not in available_courses]

    if invalid_courses:
        messagebox.showerror("ข้อผิดพลาด", "รายวิชาต่อไปนี้ไม่สามารถเพิ่มได้: {}".format(', '.join(invalid_courses)))
        return

    confirmation = messagebox.askokcancel("ยืนยันการเพิ่มรายวิชา", "คุณแน่ใจหรือไม่ที่จะ Submit รายวิชานี้")

    if confirmation:
        for course_id in course_ids:
            # เพิ่มข้อมูลการลงทะเบียน
            cursor.execute('''
                INSERT INTO Enrollments (student_id, course_id, semester, year, enrollment_date, grade)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (student_id, course_id, 1, date.today().year, date.today(), None))
        conn.commit()

        messagebox.showinfo("สำเร็จ", "เพิ่มรายวิชาเรียบร้อยแล้ว")
        show_enrollments(student_id)
    else:
        messagebox.showinfo("ยกเลิก", "การเพิ่มรายวิชาถูกยกเลิก")


# ฟังก์ชันสำหรับหน้าจอหลัก
def main_screen():
    label_title = tk.Label(root, text="ระบบลงทะเบียนนักศึกษา", font=("Arial", 20))
    label_title.pack(pady=20)

    frame = tk.Frame(root)
    frame.pack(pady=10)

    label_id = tk.Label(frame, text="รหัสนักศึกษา")
    label_id.grid(row=0, column=0, padx=5, pady=5)

    global entry_id
    entry_id = tk.Entry(frame)
    entry_id.grid(row=0, column=1, padx=5, pady=5)

    label_password = tk.Label(frame, text="รหัสผ่าน")
    label_password.grid(row=1, column=0, padx=5, pady=5)

    global entry_password
    entry_password = tk.Entry(frame, show='*')
    entry_password.grid(row=1, column=1, padx=5, pady=5)

    btn_login = tk.Button(root, text="เข้าสู่ระบบ", command=login)
    btn_login.pack(pady=10)


# สร้างหน้าต่างหลัก
root = tk.Tk()
root.title("Student Enrollment System")

# กำหนดขนาดหน้าต่างเป็น 800x500
root.geometry("800x500")

main_screen()

root.mainloop()

# ปิดการเชื่อมต่อกับฐานข้อมูล
cursor.close()
conn.close()
