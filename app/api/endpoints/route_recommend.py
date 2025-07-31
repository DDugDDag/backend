# app/api/endpoints/route_recommend.py
import logging
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.api.schemas.route_schema import RouteRequest, RouteResponse
from app.api.utils import APIException, NetworkException, AuthenticationException, DataFormatException
from app.services.route.route_finder import RouteFinder
from app.services.external.external_api import TashuAPI, DuroonubiAPI, DaejeonBikeAPI
from app.database.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()
route_finder = RouteFinder()
tashu_api = TashuAPI()
duroonubi_api = DuroonubiAPI()
daejeon_bike_api = DaejeonBikeAPI()

@router.get("/bike-paths")
def get_bike_paths(lat: float, lng: float, radius: int = 2000):
    """
    특정 위치 주변의 자전거 도로 정보를 조회하는 API
    """
    logger.info(f"자전거 도로 조회 요청: lat={lat}, lng={lng}, radius={radius}")
    
    try:
        # 입력 검증
        if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            raise HTTPException(status_code=400, detail="잘못된 좌표 값입니다.")
        
        if radius <= 0 or radius > 10000:
            raise HTTPException(status_code=400, detail="반경은 1m ~ 10km 사이여야 합니다.")
        
        # 두루누비 API를 사용하여 자전거 도로 정보 조회
        paths = duroonubi_api.get_bike_paths(lat, lng, radius)
        logger.info("자전거 도로 조회 완료")
        return paths
        
    except DataFormatException as e:
        logger.error(f"좌표 검증 실패: {e}")
        raise HTTPException(status_code=400, detail="좌표 형식이 올바르지 않습니다.")
    except AuthenticationException as e:
        logger.error(f"두루누비 API 인증 실패: {e}")
        raise HTTPException(status_code=401, detail="두루누비 API 인증에 실패했습니다.")
    except NetworkException as e:
        logger.error(f"두루누비 API 네트워크 오류: {e}")
        raise HTTPException(status_code=503, detail="두루누비 API 서버에 연결할 수 없습니다.")
    except APIException as e:
        logger.error(f"두루누비 API 오류: {e}")
        raise HTTPException(status_code=502, detail=f"두루누비 API 오류: {e.message}")
    except Exception as e:
        logger.error(f"자전거 도로 조회 중 예기치 않은 오류: {e}")
        raise HTTPException(status_code=500, detail="자전거 도로 정보 조회 중 오류가 발생했습니다.")



@router.post("/find-path", response_model=RouteResponse)
def find_path(request: RouteRequest):
    """
    출발지와 목적지 사이의 자전거 경로를 찾는 API
    """
    logger.info(f"경로 찾기 요청: {request.start_lat}, {request.start_lng} -> {request.end_lat}, {request.end_lng}")
    
    try:
        # 경로 찾기 객체를 사용하여 경로 계산
        result = route_finder.find_path(
            start_lat=request.start_lat,
            start_lng=request.start_lng,
            end_lat=request.end_lat,
            end_lng=request.end_lng
        )
        
        logger.info("경로 찾기 완료")
        return result
        
    except Exception as e:
        logger.error(f"경로 찾기 실패: {e}")
        raise HTTPException(status_code=500, detail=f"경로 찾기 중 오류가 발생했습니다: {str(e)}")


@router.get("/bike-routes")
def get_bike_routes():
    """
    대전시 자전거 노선 정보를 조회하는 API
    """
    logger.info("대전 자전거 노선 조회 요청")
    
    try:
        # 대전 자전거 API를 사용하여 노선 정보 조회
        routes = daejeon_bike_api.get_bike_routes()
        logger.info("대전 자전거 노선 조회 완료")
        return routes
        
    except AuthenticationException as e:
        logger.error(f"대전 자전거 API 인증 실패: {e}")
        raise HTTPException(status_code=401, detail="대전 자전거 API 인증에 실패했습니다.")
    except NetworkException as e:
        logger.error(f"대전 자전거 API 네트워크 오류: {e}")
        raise HTTPException(status_code=503, detail="대전 자전거 API 서버에 연결할 수 없습니다.")
    except APIException as e:
        logger.error(f"대전 자전거 API 오류: {e}")
        raise HTTPException(status_code=502, detail=f"대전 자전거 API 오류: {e.message}")
    except Exception as e:
        logger.error(f"대전 자전거 노선 조회 중 예기치 않은 오류: {e}")
        raise HTTPException(status_code=500, detail="자전거 노선 정보 조회 중 오류가 발생했습니다.")
