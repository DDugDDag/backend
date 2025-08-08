# tests/api/test_auth.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.database import Base, get_db
from app.main import app
import os
import sys

# 프로젝트 루트 경로를 sys.path에 추가 (conftest.py가 올바르게 작동하지 않을 경우를 대비)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# 테스트용 데이터베이스 설정
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
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)

def test_kakao_login_success(db_session):
    # TODO: 카카오 API를 Mocking하여 테스트해야 합니다.
    # 이 코드는 더미 응답을 가정합니다.
    client = TestClient(app)
    response = client.post(
        "/api/auth/kakao",
        json={"code": "dummy_code", "redirectUri": "dummy_uri"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "user" in response.json()
