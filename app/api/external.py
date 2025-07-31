# app/api/external.py
import logging
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.config.settings import TASHU_API_KEY, DUROONUBI_API_KEY, DAEJEON_BIKE_API_KEY
from app.api.utils import (
    APIException, NetworkException, AuthenticationException, DataFormatException,
    retry_on_failure, create_session_with_retry, validate_coordinates,
    standardize_station_data, standardize_bike_path_data, safe_get, calculate_distance
)

logger = logging.getLogger(__name__)

class TashuAPI:
    """타슈(대전 공공자전거) API 연동 클래스"""
    
    # 실제 타슈 API URL (추후 실제 URL로 교체 필요)
    BASE_URL = "https://api.tashu.or.kr/api"
    
    def __init__(self, api_key: str = TASHU_API_KEY):
        self.api_key = api_key
        self.session = create_session_with_retry()
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "DDUDDA-Backend/1.0"
        }
        logger.info(f"타슈 API 클라이언트 초기화 완료")
    
    @retry_on_failure(max_retries=3, delay=1.0)
    def get_stations(self) -> List[Dict[str, Any]]:
        """모든 대여소 정보 조회"""
        logger.info("타슈 대여소 정보 조회 시작")
        
        if not self.api_key:
            logger.error("타슈 API 키가 설정되지 않음")
            return self._get_dummy_stations()
        
        try:
            url = f"{self.BASE_URL}/stations"
            logger.debug(f"타슈 API 호출: {url}")
            
            response = self.session.get(url, headers=self.headers, timeout=10)
            
            # HTTP 상태 코드 체크
            if response.status_code == 401:
                raise AuthenticationException("타슈 API 인증 실패", response.status_code, "TASHU")
            elif response.status_code == 404:
                logger.warning("타슈 API 엔드포인트를 찾을 수 없음 - 더미 데이터 반환")
                return self._get_dummy_stations()
            elif not response.ok:
                raise APIException(f"타슈 API 오류: {response.status_code}", response.status_code, "TASHU")
            
            # 응답 데이터 파싱
            try:
                data = response.json()
            except ValueError as e:
                raise DataFormatException(f"타슈 API 응답 파싱 실패: {e}", api_name="TASHU")
            
            # 데이터 처리 및 표준화
            stations = self._process_stations_data(data)
            logger.info(f"타슈 대여소 {len(stations)}개 조회 완료")
            
            return stations
            
        except (AuthenticationException, DataFormatException, APIException):
            # 이 예외들은 다시 발생시켜서 상위에서 처리하도록 함
            raise
        except requests.RequestException as e:
            logger.error(f"타슈 API 네트워크 오류: {e}")
            if "Connection" in str(e) or "Timeout" in str(e):
                # 네트워크 오류 시 더미 데이터 반환
                logger.warning("네트워크 오류로 인해 타슈 더미 데이터 반환")
                return self._get_dummy_stations()
            raise NetworkException(f"타슈 API 네트워크 오류: {e}", api_name="TASHU")
        except Exception as e:
            logger.error(f"타슈 API 처리 중 예기치 않은 오류: {e}")
            return self._get_dummy_stations()
    
    @retry_on_failure(max_retries=3, delay=1.0)
    def get_station_status(self, station_id: str) -> Dict[str, Any]:
        """특정 대여소의 상태 조회"""
        logger.info(f"타슈 대여소 상태 조회: {station_id}")
        
        if not self.api_key:
            logger.error("타슈 API 키가 설정되지 않음")
            return self._get_dummy_station_status(station_id)
        
        try:
            url = f"{self.BASE_URL}/stations/{station_id}/status"
            logger.debug(f"타슈 상태 API 호출: {url}")
            
            response = self.session.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 401:
                raise AuthenticationException("타슈 API 인증 실패", response.status_code, "TASHU")
            elif response.status_code == 404:
                logger.warning(f"대여소 {station_id}를 찾을 수 없음")
                return self._get_dummy_station_status(station_id)
            elif not response.ok:
                raise APIException(f"타슈 상태 API 오류: {response.status_code}", response.status_code, "TASHU")
            
            data = response.json()
            status = self._process_station_status_data(data, station_id)
            logger.info(f"타슈 대여소 {station_id} 상태 조회 완료")
            
            return status
            
        except (AuthenticationException, DataFormatException, APIException):
            # 이 예외들은 다시 발생시켜서 상위에서 처리하도록 함
            raise
        except requests.RequestException as e:
            logger.error(f"타슈 상태 API 네트워크 오류: {e}")
            return self._get_dummy_station_status(station_id)
        except Exception as e:
            logger.error(f"타슈 상태 API 처리 중 오류: {e}")
            return self._get_dummy_station_status(station_id)
    
    def _process_stations_data(self, raw_data: Any) -> List[Dict[str, Any]]:
        """타슈 대여소 데이터 처리 및 표준화"""
        try:
            # API 응답 구조에 따라 데이터 추출
            stations_data = safe_get(raw_data, 'stations', default=raw_data)
            
            if not isinstance(stations_data, list):
                logger.warning("타슈 API 응답이 예상 형식이 아님")
                return []
            
            processed_stations = []
            
            for station_raw in stations_data:
                try:
                    # 기본 데이터 추출
                    station_id = safe_get(station_raw, 'id', 'station_id', default='')
                    name = safe_get(station_raw, 'name', 'station_name', default='')
                    address = safe_get(station_raw, 'address', 'addr', default='')
                    lat = safe_get(station_raw, 'latitude', 'lat', 'y', default=0.0)
                    lng = safe_get(station_raw, 'longitude', 'lng', 'lon', 'x', default=0.0)
                    available_bikes = safe_get(station_raw, 'available_bikes', 'bike_count', default=0)
                    total_docks = safe_get(station_raw, 'total_docks', 'dock_count', default=0)
                    
                    # 좌표 유효성 검사
                    if not validate_coordinates(lat, lng):
                        logger.warning(f"대여소 {station_id}의 좌표가 유효하지 않음: {lat}, {lng}")
                        continue
                    
                    # 표준화된 데이터 구조로 변환
                    standardized = standardize_station_data({
                        'station_id': station_id,
                        'name': name,
                        'address': address,
                        'lat': lat,
                        'lng': lng,
                        'available_bikes': int(available_bikes) if available_bikes else 0,
                        'total_docks': int(total_docks) if total_docks else 0,
                        'last_updated': datetime.now().isoformat()
                    })
                    
                    processed_stations.append(standardized)
                    
                except Exception as e:
                    logger.warning(f"대여소 데이터 처리 실패: {e}")
                    continue
            
            return processed_stations
            
        except Exception as e:
            logger.error(f"타슈 대여소 데이터 처리 실패: {e}")
            return []
    
    def _process_station_status_data(self, raw_data: Any, station_id: str) -> Dict[str, Any]:
        """타슈 대여소 상태 데이터 처리"""
        try:
            available_bikes = safe_get(raw_data, 'available_bikes', 'bike_count', default=0)
            total_docks = safe_get(raw_data, 'total_docks', 'dock_count', default=0)
            last_updated = safe_get(raw_data, 'last_updated', 'updated_at', default=datetime.now().isoformat())
            
            return {
                "station_id": station_id,
                "available_bikes": int(available_bikes) if available_bikes else 0,
                "total_docks": int(total_docks) if total_docks else 0,
                "available_docks": max(0, int(total_docks) - int(available_bikes)) if total_docks and available_bikes else 0,
                "last_updated": last_updated
            }
            
        except Exception as e:
            logger.error(f"타슈 상태 데이터 처리 실패: {e}")
            return self._get_dummy_station_status(station_id)
    
    def _get_dummy_stations(self) -> List[Dict[str, Any]]:
        """테스트용 더미 대여소 데이터"""
        logger.info("타슈 더미 데이터 반환")
        return [
            {
                "station_id": "ST001",
                "name": "대전역 앞",
                "address": "대전광역시 동구 정동 1-1",
                "lat": 36.332612,
                "lng": 127.434732,
                "available_bikes": 8,
                "total_docks": 15,
                "last_updated": datetime.now().isoformat()
            },
            {
                "station_id": "ST002",
                "name": "충남대학교 정문",
                "address": "대전광역시 유성구 대학로 99",
                "lat": 36.368762,
                "lng": 127.346390,
                "available_bikes": 3,
                "total_docks": 12,
                "last_updated": datetime.now().isoformat()
            },
            {
                "station_id": "ST003",
                "name": "유성온천역 2번 출구",
                "address": "대전광역시 유성구 봉명동 548-1",
                "lat": 36.356548,
                "lng": 127.334073,
                "available_bikes": 5,
                "total_docks": 10,
                "last_updated": datetime.now().isoformat()
            }
        ]
    
    def _get_dummy_station_status(self, station_id: str) -> Dict[str, Any]:
        """테스트용 더미 대여소 상태 데이터"""
        return {
            "station_id": station_id,
            "available_bikes": 5,
            "total_docks": 10,
            "available_docks": 5,
            "last_updated": datetime.now().isoformat()
        }


