# app/api/endpoints/route_recommend.py

import logging
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.api.schemas.route_schema import RouteRequest, RouteResponse
from app.common.utils.exceptions import APIException, NetworkException, AuthenticationException, DataFormatException
# 서비스 레이어의 클래스들을 직접 import
from app.services.route.route_service import RouteService
from app.services.external.external_api import TashuAPI, DuroonubiAPI, DaejeonBikeAPI
from app.database.database import get_db
# RouteService가 필요로 하는 클래스들을 import
from app.services.ai.ai_integration import AIRouteOptimizer
from app.route_engine import RouteCalculator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/routes", tags=["Routes"])

# 모든 서비스 의존성을 관리하는 팩토리 함수를 정의합니다.
# 이 함수는 FastAPI의 Depends()를 통해 의존성 주입에 사용됩니다.
def get_route_service() -> RouteService:
    """
    RouteService 인스턴스를 생성하고 의존성을 주입합니다.
    """
    tashu_api = TashuAPI()
    ai_optimizer = AIRouteOptimizer()
    route_calculator = RouteCalculator()
    return RouteService(tashu_api, ai_optimizer, route_calculator)

# 기존에 최상단에서 인스턴스화하던 부분을 모두 삭제하고
# 의존성 주입을 통해 받도록 변경합니다.

@router.get("/bike-paths", 
    summary="주변 자전거 도로 정보 조회",
    description="""
    특정 위치(위도, 경도)를 기준으로 주변 반경(radius) 내의 자전거 도로 정보를 조회합니다.
    - `lat`, `lng`: 조회할 중심 좌표
    - `radius`: 검색 반경 (단위: 미터). 기본값은 2000m입니다.
    """,
    responses={
        200: {"description": "성공적으로 자전거 도로 정보를 조회했습니다."},
        400: {"description": "요청 파라미터가 잘못되었습니다."},
        401: {"description": "API 키 인증에 실패했습니다."},
        500: {"description": "서버 내부 오류가 발생했습니다."},
        503: {"description": "외부 API 서버에 연결할 수 없습니다."}
    }
)
def get_bike_paths(
    lat: float, lng: float, radius: int = 2000,
    duroonubi_api: DuroonubiAPI = Depends()  # DuroonubiAPI를 의존성 주입
):
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


@router.post("/find-path", response_model=RouteResponse,
            summary="AI 기반 자전거 경로 추천",
            description="출발지와 목적지, 그리고 사용자 선호도를 바탕으로 최적의 자전거 경로를 추천합니다.",
            responses={
                200: {"description": "성공적으로 경로를 찾았습니다."},
                400: {"description": "요청 파라미터가 잘못되었습니다."},
                401: {"description": "API 키 인증에 실패했습니다."},
                500: {"description": "서버 내부 오류가 발생했습니다."},
                503: {"description": "외부 API 서버에 연결할 수 없습니다."}
            }
)
async def find_path(
    request: RouteRequest,
    route_service: RouteService = Depends(get_route_service)
):
    """
    출발지와 목적지 사이의 자전거 경로를 찾는 API
    """
    logger.info(f"경로 찾기 요청: {request.start_lat}, {request.start_lng} -> {request.end_lat}, {request.end_lng}")
    
    try:
        # RouteService의 비동기 메서드를 사용하여 경로 계산
        # 이전에 동기 함수였던 find_path를 find_path_async로 변경했다고 가정합니다.
        result = await route_service.find_path_async(
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


@router.get("/bike-routes",
            summary="대전시 자전거 노선 정보 조회",
            description="""
            대전시 자전거 노선 정보를 조회하는 API
            """,
            responses={
                200: {"description": "성공적으로 자전거 노선 정보를 조회했습니다."},
                401: {"description": "API 키 인증에 실패했습니다."},
                500: {"description": "서버 내부 오류가 발생했습니다."},
                503: {"description": "외부 API 서버에 연결할 수 없습니다."}
            }
)
def get_bike_routes(
    daejeon_bike_api: DaejeonBikeAPI = Depends() # DaejeonBikeAPI를 의존성 주입
):
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
