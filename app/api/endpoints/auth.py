# app/api/endpoints/auth.py
import os
import requests
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models.user import User
from app.common.utils.auth import create_access_token
from fastapi import Request

KAKAO_RESTAPI_KEY = os.getenv("KAKAO_REST_API_KEY")
KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI")

router = APIRouter()

@router.post("/auth/kakao")
async def kakao_login_code_exchange(request: Request, db: Session = Depends(get_db)):
    """
    카카오 인가 코드를 백엔드로 보내 사용자 인증을 처리하고 JWT 토큰을 발급합니다.
    """
    data = await request.json()
    code = data.get("code")
    redirect_uri = data.get("redirectUri")

    if not code or not redirect_uri:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="code or redirectUri missing")

    try:
        # 🔐 토큰 발급
        token_res = requests.post(
            "https://kauth.kakao.com/oauth/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "authorization_code",
                "client_id": KAKAO_RESTAPI_KEY,
                "redirect_uri": redirect_uri,
                "code": code,
            },
        )
        token_res.raise_for_status() # HTTP 오류가 발생하면 예외를 발생시킵니다.
        token_data = token_res.json()
        access_token = token_data.get("access_token")

        # 🙍 사용자 정보 조회
        user_res = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_res.raise_for_status() # HTTP 오류가 발생하면 예외를 발생시킵니다.
        user_info = user_res.json()
        
        kakao_id = str(user_info["id"])
        email = user_info.get("kakao_account", {}).get("email")
        nickname = user_info.get("properties", {}).get("nickname")

        # 📦 사용자 등록 or 조회
        # 데이터베이스에서 kakao_id를 기준으로 사용자를 찾습니다.
        user = db.query(User).filter(User.kakao_id == kakao_id).first()
        
        if not user:
            # 사용자가 없으면 새로 생성하여 추가합니다.
            user = User(
                kakao_id=kakao_id, 
                email=email, 
                nickname=nickname
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"새로운 사용자 등록: {user.nickname} (ID: {user.id})")
        else:
            print(f"기존 사용자 로그인: {user.nickname} (ID: {user.id})")

        # 🔐 JWT 발급
        jwt_token = create_access_token({"sub": str(user.id)})
        
        return JSONResponse({
            "access_token": jwt_token,
            "user": {
                "id": user.id, 
                "nickname": user.nickname,
                "email": user.email,
            }
        })
    
    except requests.exceptions.RequestException as e:
        print(f"카카오 API 호출 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, 
            detail=f"카카오 API 호출에 실패했습니다: {e}"
        )
    except Exception as e:
        print(f"예기치 않은 오류 발생: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버 오류가 발생했습니다."
        )

# /auth/callback 엔드포인트는 사용하지 않으므로 삭제하거나 주석 처리합니다.
# 클라이언트가 WebBrowser를 통해 직접 카카오 API와 통신하므로,
# 백엔드에서는 위 /auth/kakao 엔드포인트만으로 충분합니다.
"""
@router.get("/auth/callback")
async def kakao_callback(...):
    # ...
    # 이 엔드포인트는 더 이상 필요하지 않습니다.
    pass
"""