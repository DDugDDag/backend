# backend\app\database\models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

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
    distance = Column(Float)  # 킬로미터
    duration = Column(Integer)  # 분
    route_data = Column(Text)  # JSON 형식의 경로 데이터
    created_at = Column(DateTime, server_default=func.now())

class BikeStation(Base):
    __tablename__ = "bike_stations"
    
    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(String(50), unique=True, index=True)
    name = Column(String(100))
    address = Column(String(255))
    lat = Column(Float)
    lng = Column(Float)
    available_bikes = Column(Integer)
    last_updated = Column(DateTime) 