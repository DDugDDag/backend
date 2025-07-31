# backend\app\main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router
from app.database.database import test_db_connection
from app.config.settings import PORT, KAKAO_RESTAPI_KEY

import requests
# from django.shortcuts import render, get_object_or_404


def kakao_rest_api(longitude, latitude):
    url = 'https://dapi.kakao.com/v2/local/geo/coord2regioncode.json'
    headers = {'Authorization': f'KakaoAK {KAKAO_RESTAPI_KEY}'}
    params = {'x': longitude, 'y': latitude}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        # 에러 메시지를 dict로 반환
        return {"error": response.text, "status_code": response.status_code}

# FastAPI 애플리케이션 생성
app = FastAPI(
    title="뚜따 백엔드 API",
    description="대전 자전거 경로 추천 시스템 백엔드 API",
    version="0.1.0"
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 오리진만 허용하도록 변경 필요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(api_router)

@app.get("/")
def root():
    return kakao_rest_api("37.559624", "126.825676")
    # """루트 경로"""
    # return {
    #     "message": "Welcome to DDUDDA BACKEND DYAYAYAAY",
    #     "documentation": "/docs",
    # }

@app.get("/db-connection")
def check_db_connection():
    """데이터베이스 연결 상태 확인"""
    success, message = test_db_connection()
    return {"success": success, "message": message}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=PORT, reload=True)