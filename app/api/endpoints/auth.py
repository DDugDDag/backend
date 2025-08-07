# app/api/endpoints/auth.py
import os
import requests
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models.user import User
from app.common.utils.auth import create_access_token
from fastapi import Request

KAKAO_RESTAPI_KEY = os.getenv("KAKAO_RESTAPI_KEY")
KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI")

router = APIRouter()

@router.post("/auth/kakao")
async def kakao_login_code_exchange(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    code = data.get("code")
    redirect_uri = data.get("redirectUri")

    if not code or not redirect_uri:
        raise HTTPException(status_code=400, detail="code or redirectUri missing")

    # 🔐 토큰 발급
    token_res = requests.post(
        "https://kauth.kakao.com/oauth/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "authorization_code",
            "client_id": KAKAO_RESTAPI_KEY,
            "redirect_uri": redirect_uri,  # ← 프론트에서 전달된 값을 사용해야 함!
            "code": code,
        },
    )

    token_data = token_res.json()
    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="카카오 access_token 발급 실패")

    # 🙍 사용자 정보 조회
    user_res = requests.get(
        "https://kapi.kakao.com/v2/user/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    user_info = user_res.json()

    kakao_id = str(user_info["id"])
    email = user_info["kakao_account"].get("email")
    nickname = user_info["properties"].get("nickname")

    # 📦 사용자 등록 or 조회
    user = db.query(User).filter(User.kakao_id == kakao_id).first()
    if not user:
        user = User(kakao_id=kakao_id, email=email, nickname=nickname)
        db.add(user)
        db.commit()
        db.refresh(user)

    # 🔐 JWT 발급
    jwt_token = create_access_token({"sub": str(user.id)})
    return JSONResponse({
        "access_token": jwt_token,
        "user": {"id": user.id, "nickname": user.nickname}
    })

@router.get("/auth/callback")
async def kakao_callback(code: str, db: Session = Depends(get_db)):
    token_res = requests.post(
        "https://kauth.kakao.com/oauth/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "authorization_code",
            "client_id": KAKAO_RESTAPI_KEY,
            "redirect_uri": KAKAO_REDIRECT_URI,
            "code": code,
        },
    )
    access_token = token_res.json().get("access_token")

    user_res = requests.get(
        "https://kapi.kakao.com/v2/user/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    user_info = user_res.json()
    kakao_id = str(user_info["id"])
    email = user_info["kakao_account"].get("email")
    nickname = user_info["properties"].get("nickname")

    user = db.query(User).filter(User.kakao_id == kakao_id).first()
    if not user:
        user = User(kakao_id=kakao_id, email=email, nickname=nickname)
        db.add(user)
        db.commit()
        db.refresh(user)

    jwt_token = create_access_token({"sub": str(user.id)})
    return JSONResponse({
        "access_token": jwt_token,
        "user": {"id": user.id, "nickname": user.nickname}
    })