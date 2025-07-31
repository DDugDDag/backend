# app/database/models/route.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.database.database import Base

class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    start_point = Column(String(255))
    end_point = Column(String(255))
    start_lat = Column(Float)
    start_lng = Column(Float)
    end_lat = Column(Float)
    end_lng = Column(Float)
    distance = Column(Float)
    duration = Column(Integer)
    route_data = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
