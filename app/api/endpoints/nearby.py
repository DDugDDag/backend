# app/api/endpoints/nearby.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any

from app.services.external.external_api import PublicDataAPI
from app.common.utils.validators import validate_coordinates
from app.common.utils.exceptions import DataFormatException, NetworkException, APIException

router = APIRouter(
    prefix="/nearby",
    tags=["Location"]
)

def get_public_data_api() -> PublicDataAPI:
    return PublicDataAPI()

@router.get(
    "/places",
    summary="위치 기반 추천 장소 조회",
    description="""
    현재 위치를 기반으로 주변 추천 장소를 조회합니다.
    """
)
async def get_nearby_places(
    lat: float, 
    lng: float, 
    radius: int = 1000,
    api_client: PublicDataAPI = Depends(get_public_data_api)
):
    try:
        if not validate_coordinates(lat, lng):
            raise DataFormatException("유효하지 않은 좌표입니다.")
        
        places = await api_client.get_nearby_places(lat, lng, radius)
        
        return {
            "places": places
        }
    except DataFormatException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except (NetworkException, APIException) as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="서버 오류가 발생했습니다.")
