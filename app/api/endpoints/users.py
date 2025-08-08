# app/api/endpoints/users.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
# 🆕 List를 사용하기 위해 typing 모듈에서 가져옵니다.
from typing import List, Optional

from app.database.database import get_db
from app.database.models.user import User
from app.database.models.route import Route
from app.api.schemas.route_schema import UserResponse, RouteResponse, RouteRequest, UserUpdate
from app.common.utils.auth import get_current_user_id
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


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="사용자 정보 수정",
    description="""
    로그인한 사용자의 프로필 정보를 수정합니다. JWT 토큰으로 인증된 사용자의 정보만 수정할 수 있습니다.
    """
)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    # JWT 토큰으로 현재 로그인한 사용자 ID를 가져옵니다.
    current_user_id: int = Depends(get_current_user_id)
):
    # 현재 로그인한 사용자와 수정하려는 사용자가 동일한지 확인합니다.
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인의 정보만 수정할 수 있습니다."
        )

    user_to_update = db.query(User).filter(User.id == user_id).first()
    
    if not user_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )

    if user_update.nickname:
        user_to_update.nickname = user_update.nickname

    db.commit()
    db.refresh(user_to_update)
    
    return user_to_update


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
    
    return [
        RouteResponse(
            route_id=str(record.id),
            summary={
                "distance": record.distance,
                "duration": record.duration,
                "elevation_gain": 0.0,
                "safety_score": 0.5,
                "confidence_score": 0.9,
                "algorithm_version": "v1.0",
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
    request: RouteRequest,
    db: Session = Depends(get_db)
):
    new_route = Route(
        user_id=user_id,
        start_point="출발지",
        end_point="목적지",
        start_lat=request.start_lat,
        start_lng=request.start_lng,
        end_lat=request.end_lng,
        end_lng=request.end_lng,
        distance=0.0,
        duration=0,
        route_data="[]",
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
