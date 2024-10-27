import mysql.connector
import tkinter as tk
from tkinter import messagebox

# Create a connection to the database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="sesar123",
    database="education_sector"
)

# Check if the connection was successful
if conn.is_connected():
    print("Connected to MySQL database")
cursor = conn.cursor()


def get_enrollment_info(student_id, student_password):
    conn = mysql.connector.connect(
        host="localhost",  # แก้ไขตาม host ของคุณ
        user="root",  # แก้ไขตาม user ของคุณ
        password="sesar123",
        database="education_sector"  # แก้ไขตามชื่อฐานข้อมูลของคุณ
    )

    cursor = conn.cursor(dictionary=True)

    cursor.execute('''
        SELECT student_id, first_name, last_name
        FROM Students
        WHERE student_id = %s AND student_password = %s
    ''', (student_id, student_password))

    student = cursor.fetchone()

    if student:
        cursor.execute('''
            SELECT e.student_id, s.first_name, s.last_name, c.course_id, c.course_name, c.credits, e.semester, e.year, e.grade
            FROM Enrollments e
            JOIN Students s ON e.student_id = s.student_id
            JOIN Courses c ON e.course_id = c.course_id
            WHERE e.student_id = %s
        ''', (student_id,))

        enrollments = cursor.fetchall()

        if enrollments:
            result_text = f"ข้อมูลการลงทะเบียนของ {student['first_name']} {student['last_name']} (Student ID: {student_id})\n"
            result_text += f"{'Course ID':<10}{'Course Name':<25}{'Credits':<10}{'Semester':<10}{'Year':<6}{'Grade':<5}\n"
            result_text += "-" * 70 + "\n"
            for enrollment in enrollments:
                result_text += f"{enrollment['course_id']:<10}{enrollment['course_name']:<25}{enrollment['credits']:<10}{enrollment['semester']:<10}{enrollment['year']:<6}{enrollment['grade'] or 'N/A':<5}\n"
            result_label.config(text=result_text)
        else:
            result_label.config(text="ไม่พบข้อมูลการลงทะเบียน")
    else:
        messagebox.showerror("Error", "รหัสนักศึกษาหรือรหัสผ่านของคุณไม่ถูกต้อง")

    cursor.close()
    conn.close()


def submit():
    student_id = student_id_entry.get()
    student_password = student_password_entry.get()
    get_enrollment_info(student_id, student_password)


# สร้างหน้าต่างหลัก
root = tk.Tk()
root.title("Student Enrollment Info")

# สร้าง Label และ Entry สำหรับ student_id
tk.Label(root, text="Student ID:").grid(row=0, column=0)
student_id_entry = tk.Entry(root)
student_id_entry.grid(row=0, column=1)

# สร้าง Label และ Entry สำหรับ student_password
tk.Label(root, text="Student Password:").grid(row=1, column=0)
student_password_entry = tk.Entry(root, show='*')  # ใช้ show='*' เพื่อซ่อนรหัสผ่าน
student_password_entry.grid(row=1, column=1)

# สร้างปุ่มสำหรับการ submit
submit_button = tk.Button(root, text="Submit", command=submit)
submit_button.grid(row=2, column=1)

# สร้าง Label สำหรับแสดงผลลัพธ์
result_label = tk.Label(root, text="", justify="left", anchor="w")
result_label.grid(row=3, column=0, columnspan=2)

# เริ่มต้น GUI
root.mainloop()
