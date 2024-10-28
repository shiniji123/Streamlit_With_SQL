import streamlit as st
import psycopg2
import os
from dotenv import load_dotenv

# โหลด Environment Variables จากไฟล์ .env
load_dotenv()

# ตั้งค่า Connection URL จาก Supabase
DATABASE_URL = os.getenv("DATABASE_URL")

# ฟังก์ชันการเชื่อมต่อกับฐานข้อมูล
def create_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        return conn
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return None

# ฟังก์ชันการสร้างตารางในฐานข้อมูล
def create_tables():
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        # สร้างตาราง Students
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Students (
                student_id SERIAL PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                contact_number VARCHAR(15),
                address VARCHAR(200),
                enrollment_date DATE NOT NULL,
                student_password VARCHAR(20)
            );
        ''')

        # สร้างตาราง Departments
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Departments (
                department_id SERIAL PRIMARY KEY,
                department_name VARCHAR(100) NOT NULL
            );
        ''')

        # สร้างตาราง Instructors
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Instructors (
                instructor_id SERIAL PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                department_id INT NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                contact_number VARCHAR(15),
                FOREIGN KEY (department_id) REFERENCES Departments(department_id) ON DELETE CASCADE
            );
        ''')

        # สร้างตาราง Courses
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Courses (
                course_id SERIAL PRIMARY KEY,
                course_name VARCHAR(100) NOT NULL,
                credits INT NOT NULL,
                department_id INT NOT NULL,
                instructor_id INT NOT NULL,
                FOREIGN KEY (department_id) REFERENCES Departments(department_id) ON DELETE CASCADE,
                FOREIGN KEY (instructor_id) REFERENCES Instructors(instructor_id) ON DELETE CASCADE
            );
        ''')

        # สร้างตาราง Enrollments
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Enrollments (
                enrollment_id SERIAL PRIMARY KEY,
                student_id INT NOT NULL,
                course_id INT NOT NULL,
                semester VARCHAR(10) NOT NULL,
                year INT NOT NULL,
                grade VARCHAR(2),
                enrollment_date DATE NOT NULL,
                FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE,
                FOREIGN KEY (course_id) REFERENCES Courses(course_id) ON DELETE CASCADE
            );
        ''')

        conn.commit()
        cursor.close()
        conn.close()
        st.success("Tables created successfully!")

# ฟังก์ชันการเพิ่มข้อมูล
def insert_data():
    conn = create_connection()
    if conn:
        cursor = conn.cursor()

        # เพิ่มข้อมูลในตาราง Students
        students_data = [
            (6705177, 'Somchai', 'Suksan', 'somchai.s@email.com', '088-1234-567', '123 Phahonyothin Road Bangkok', '2024-09-01', '1'),
            (6705225, 'Suda', 'Chaiyo', 'suda.c@email.com', '088-5678-910', '456 Sukhumvit Road Bangkok', '2024-09-01', 'vZ5uP7xE'),
            (6705413, 'Nattapong', 'Jindarat', 'nattapong.j@email.com', '088-2345-678', '789 Phetkasem Road Bangkok', '2024-09-02', '9xF1tS3b')
        ]
        cursor.executemany('''
            INSERT INTO Students (student_id, first_name, last_name, email, contact_number, address, enrollment_date, student_password)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (email) DO NOTHING;
        ''', students_data)

        conn.commit()
        cursor.close()
        conn.close()
        st.success("Data inserted successfully!")

# ฟังก์ชันการแสดงข้อมูล
def show_data(table_name):
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data

# ส่วนของอินเตอร์เฟซเว็บ Streamlit
st.title("Student Enrollment System using Supabase")

if st.button("Create Tables"):
    create_tables()

if st.button("Insert Data"):
    insert_data()

# เลือกตารางที่จะแสดงข้อมูล
table = st.selectbox("Select Table", ["Students", "Departments", "Instructors", "Courses", "Enrollments"])

if st.button("Show Data"):
    data = show_data(table)
    if data:
        st.write(data)
    else:
        st.write(f"No data found in {table} table.")
