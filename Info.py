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

#=====================================================================================
# DROP BEFORE RUN
List_table = ["Enrollments", "Courses", "Instructors", "Departments", "Students"]
for table in List_table:
    # Check if the table exists
    cursor.execute(f"SHOW TABLES LIKE '{table}'")
    result = cursor.fetchone()  # Fetch the result

    if result:
        # Table exists, so drop it
        print(f'DROPPING TABLE {table}')
        cursor.execute(f'DROP TABLE {table};')
    else:
        # Table does not exist
        print(f'TABLE {table} does not exist')

#===================================================================================
cursor.execute('''
    CREATE TABLE Students (
        student_id INT PRIMARY KEY,        
        first_name VARCHAR(50) NOT NULL,   
        last_name VARCHAR(50) NOT NULL,                
        email VARCHAR(100) NOT NULL UNIQUE,   
        contact_number VARCHAR(15),          
        address VARCHAR(200),                         
        enrollment_date DATE NOT NULL,
        student_password VARCHAR(20)
    );
''')

# Create table: Departments
cursor.execute('''
    CREATE TABLE Departments (
        department_id INT AUTO_INCREMENT PRIMARY KEY,    
        department_name VARCHAR(100) NOT NULL
    );
''')

# Create table: Instructors
cursor.execute('''
    CREATE TABLE Instructors (
        instructor_id INT AUTO_INCREMENT PRIMARY KEY,   
        first_name VARCHAR(50) NOT NULL,      
        last_name VARCHAR(50) NOT NULL,      
        department_id INT NOT NULL,           
        email VARCHAR(100) NOT NULL UNIQUE,   
        contact_number VARCHAR(15),        
        FOREIGN KEY (department_id) REFERENCES Departments(department_id) ON DELETE CASCADE
    );
''')

# Create table: Courses
cursor.execute('''
    CREATE TABLE Courses (
        course_id INT PRIMARY KEY,       
        course_name VARCHAR(100) NOT NULL,   
        credits INT NOT NULL,                
        department_id INT NOT NULL,          
        instructor_id INT NOT NULL,          
        FOREIGN KEY (department_id) REFERENCES Departments(department_id) ON DELETE CASCADE,
        FOREIGN KEY (instructor_id) REFERENCES Instructors(instructor_id) ON DELETE CASCADE
    );
''')

