import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import mysql.connector
from datetime import date

def connect_to_db_admin():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="scma348",
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

    label = tk.Label(root, text="ข้อมูลการลงทะเบียนของคุณ")
    label.pack()

    columns = ('student_id', 'first_name', 'last_name', 'course_id', 'course_name', 'credits', 'semester', 'year', 'grade')
    tree = ttk.Treeview(root, columns=columns, show='headings')

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

    tree.pack()

    btn_add_course = tk.Button(root, text="Add รายวิชา", command=lambda: add_courses(student_id))
    btn_add_course.pack()

    btn_clear = tk.Button(root, text="Clear", command=clear_screen)
    btn_clear.pack()

# ฟังก์ชันสำหรับล้างหน้าจอ
def clear_screen():
    for widget in root.winfo_children():
        widget.destroy()
    main_screen()

# ฟังก์ชันสำหรับเพิ่มรายวิชา
def add_courses(student_id):
    for widget in root.winfo_children():
        widget.destroy()

    label = tk.Label(root, text="เลือกวิชาที่ต้องการเพิ่ม (สูงสุด 3 วิชา)")
    label.pack()

    columns = ('course_id', 'course_name', 'credits', 'department_id', 'instructor_id')
    tree = ttk.Treeview(root, columns=columns, show='headings')

    for col in columns:
        tree.heading(col, text=col)

    # แก้ไขส่วนนี้เพื่อเลือกเฉพาะรายวิชาที่นักศึกษายังไม่ได้ลงทะเบียน
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

    tree.pack()

    label_select = tk.Label(root, text="กรุณาใส่ course_id ที่ต้องการเพิ่ม (คั่นด้วยเครื่องหมายจุลภาค)")
    label_select.pack()

    entry_courses = tk.Entry(root)
    entry_courses.pack()

    btn_submit = tk.Button(root, text="Submit", command=lambda: submit_courses(student_id, entry_courses.get()))
    btn_submit.pack()

    btn_back = tk.Button(root, text="ย้อนกลับ", command=lambda: show_enrollments(student_id))
    btn_back.pack()


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
    label_id = tk.Label(root, text="รหัสนักศึกษา")
    label_id.pack()

    global entry_id
    entry_id = tk.Entry(root)
    entry_id.pack()

    label_password = tk.Label(root, text="รหัสผ่าน")
    label_password.pack()

    global entry_password
    entry_password = tk.Entry(root, show='*')
    entry_password.pack()

    btn_login = tk.Button(root, text="เข้าสู่ระบบ", command=login)
    btn_login.pack()

# สร้างหน้าต่างหลัก
root = tk.Tk()
root.title("Student Enrollment System")

main_screen()

root.mainloop()

# ปิดการเชื่อมต่อกับฐานข้อมูล
cursor.close()
conn.close()
