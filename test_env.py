from dotenv import load_dotenv
import os

# โหลดค่า Environment Variables จากไฟล์ .env
load_dotenv()

# เข้าถึงค่าจากตัวแปรใน .env
DATABASE_URL = os.getenv("DATABASE_URL")

print(f"Database URL: {DATABASE_URL}")