# Create table: Enrollments
cursor.execute('''
    CREATE TABLE Enrollments (
        enrollment_id INT AUTO_INCREMENT PRIMARY KEY,    
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

# Insert data statements can remain the same as before.


#================================================================================

cursor.execute(''' INSERT INTO Students (student_id, first_name, last_name, email, contact_number, address, enrollment_date, student_password)
    VALUES
    (6705177,'Somchai', 'Suksan', 'somchai.s@email.com', '088-1234-567', '123 Phahonyothin Road Bangkok', '2024-09-01', '1'),
    (6705225,'Suda', 'Chaiyo', 'suda.c@email.com', '088-5678-910', '456 Sukhumvit Road Bangkok', '2024-09-01', 'vZ5uP7xE'),
    (6705413,'Nattapong', 'Jindarat', 'nattapong.j@email.com', '088-2345-678', '789 Phetkasem Road Bangkok', '2024-09-02', '9xF1tS3b'),
    (6705332,'Siriporn', 'Pimpa', 'siriporn.p@email.com', '088-8765-432', '321 Ladprao Road Bangkok', '2024-09-02', 'H6zR2mKq'),
    (6705213,'Ratchanee', 'Srisuk', 'ratchanee.s@email.com', '088-4321-876', '654 Ngamwongwan Road Bangkok', '2024-09-03', 'cU8rT4aW'),
    (6705441,'Narong', 'Thongchai', 'narong.t@email.com', '088-5670-345', '987 Ratchapruek Road Bangkok', '2024-09-03', 'Y9sQ3dV2'),
    (6705234,'Supaporn', 'Wattanakorn', 'supaporn.w@email.com', '088-1239-876', '159 Ratchadapisek Road Bangkok', '2024-09-04', 'nM5wP0kL'),
    (6705141,'Prasert', 'Sriwong', 'prasert.s@email.com', '088-6789-123', '357 Rama 9 Road Bangkok', '2024-09-04', '3Fv7xJ6h'),
    (6705500,'Ornchuma', 'Thitikul', 'ornchuma.t@email.com', '088-9876-543', '753 Sathorn Road Bangkok', '2024-09-05', 'zT1eP4aM'),
    (6705101,'Kasem', 'Jarernchai', 'kasem.j@email.com', '088-3456-789', '951 Prachachuen Road Bangkok', '2024-09-05', 'qN8rC5wX'),
    (6705003,'Anan', 'Wongyai', 'anan.w@email.com', '088-7890-432', '246 On Nut Road Bangkok', '2024-09-06', 'K7mV3y2R'),
    (6705061,'Supansa', 'Rattanaporn', 'supansa.r@email.com', '088-5671-098', '357 Rama 4 Road Bangkok', '2024-09-06', 'uT4sZ6xB'),
    (6705118,'Wichai', 'Phutthichai', 'wichai.p@email.com', '088-6543-210', '951 Charoen Krung Road Bangkok', '2024-09-07', 'pN1qY9fC'),
    (6705198,'Natcha', 'Maneerat', 'natcha.m@email.com', '088-3210-654', '753 Vibhavadi Road Bangkok', '2024-09-07', '8WzX2tL0'),
    (6705217,'Korn', 'Thammasak', 'korn.t@email.com', '088-8764-321', '852 Charansanitwong Road Bangkok', '2024-09-08', 'hV5pT7nR');
    ''')

cursor.execute('''INSERT INTO Departments (department_id,department_name)
    VALUES
    (101,'Computer Science'),
    (102,'Mathematics'),
    (103,'Physics'),
    (104,'Chemistry'),
    (105,'Biology');
    ''')

cursor.execute('''INSERT INTO Instructors (instructor_id,first_name, last_name, department_id, email, contact_number)
    VALUES
    (542018,'Tanakrit', 'Phromwong', 101, 'tanakrit.p@email.com', '089-1234-567'),
    (547382,'Kanya', 'Srisai', 102, 'kanya.s@email.com', '089-5678-910'),
    (540386,'Wirot', 'Chareonrat', 103, 'wirot.c@email.com', '089-2345-678'),
    (541965,'Sukanya', 'Sangthong', 104, 'sukanya.s@email.com', '089-8765-432'),
    (546430,'Kritsada', 'Sukam', 105, 'kritsada.s@email.com', '089-4321-876');
    ''')
cursor.execute('''INSERT INTO Courses (course_id, course_name, credits, department_id, instructor_id)
    VALUES
    (10122,'Database', 3 , 101 , 542018),
    (10215,'Math Analysis', 3 , 102 , 547382),
    (10388,'Thermodynamic', 2 , 103 , 540386),
    (10438,'General Chemistry', 2 , 104 , 541965),
    (10512,'Biology', 2 , 105, 546430);
    ''')
cursor.execute('''INSERT INTO Enrollments (student_id, course_id, semester, year, enrollment_date, grade)
    VALUES
    (6705177, 10122, 1, 2024, '2024-09-01',NULL),
    (6705225, 10438, 1, 2024, '2024-09-01',NULL),
    (6705413, 10215, 1, 2024, '2024-09-02',NULL),
    (6705332, 10122, 1, 2024, '2024-09-02',NULL),
    (6705213, 10388, 1, 2024, '2024-09-03',NULL),
    (6705441, 10512, 1, 2024, '2024-09-03',NULL),
    (6705234, 10438, 1, 2024, '2024-09-04',NULL),
    (6705141, 10388, 1, 2024, '2024-09-04',NULL),
    (6705500, 10215, 1, 2024, '2024-09-05',NULL),
    (6705101, 10512, 1, 2024, '2024-09-05',NULL),
    (6705003, 10215, 1, 2024, '2024-09-06',NULL),
    (6705061, 10122, 1, 2024, '2024-09-06',NULL),
    (6705118, 10388, 1, 2024, '2024-09-07',NULL),
    (6705198, 10215, 1, 2024, '2024-09-07',NULL),
    (6705217, 10512, 1, 2024, '2024-09-08',NULL);
    ''')

#===================================================================================

conn.commit()

#========================================================================

# Close the cursor and connection
cursor.close()
conn.close()



