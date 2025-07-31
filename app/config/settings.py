# backend\app\config\settings.py
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 데이터베이스 설정
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "ddudda_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "ddudda_password")
DB_NAME = os.getenv("DB_NAME", "ddudda_db")

# API 키 설정
TASHU_API_KEY = os.getenv("TASHU_API_KEY", "")
DUROONUBI_API_KEY = os.getenv("DUROONUBI_API_KEY", "")
DAEJEON_BIKE_API_KEY = os.getenv("DAEJEON_BIKE_API_KEY", "")

# 서버 설정
PORT = int(os.getenv("PORT", 8080))
ENV = os.getenv("ENV", "development")

# 데이터베이스 URL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}" 
KAKAO_RESTAPI_KEY = os.getenv("KAKAO_RESTAPI_KEY", "")