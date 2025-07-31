# app/database/models/station.py
from sqlalchemy import Column, Integer, String, Float, DateTime
from app.database.database import Base

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
