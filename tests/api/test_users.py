# tests/api/test_users.py

import pytest
from fastapi.testclient import TestClient
from main import app
from app.database.models.user import User
from app.database.database import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
from typing import List, Dict

# 테스트용 데이터베이스 설정 (test_auth.py와 동일하게 유지)
TEST_DATABASE_URL = "sqlite:///./test.db"
test_engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# 테스트용 의존성 오버라이드
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(name="db_session")
def db_session_fixture():
    # 픽스처가 실행될 때마다 모든 테이블을 생성하고 테스트 종료 후 삭제
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)

client = TestClient(app)

def test_get_user_info_success(db_session):
    # 테스트 사용자 생성 (username과 email 명시적으로 추가)
    test_user = User(
        nickname="testuser",
        email="test@example.com",
        username="testuser", # 🆕 username 필드 추가
        kakao_id="kakao_12345"
    )
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    response = client.get(f"/api/users/{test_user.id}")
    assert response.status_code == 200
    assert response.json()["nickname"] == "testuser"
    assert response.json()["username"] == "testuser"


def test_get_user_info_not_found(db_session): # 🆕 픽스처 추가
    response = client.get("/api/users/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "사용자를 찾을 수 없습니다."
