# app/api/endpoints/tashu.py

from fastapi import APIRouter, HTTPException
from app.api.utils import AuthenticationException, NetworkException, DataFormatException, APIException

router = APIRouter()

@router.get("/bike-stations")
def get_bike_stations():
    """
    모든 따릉이 자전거 스테이션의 정보를 가져옵니다.
    """
    from app.services.external.external_api import TashuAPI
    tashu_api = TashuAPI()
    try:
        return tashu_api.get_stations()
    except (AuthenticationException, NetworkException, DataFormatException, APIException) as e:
        # 적절한 HTTP 상태 코드로 에러를 처리합니다.
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bike-stations/{station_id}")
def get_bike_station_status(station_id: str):
    """
    특정 자전거 스테이션의 상태 정보를 가져옵니다.
    """
    from app.services.external.external_api import TashuAPI
    tashu_api = TashuAPI()
    try:
        return tashu_api.get_station_status(station_id)
    except (AuthenticationException, NetworkException, DataFormatException, APIException) as e:
        raise HTTPException(status_code=500, detail=str(e))
