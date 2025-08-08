# app/api/schemas/support_schema.py

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class InquiryRequest(BaseModel):
    """사용자 문의/건의사항 제출 요청 모델"""
    user_id: int = Field(..., description="문의를 제출한 사용자의 ID")
    inquiry_type: str = Field(..., description="문의 유형 (예: '버그', '기능 제안', '일반 문의')")
    content: str = Field(..., description="문의 내용")

class InquiryResponse(BaseModel):
    """문의사항 제출 응답 모델"""
    inquiry_id: int = Field(..., description="생성된 문의사항의 고유 ID")
    user_id: int = Field(..., description="문의를 제출한 사용자의 ID")
    inquiry_type: str = Field(..., description="문의 유형")
    content: str = Field(..., description="문의 내용")
    status: str = Field(..., description="문의 처리 상태")
    created_at: datetime = Field(..., description="문의 접수 시간")