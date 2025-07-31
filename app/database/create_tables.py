# backend\app\database\create_tables.py
from app.database.database import engine
from app.database.models import Base

def create_tables():
    """데이터베이스 테이블 생성 함수"""
    try:
        # 모든 모델의 테이블 생성
        Base.metadata.create_all(bind=engine)
        print("데이터베이스 테이블이 성공적으로 생성되었습니다.")
        return True
    except Exception as e:
        print(f"테이블 생성 중 오류 발생: {str(e)}")
        return False

if __name__ == "__main__":
    create_tables() 