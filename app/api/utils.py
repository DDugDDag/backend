# backend\app\api\utils.py
import logging
import time
from typing import Optional, Dict, Any
from functools import wraps
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

class APIException(Exception):
    """API 관련 예외 클래스"""
    def __init__(self, message: str, status_code: Optional[int] = None, api_name: str = ""):
        self.message = message
        self.status_code = status_code
        self.api_name = api_name
        super().__init__(self.message)

class NetworkException(APIException):
    """네트워크 관련 예외"""
    pass

class AuthenticationException(APIException):
    """인증 관련 예외"""
    pass

class DataFormatException(APIException):
    """데이터 형식 관련 예외"""
    pass

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """API 호출 실패 시 재시도하는 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (requests.RequestException, APIException) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt)  # 지수적 백오프
                        logger.warning(f"API 호출 실패 (시도 {attempt + 1}/{max_retries}): {e}. {wait_time}초 후 재시도...")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"모든 재시도 실패: {e}")
                        
            raise last_exception
        return wrapper
    return decorator

def create_session_with_retry() -> requests.Session:
    """재시도 로직이 포함된 requests 세션 생성"""
    session = requests.Session()
    
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"],
        backoff_factor=1
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

def validate_coordinates(lat: float, lng: float) -> bool:
    """좌표 유효성 검사"""
    if not isinstance(lat, (int, float)) or not isinstance(lng, (int, float)):
        return False
    
    # 위도는 -90 ~ 90, 경도는 -180 ~ 180
    if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
        return False
        
    return True

def normalize_coordinates(lat: float, lng: float) -> tuple:
    """좌표 정규화 (소수점 6자리까지)"""
    return round(float(lat), 6), round(float(lng), 6)

def safe_get(data: dict, *keys, default=None):
    """안전한 딕셔너리 키 접근 - 여러 키를 시도하여 첫 번째로 찾은 값 반환"""
    if not isinstance(data, dict):
        return default
        
    for key in keys:
        try:
            if key in data and data[key] is not None:
                return data[key]
        except (TypeError, KeyError):
            continue
    return default

def validate_api_response(response_data: Any, required_fields: list) -> bool:
    """API 응답 데이터 유효성 검사"""
    if not isinstance(response_data, dict):
        return False
        
    for field in required_fields:
        if field not in response_data:
            return False
            
    return True

def standardize_station_data(raw_data: dict) -> dict:
    """대여소 데이터 표준화"""
    try:
        # 좌표 정규화
        lat = safe_get(raw_data, 'lat', default=0.0)
        lng = safe_get(raw_data, 'lng', default=0.0)
        
        if not validate_coordinates(lat, lng):
            raise DataFormatException(f"잘못된 좌표 데이터: lat={lat}, lng={lng}")
            
        lat, lng = normalize_coordinates(lat, lng)
        
        # 표준 형식으로 변환
        standardized = {
            "station_id": safe_get(raw_data, 'station_id', default=''),
            "name": safe_get(raw_data, 'name', default=''),
            "address": safe_get(raw_data, 'address', default=''),
            "lat": lat,
            "lng": lng,
            "available_bikes": safe_get(raw_data, 'available_bikes', default=0),
            "total_docks": safe_get(raw_data, 'total_docks', default=0),
            "last_updated": safe_get(raw_data, 'last_updated', default='')
        }
        
        return standardized
        
    except Exception as e:
        logger.error(f"대여소 데이터 표준화 실패: {e}")
        raise DataFormatException(f"대여소 데이터 표준화 실패: {e}")

def standardize_bike_path_data(raw_data: dict) -> dict:
    """자전거 도로 데이터 표준화"""
    try:
        # 좌표 배열 정규화
        coordinates = safe_get(raw_data, 'coordinates', default=[])
        normalized_coords = []
        
        for coord in coordinates:
            lat = safe_get(coord, 'lat', default=0.0)
            lng = safe_get(coord, 'lng', default=0.0)
            
            if validate_coordinates(lat, lng):
                lat, lng = normalize_coordinates(lat, lng)
                normalized_coords.append({"lat": lat, "lng": lng})
        
        standardized = {
            "path_id": safe_get(raw_data, 'path_id', default=''),
            "name": safe_get(raw_data, 'name', default=''),
            "length": safe_get(raw_data, 'length', default=0.0),
            "path_type": safe_get(raw_data, 'path_type', default=''),
            "coordinates": normalized_coords
        }
        
        return standardized
        
    except Exception as e:
        logger.error(f"자전거 도로 데이터 표준화 실패: {e}")
        raise DataFormatException(f"자전거 도로 데이터 표준화 실패: {e}")

def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """두 좌표 간의 거리 계산 (Haversine 공식)"""
    import math
    
    # 지구 반지름 (km)
    R = 6371.0
    
    # 라디안으로 변환
    lat1_rad = math.radians(lat1)
    lng1_rad = math.radians(lng1)
    lat2_rad = math.radians(lat2)
    lng2_rad = math.radians(lng2)
    
    # 차이 계산
    dlat = lat2_rad - lat1_rad
    dlng = lng2_rad - lng1_rad
    
    # Haversine 공식
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c 