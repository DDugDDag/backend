# app/database/create_tables.py
from app.database.database import engine
from app.database.models import Base

def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ 데이터베이스 테이블 생성 완료")
        return True
    except Exception as e:
        print(f"❌ 테이블 생성 실패: {e}")  
        return False

if __name__ == "__main__":
    create_tables()
