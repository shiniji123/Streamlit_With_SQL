import mysql.connector

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
    # สร้างการเชื่อมต่อกับ MySQL
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="sesar123",
        database="education_sector"  # แก้ไขตามชื่อฐานข้อมูลของคุณ
    )

    cursor = conn.cursor(dictionary=True)

    # ตรวจสอบว่ามี student_id และ student_password ตรงกับที่ในฐานข้อมูลหรือไม่
    cursor.execute('''
        SELECT student_id, first_name, last_name
        FROM Students
        WHERE student_id = %s AND student_password = %s
    ''', (student_id, student_password))

    student = cursor.fetchone()

    if student:
        # ถ้าข้อมูลถูกต้อง ดึงข้อมูล Enrollments
        cursor.execute('''
            SELECT e.student_id, s.first_name, s.last_name, c.course_id, c.course_name, c.credits, e.semester, e.year, e.grade
            FROM Enrollments e
            JOIN Students s ON e.student_id = s.student_id
            JOIN Courses c ON e.course_id = c.course_id
            WHERE e.student_id = %s
        ''', (student_id,))

        enrollments = cursor.fetchall()

        if enrollments:
            # แสดงผลข้อมูลการลงทะเบียน
            print(f"ข้อมูลการลงทะเบียนเรียนของ {student['first_name']} {student['last_name']} (Student ID: {student_id})")
            print(f"{'Course ID':<10}{'Course Name':<25}{'Credits':<10}{'Semester':<10}{'Year':<6}{'Grade':<5}")
            print("-" * 70)
            for enrollment in enrollments:
                print(
                    f"{enrollment['course_id']:<10}{enrollment['course_name']:<25}{enrollment['credits']:<10}{enrollment['semester']:<10}{enrollment['year']:<6}{enrollment['grade'] or 'N/A':<5}")
        else:
            print("ไม่พบข้อมูลการลงทะเบียน")
    else:
        # ถ้าข้อมูลไม่ถูกต้อง
        print("รหัสนักศึกษาหรือรหัสผ่านของคุณไม่ถูกต้อง")

    # ปิดการเชื่อมต่อ
    cursor.close()
    conn.close()


# เริ่มต้นโปรแกรม
if __name__ == "__main__":
    student_id = input("กรุณากรอก Student ID: ")
    student_password = input("กรุณากรอก Student Password: ")

    get_enrollment_info(student_id, student_password)