class DuroonubiAPI:
    """두루누비(자전거 도로 정보) API 연동 클래스"""
    
    BASE_URL = "https://api.duroonubi.kr/api"
    
    def __init__(self, api_key: str = DUROONUBI_API_KEY):
        self.api_key = api_key
        self.session = create_session_with_retry()
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "DDUDDA-Backend/1.0"
        }
        logger.info(f"두루누비 API 클라이언트 초기화 완료")
    
    @retry_on_failure(max_retries=3, delay=1.0)
    def get_bike_paths(self, lat: float, lng: float, radius: int = 2000) -> Dict[str, Any]:
        """특정 위치 주변의 자전거 도로 정보 조회"""
        logger.info(f"두루누비 자전거 도로 조회: lat={lat}, lng={lng}, radius={radius}")
        
        # 좌표 유효성 검사
        if not validate_coordinates(lat, lng):
            raise DataFormatException(f"잘못된 좌표: lat={lat}, lng={lng}", api_name="DUROONUBI")
        
        if not self.api_key:
            logger.error("두루누비 API 키가 설정되지 않음")
            return self._get_dummy_bike_paths()
        
        try:
            url = f"{self.BASE_URL}/bike-paths"
            params = {
                "lat": lat,
                "lng": lng,
                "radius": radius
            }
            
            logger.debug(f"두루누비 API 호출: {url}, params: {params}")
            
            response = self.session.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 401:
                raise AuthenticationException("두루누비 API 인증 실패", response.status_code, "DUROONUBI")
            elif response.status_code == 404:
                logger.warning("두루누비 API 엔드포인트를 찾을 수 없음 - 더미 데이터 반환")
                return self._get_dummy_bike_paths()
            elif not response.ok:
                raise APIException(f"두루누비 API 오류: {response.status_code}", response.status_code, "DUROONUBI")
            
            data = response.json()
            paths = self._process_bike_paths_data(data)
            logger.info(f"두루누비 자전거 도로 조회 완료")
            
            return paths
            
        except (AuthenticationException, DataFormatException, APIException):
            # 이 예외들은 다시 발생시켜서 상위에서 처리하도록 함
            raise
        except requests.RequestException as e:
            logger.error(f"두루누비 API 네트워크 오류: {e}")
            if "Connection" in str(e) or "Timeout" in str(e):
                return self._get_dummy_bike_paths()
            raise NetworkException(f"두루누비 API 네트워크 오류: {e}", api_name="DUROONUBI")
        except Exception as e:
            logger.error(f"두루누비 API 처리 중 오류: {e}")
            return self._get_dummy_bike_paths()
    
    def _process_bike_paths_data(self, raw_data: Any) -> Dict[str, Any]:
        """두루누비 자전거 도로 데이터 처리 및 표준화"""
        try:
            paths_data = safe_get(raw_data, 'bike_paths', 'paths', default=raw_data)
            
            if isinstance(paths_data, dict) and 'bike_paths' in paths_data:
                paths_data = paths_data['bike_paths']
            
            processed_paths = []
            
            if isinstance(paths_data, list):
                for path_raw in paths_data:
                    try:
                        standardized = standardize_bike_path_data(path_raw)
                        processed_paths.append(standardized)
                    except Exception as e:
                        logger.warning(f"자전거 도로 데이터 처리 실패: {e}")
                        continue
            
            return {"bike_paths": processed_paths}
            
        except Exception as e:
            logger.error(f"두루누비 자전거 도로 데이터 처리 실패: {e}")
            return {"bike_paths": []}
    
    def _get_dummy_bike_paths(self) -> Dict[str, Any]:
        """테스트용 더미 자전거 도로 데이터"""
        logger.info("두루누비 더미 데이터 반환")
        return {
            "bike_paths": [
                {
                    "path_id": "P001",
                    "name": "대전 중앙로 자전거도로",
                    "length": 5.2,
                    "path_type": "전용도로",
                    "coordinates": [
                        {"lat": 36.350971, "lng": 127.385288},
                        {"lat": 36.347563, "lng": 127.377091},
                        {"lat": 36.342285, "lng": 127.369709}
                    ]
                },
                {
                    "path_id": "P002",
                    "name": "유성구 자전거길",
                    "length": 3.8,
                    "path_type": "겸용도로",
                    "coordinates": [
                        {"lat": 36.362283, "lng": 127.356248},
                        {"lat": 36.368146, "lng": 127.352172},
                        {"lat": 36.374063, "lng": 127.346852}
                    ]
                }
            ]
        }


