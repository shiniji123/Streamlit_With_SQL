import streamlit as st
import mysql.connector
import pandas as pd

# ฟังก์ชันสำหรับเชื่อมต่อกับ MySQL
def create_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="sesar123",
        database="education_sector"
    )
    return conn

# ฟังก์ชันสำหรับดึงข้อมูลจาก MySQL
def fetch_data(query):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    return result

# ฟังก์ชันสำหรับแสดงข้อมูลในตาราง
def show_data(data, title):
    df = pd.DataFrame(data)
    st.subheader(title)
    st.write(df)

# Layout ของหน้าเว็บ
st.title("Student Enrollment System")

# เมนูเลือกการแสดงข้อมูล
menu = ["Students", "Departments", "Instructors", "Courses", "Enrollments"]
choice = st.sidebar.selectbox("Select Table", menu)

# การแสดงข้อมูลตามที่เลือก
if choice == "Students":
    data = fetch_data("SELECT * FROM Students")
    show_data(data, "Students Table")

elif choice == "Departments":
    data = fetch_data("SELECT * FROM Departments")
    show_data(data, "Departments Table")

elif choice == "Instructors":
    data = fetch_data("SELECT * FROM Instructors")
    show_data(data, "Instructors Table")

elif choice == "Courses":
    data = fetch_data("SELECT * FROM Courses")
    show_data(data, "Courses Table")

elif choice == "Enrollments":
    data = fetch_data("SELECT * FROM Enrollments")
    show_data(data, "Enrollments Table")
