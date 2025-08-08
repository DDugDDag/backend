# app/api/endpoints/users.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.database.models.user import User
from app.database.models.route import Route
from app.api.schemas.route_schema import UserResponse, RouteResponse, RouteRequest
import json

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get(
    "/{user_id}", 
    response_model=UserResponse,
    summary="사용자 정보 조회",
    description="""
    특정 `user_id`를 가진 사용자의 프로필 정보를 조회합니다.
    사용자 인증이 필요하며, 요청자와 조회 대상이 일치해야 합니다.
    """
)
def get_user(
    user_id: int, 
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    
    return user

@router.get(
    "/{user_id}/records",
    response_model=List[RouteResponse],
    summary="사용자 활동 기록 조회",
    description="""
    특정 `user_id`를 가진 사용자의 모든 자전거 여행 기록을 조회합니다.
    """
)
def get_user_records(
    user_id: int,
    db: Session = Depends(get_db)
):
    records = db.query(Route).filter(Route.user_id == user_id).all()
    
    # 데이터베이스 모델을 Pydantic 모델로 변환
    # route_data는 JSON 문자열로 저장되어 있으므로, json.loads로 변환 필요
    return [
        RouteResponse(
            route_id=str(record.id),
            summary={
                "distance": record.distance,
                "duration": record.duration,
                "elevation_gain": 0.0, # 데이터가 없으므로 0으로 설정
                "safety_score": 0.5, # 데이터가 없으므로 0.5로 설정
                "confidence_score": 0.0,
                "algorithm_version": "unknown",
                "bike_stations": 0
            },
            route_points=json.loads(record.route_data) if record.route_data else [],
            instructions=[],
            nearby_stations=[],
            metadata={}
        )
        for record in records
    ]


@router.post(
    "/{user_id}/records",
    status_code=status.HTTP_201_CREATED,
    summary="사용자 여행 기록 추가",
    description="""
    특정 `user_id`를 가진 사용자의 새로운 자전거 여행 기록을 추가합니다.
    """
)
def add_user_record(
    user_id: int,
    request: RouteRequest, # 경로 추천 API와 동일한 스키마 사용 가능
    db: Session = Depends(get_db)
):
    # TODO: 사용자 인증 로직 추가 (요청자와 user_id가 일치하는지 확인)
    
    # 새로운 경로 기록 생성
    new_route = Route(
        user_id=user_id,
        start_point="출발지", # TODO: 실제 장소명으로 변경
        end_point="목적지", # TODO: 실제 장소명으로 변경
        start_lat=request.start_lat,
        start_lng=request.start_lng,
        end_lat=request.end_lat,
        end_lng=request.end_lng,
        # TODO: 경로 데이터, 거리, 시간 등은 요청 본문에서 받아와야 함
        distance=0.0,
        duration=0,
        route_data="[]", # 임시로 빈 리스트 저장
    )
    db.add(new_route)
    db.commit()
    db.refresh(new_route)
    
    return {"message": f"여행 기록 {new_route.id}이(가) 추가되었습니다."}


@router.delete(
    "/{user_id}/records/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="사용자 여행 기록 삭제",
    description="""
    특정 `user_id`를 가진 사용자의 특정 여행 기록을 삭제합니다.
    """
)
def delete_user_record(
    user_id: int,
    record_id: int,
    db: Session = Depends(get_db)
):
    # TODO: 사용자 인증 로직 추가 (요청자와 user_id가 일치하는지 확인)
    
    record_to_delete = db.query(Route).filter(
        Route.user_id == user_id,
        Route.id == record_id
    ).first()
    
    if not record_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="기록을 찾을 수 없습니다."
        )
    
    db.delete(record_to_delete)
    db.commit()
    
    return
