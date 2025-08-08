# app/common/utils/auth.py
import os
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException, status, Header

SECRET_KEY = os.getenv("SECRET_KEY", "your_secret")
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=60)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# 🆕 JWT 토큰에서 사용자 ID를 추출하는 함수
def get_current_user_id(authorization: str = Header(...)) -> int:
    """
    HTTP Header의 Authorization 필드에서 JWT 토큰을 추출하고 유효성을 검증하여
    로그인한 사용자의 ID를 반환합니다.
    """
    token_prefix, token = authorization.split(' ')
    if token_prefix.lower() != 'bearer':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="잘못된 인증 형식입니다. 'Bearer <token>' 형식을 사용해주세요."
        )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="토큰에 유효한 사용자 ID가 없습니다."
            )
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 유효하지 않습니다."
        )
