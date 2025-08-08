# tests/api/test_users.py

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.models.user import User

client = TestClient(app)

def test_get_user_info_success(db_session):
    # 테스트 사용자 생성
    test_user = User(
        nickname="testuser",
        email="test@example.com",
        kakao_id="kakao_12345"
    )
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    response = client.get(f"/api/users/{test_user.id}")
    assert response.status_code == 200
    assert response.json()["nickname"] == "testuser"

def test_get_user_info_not_found():
    response = client.get("/api/users/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "사용자를 찾을 수 없습니다."
