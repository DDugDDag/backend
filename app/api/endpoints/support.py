# app/api/endpoints/support.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models.inquiry import Inquiry
from app.api.schemas.support_schema import InquiryRequest, InquiryResponse

router = APIRouter(
    prefix="/support",
    tags=["Support"]
)

@router.post(
    "/inquiry",
    status_code=status.HTTP_201_CREATED,
    response_model=InquiryResponse,
    summary="사용자 문의/건의사항 제출",
    description="""
    사용자의 문의사항이나 건의사항을 제출하고 저장합니다.
    """
)
def submit_inquiry(
    request: InquiryRequest,
    db: Session = Depends(get_db)
):
    """
    Args:
        request (InquiryRequest): 문의 내용을 담은 요청 본문
        db (Session): 데이터베이스 세션
    
    Returns:
        InquiryResponse: 저장된 문의 정보
    """
    # 데이터베이스에 문의사항 저장
    new_inquiry = Inquiry(
        user_id=request.user_id,
        inquiry_type=request.inquiry_type,
        content=request.content
    )
    db.add(new_inquiry)
    db.commit()
    db.refresh(new_inquiry)
    
    # 저장된 문의 정보를 Pydantic 모델로 변환하여 반환
    return InquiryResponse(
        inquiry_id=new_inquiry.id,
        user_id=new_inquiry.user_id,
        inquiry_type=new_inquiry.inquiry_type,
        content=new_inquiry.content,
        status=new_inquiry.status,
        created_at=new_inquiry.created_at
    )
