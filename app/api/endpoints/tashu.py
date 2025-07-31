# app/api/endpoints/tashu.py
from fastapi import APIRouter, HTTPException
from app.services.external.external_api import TashuAPI
from app.api.utils import AuthenticationException, NetworkException, DataFormatException, APIException

router = APIRouter()
tashu_api = TashuAPI()

@router.get("/bike-stations")
def get_bike_stations():
    return tashu_api.get_stations()

@router.get("/bike-stations/{station_id}")
def get_bike_station_status(station_id: str):
    return tashu_api.get_station_status(station_id)