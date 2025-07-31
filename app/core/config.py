# app/core/config.py
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# =============================
# ✅ 데이터베이스 설정
# =============================
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "ddudda_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "ddudda_password")
DB_NAME = os.getenv("DB_NAME", "ddudda_db")
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# =============================
# ✅ 외부 API 키
# =============================
TASHU_API_KEY = os.getenv("TASHU_API_KEY", "")
DUROONUBI_API_KEY = os.getenv("DUROONUBI_API_KEY", "")
DAEJEON_BIKE_API_KEY = os.getenv("DAEJEON_BIKE_API_KEY", "")
API_KEY = os.getenv("API_KEY", "")
ENAPI_KEY = os.getenv("ENAPI_KEY", "")
AI_MODEL_SERVER_URL = os.getenv("AI_MODEL_SERVER_URL", "")

# =============================
# ✅ 카카오 로그인
# =============================
KAKAO_RESTAPI_KEY = os.getenv("KAKAO_REST_API_KEY", "")
KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI", "")
KAKAO_MAP_API_KEY = os.getenv("KAKAO_MAP_API_KEY", "")

# =============================
# ✅ JWT
# =============================
SECRET_KEY = os.getenv("SECRET_KEY", "secret")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24 * 7))
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# =============================
# ✅ 기타
# =============================
PORT = int(os.getenv("PORT", 8000))
ENV = os.getenv("ENV", "development")