class DaejeonBikeAPI:
    """대전 자전거도로 정보 API 연동 클래스"""
    
    BASE_URL = "https://api.daejeon.go.kr/bicycle"
    
    def __init__(self, api_key: str = DAEJEON_BIKE_API_KEY):
        self.api_key = api_key
        self.session = create_session_with_retry()
        self.params = {
            "apiKey": self.api_key,
            "format": "json"
        }
        logger.info(f"대전 자전거 API 클라이언트 초기화 완료")
    
    @retry_on_failure(max_retries=3, delay=1.0)
    def get_bike_routes(self) -> Dict[str, Any]:
        """대전시 자전거 노선 정보 조회"""
        logger.info("대전 자전거 노선 정보 조회 시작")
        
        if not self.api_key:
            logger.error("대전 자전거 API 키가 설정되지 않음")
            return self._get_dummy_bike_routes()
        
        try:
            url = f"{self.BASE_URL}/routes"
            logger.debug(f"대전 자전거 API 호출: {url}")
            
            response = self.session.get(url, params=self.params, timeout=10)
            
            if response.status_code == 401:
                raise AuthenticationException("대전 자전거 API 인증 실패", response.status_code, "DAEJEON_BIKE")
            elif response.status_code == 404:
                logger.warning("대전 자전거 API 엔드포인트를 찾을 수 없음 - 더미 데이터 반환")
                return self._get_dummy_bike_routes()
            elif not response.ok:
                raise APIException(f"대전 자전거 API 오류: {response.status_code}", response.status_code, "DAEJEON_BIKE")
            
            data = response.json()
            routes = self._process_bike_routes_data(data)
            logger.info(f"대전 자전거 노선 조회 완료")
            
            return routes
            
        except (AuthenticationException, DataFormatException, APIException):
            # 이 예외들은 다시 발생시켜서 상위에서 처리하도록 함
            raise
        except requests.RequestException as e:
            logger.error(f"대전 자전거 API 네트워크 오류: {e}")
            if "Connection" in str(e) or "Timeout" in str(e):
                return self._get_dummy_bike_routes()
            raise NetworkException(f"대전 자전거 API 네트워크 오류: {e}", api_name="DAEJEON_BIKE")
        except Exception as e:
            logger.error(f"대전 자전거 API 처리 중 오류: {e}")
            return self._get_dummy_bike_routes()
    
    def _process_bike_routes_data(self, raw_data: Any) -> Dict[str, Any]:
        """대전 자전거 노선 데이터 처리 및 표준화"""
        try:
            routes_data = safe_get(raw_data, 'routes', 'data', default=raw_data)
            
            processed_routes = []
            
            if isinstance(routes_data, list):
                for route_raw in routes_data:
                    try:
                        route_id = safe_get(route_raw, 'route_id', 'id', default='')
                        name = safe_get(route_raw, 'name', 'route_name', default='')
                        length = safe_get(route_raw, 'length', 'distance', default=0.0)
                        difficulty = safe_get(route_raw, 'difficulty', 'level', default='')
                        description = safe_get(route_raw, 'description', 'desc', default='')
                        
                        standardized = {
                            "route_id": route_id,
                            "name": name,
                            "length": float(length) if length else 0.0,
                            "difficulty": difficulty,
                            "description": description
                        }
                        
                        processed_routes.append(standardized)
                        
                    except Exception as e:
                        logger.warning(f"자전거 노선 데이터 처리 실패: {e}")
                        continue
            
            return {"routes": processed_routes}
            
        except Exception as e:
            logger.error(f"대전 자전거 노선 데이터 처리 실패: {e}")
            return {"routes": []}
    
    def _get_dummy_bike_routes(self) -> Dict[str, Any]:
        """테스트용 더미 자전거 노선 데이터"""
        logger.info("대전 자전거 더미 데이터 반환")
        return {
            "routes": [
                {
                    "route_id": "R001",
                    "name": "갑천 자전거도로",
                    "length": 15.3,
                    "difficulty": "쉬움",
                    "description": "대전 시민들이 즐겨찾는 갑천변 자전거도로입니다."
                },
                {
                    "route_id": "R002",
                    "name": "대전 금강 자전거길",
                    "length": 21.5,
                    "difficulty": "중간",
                    "description": "금강변을 따라 조성된 자전거 전용도로입니다."
                },
                {
                    "route_id": "R003",
                    "name": "대청호 자전거길",
                    "length": 32.8,
                    "difficulty": "어려움",
                    "description": "대청호 주변을 일주하는 자전거 코스입니다."
                }
            ]
        } 