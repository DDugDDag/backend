# app/api/endpoints/users.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/{user_id}")
def get_user(user_id: int):
    return {"message": f"사용자 {user_id} 정보"}

@router.get("/{user_id}/records")
def get_user_records(user_id: int):
    return {"message": f"사용자 {user_id}의 기록"}