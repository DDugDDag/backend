# app/database/models/inquiry.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database.database import Base

class Inquiry(Base):
    """
    사용자 문의/건의사항을 위한 데이터베이스 모델
    """
    __tablename__ = "inquiries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))  # 사용자 테이블과 외래 키로 연결
    inquiry_type = Column(String(50))
    content = Column(String(1000))
    status = Column(String(50), default="접수 완료")  # 문의 처리 상태 (예: "접수 완료", "처리 중", "답변 완료")
    created_at = Column(DateTime, server_default=func.now())
