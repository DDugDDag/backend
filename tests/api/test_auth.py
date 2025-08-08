# tests/api/test_auth.py

import sys
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# 프로젝트 루트 경로를 sys.path에 추가하여 app 모듈을 찾도록 합니다.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app.database.database import Base, get_db
from app.main import app
from unittest.mock import patch, Mock
from typing import List, Dict

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

@patch('app.api.endpoints.auth.requests.post')
@patch('app.api.endpoints.auth.requests.get')
def test_kakao_login_success(mock_get, mock_post, db_session):
    """카카오 로그인 성공 테스트 (Mocking)"""
    # 카카오 토큰 발급 응답 모의
    mock_token_response = Mock()
    mock_token_response.status_code = 200
    mock_token_response.json.return_value = {"access_token": "dummy_access_token"}
    mock_token_response.raise_for_status.return_value = None
    mock_post.return_value = mock_token_response

    # 카카오 사용자 정보 응답 모의
    mock_user_response = Mock()
    mock_user_response.status_code = 200
    mock_user_response.json.return_value = {
        "id": 12345,
        "kakao_account": {"email": "test@kakao.com"},
        "properties": {"nickname": "테스트유저"}
    }
    mock_user_response.raise_for_status.return_value = None
    mock_get.return_value = mock_user_response

    client = TestClient(app)
    response = client.post(
        "/api/auth/kakao",
        json={"code": "dummy_code", "redirectUri": "dummy_uri"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["user"]["nickname"] == "테스트유저"
