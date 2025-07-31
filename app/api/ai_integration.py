# app/api/ai_integration.py
import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from app.api.utils import calculate_distance, validate_coordinates, DataFormatException
from app.api.external import TashuAPI, DuroonubiAPI

logger = logging.getLogger(__name__)

class AIRouteRequest:
    """AI 모델 요청 데이터 구조"""
    
    def __init__(self, start_lat: float, start_lng: float, end_lat: float, end_lng: float, 
                 preferences: Optional[Dict[str, Any]] = None):
        self.start_lat = start_lat
        self.start_lng = start_lng
        self.end_lat = end_lat
        self.end_lng = end_lng
        self.preferences = preferences or {}
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """AI 모델 요청을 위한 딕셔너리로 변환"""
        return {
            "start_location": {
                "latitude": self.start_lat,
                "longitude": self.start_lng
            },
            "end_location": {
                "latitude": self.end_lat,
                "longitude": self.end_lng
            },
            "preferences": self.preferences,
            "timestamp": self.timestamp
        }

class AIRouteResponse:
    """AI 모델 응답 데이터 구조"""
    
    def __init__(self, route_data: Dict[str, Any]):
        self.route_data = route_data
        self.process_time = route_data.get('process_time', 0)
        self.confidence_score = route_data.get('confidence_score', 0.0)
        self.algorithm_version = route_data.get('algorithm_version', '1.0')
    
    @property
    def coordinates(self) -> List[Dict[str, float]]:
        """경로 좌표 리스트"""
        return self.route_data.get('coordinates', [])
    
    @property
    def total_distance(self) -> float:
        """총 거리 (km)"""
        return self.route_data.get('total_distance', 0.0)
    
    @property
    def estimated_duration(self) -> int:
        """예상 소요 시간 (분)"""
        return self.route_data.get('estimated_duration', 0)
    
    @property
    def elevation_gain(self) -> float:
        """고도 상승 (m)"""
        return self.route_data.get('elevation_gain', 0.0)
    
    @property
    def safety_score(self) -> float:
        """안전도 점수 (0-1)"""
        return self.route_data.get('safety_score', 0.5)

class AIRouteOptimizer:
    """AI 기반 경로 최적화 클래스"""
    
    def __init__(self):
        self.tashu_api = TashuAPI()
        self.duroonubi_api = DuroonubiAPI()
        self.model_url = "http://localhost:5000/api/route"  # AI 모델 서버 URL (추후 설정)
        self.fallback_enabled = True
        logger.info("AI 경로 최적화 모듈 초기화 완료")
    
    async def find_optimal_route(self, request: AIRouteRequest) -> AIRouteResponse:
        """AI 모델을 사용하여 최적 경로 찾기"""
        logger.info(f"AI 경로 최적화 요청: {request.start_lat}, {request.start_lng} -> {request.end_lat}, {request.end_lng}")
        
        # 입력 유효성 검사
        self._validate_request(request)
        
        try:
            # AI 모델 호출 시도
            ai_response = await self._call_ai_model(request)
            logger.info("AI 모델 응답 수신 완료")
            return ai_response
            
        except Exception as e:
            logger.warning(f"AI 모델 호출 실패: {e}")
            
            if self.fallback_enabled:
                logger.info("대체 경로 알고리즘 사용")
                return await self._fallback_route_calculation(request)
            else:
                raise Exception("AI 모델을 사용할 수 없고 대체 알고리즘이 비활성화되어 있습니다.")
    
    def _validate_request(self, request: AIRouteRequest) -> None:
        """요청 데이터 유효성 검사"""
        if not validate_coordinates(request.start_lat, request.start_lng):
            raise DataFormatException(f"잘못된 출발지 좌표: {request.start_lat}, {request.start_lng}")
        
        if not validate_coordinates(request.end_lat, request.end_lng):
            raise DataFormatException(f"잘못된 목적지 좌표: {request.end_lat}, {request.end_lng}")
        
        # 출발지와 목적지가 너무 가까운 경우
        distance = calculate_distance(request.start_lat, request.start_lng, request.end_lat, request.end_lng)
        if distance < 0.1:  # 100m 미만
            raise DataFormatException("출발지와 목적지가 너무 가깝습니다.")
        
        # 거리가 너무 먼 경우 (100km 이상)
        if distance > 100:
            raise DataFormatException("출발지와 목적지가 너무 멉니다.")
    
    async def _call_ai_model(self, request: AIRouteRequest) -> AIRouteResponse:
        """실제 AI 모델 호출"""
        try:
            # 실제 AI 모델 서버에 HTTP 요청을 보내는 로직
            # 현재는 더미 구현
            
            # AI 모델 요청 데이터 준비
            request_data = request.to_dict()
            
            # 주변 인프라 정보 수집
            infrastructure_data = await self._collect_infrastructure_data(request)
            request_data['infrastructure'] = infrastructure_data
            
            logger.debug(f"AI 모델 요청 데이터: {json.dumps(request_data, indent=2)}")
            
            # TODO: 실제 AI 모델 서버에 HTTP 요청
            # import httpx
            # async with httpx.AsyncClient() as client:
            #     response = await client.post(self.model_url, json=request_data, timeout=30)
            #     response.raise_for_status()
            #     ai_result = response.json()
            
            # 임시 더미 응답 (실제 AI 모델 연동 전까지)
            ai_result = await self._generate_dummy_ai_response(request, infrastructure_data)
            
            return AIRouteResponse(ai_result)
            
        except Exception as e:
            logger.error(f"AI 모델 호출 중 오류: {e}")
            raise
    
    async def _collect_infrastructure_data(self, request: AIRouteRequest) -> Dict[str, Any]:
        """경로 계산에 필요한 인프라 데이터 수집"""
        logger.info("인프라 데이터 수집 시작")
        
        infrastructure = {
            "bike_stations": [],
            "bike_paths": [],
            "weather": "clear",  # 추후 날씨 API 연동
            "traffic_conditions": "normal"  # 추후 교통 정보 API 연동
        }
        
        try:
            # 자전거 대여소 정보 수집
            stations = self.tashu_api.get_stations()
            infrastructure["bike_stations"] = stations
            logger.info(f"자전거 대여소 {len(stations)}개 수집 완료")
            
            # 자전거 도로 정보 수집
            center_lat = (request.start_lat + request.end_lat) / 2
            center_lng = (request.start_lng + request.end_lng) / 2
            distance = calculate_distance(request.start_lat, request.start_lng, request.end_lat, request.end_lng)
            search_radius = min(max(int(distance * 1000), 2000), 10000)  # 2km ~ 10km
            
            bike_paths = self.duroonubi_api.get_bike_paths(center_lat, center_lng, search_radius)
            infrastructure["bike_paths"] = bike_paths.get("bike_paths", [])
            logger.info(f"자전거 도로 {len(infrastructure['bike_paths'])}개 수집 완료")
            
        except Exception as e:
            logger.warning(f"인프라 데이터 수집 중 오류: {e}")
            # 오류가 발생해도 계속 진행 (부분적인 데이터로도 경로 계산 가능)
        
        return infrastructure
    
    async def _generate_dummy_ai_response(self, request: AIRouteRequest, infrastructure: Dict[str, Any]) -> Dict[str, Any]:
        """AI 모델 연동 전 임시 더미 응답 생성"""
        logger.info("더미 AI 응답 생성")
        
        # 거리 및 시간 계산
        distance = calculate_distance(request.start_lat, request.start_lng, request.end_lat, request.end_lng)
        duration = max(int(distance / 15 * 60), 5)  # 평균 15km/h, 최소 5분
        
        # 더 정교한 경로 포인트 생성
        coordinates = self._generate_smart_route_points(
            request.start_lat, request.start_lng, 
            request.end_lat, request.end_lng,
            infrastructure.get("bike_paths", [])
        )
        
        return {
            "coordinates": coordinates,
            "total_distance": round(distance, 2),
            "estimated_duration": duration,
            "elevation_gain": max(0, distance * 10 + (coordinates[-1]["lat"] - coordinates[0]["lat"]) * 1000),
            "safety_score": min(0.8, 0.5 + len(infrastructure.get("bike_paths", [])) * 0.1),
            "confidence_score": 0.85,
            "algorithm_version": "dummy_v1.0",
            "process_time": 0.5
        }
    
    def _generate_smart_route_points(self, start_lat: float, start_lng: float, 
                                   end_lat: float, end_lng: float, 
                                   bike_paths: List[Dict[str, Any]]) -> List[Dict[str, float]]:
        """자전거 도로 정보를 고려한 더 정교한 경로 포인트 생성"""
        import random
        
        # 기본 직선 경로 생성
        distance = calculate_distance(start_lat, start_lng, end_lat, end_lng)
        num_points = max(5, int(distance * 4))  # 더 세밀한 포인트
        
        coordinates = []
        
        for i in range(num_points + 1):
            ratio = i / num_points
            lat = start_lat + (end_lat - start_lat) * ratio
            lng = start_lng + (end_lng - start_lng) * ratio
            
            # 자전거 도로 근처로 경로 조정 (간단한 휴리스틱)
            if bike_paths and 0 < i < num_points:
                closest_path = min(bike_paths, 
                                 key=lambda path: min(
                                     calculate_distance(lat, lng, coord["lat"], coord["lng"])
                                     for coord in path.get("coordinates", [{"lat": lat, "lng": lng}])
                                 ) if path.get("coordinates") else float('inf'))
                
                if closest_path.get("coordinates"):
                    closest_coord = min(closest_path["coordinates"],
                                      key=lambda coord: calculate_distance(lat, lng, coord["lat"], coord["lng"]))
                    
                    # 자전거 도로 방향으로 약간 조정
                    adjustment_factor = 0.3
                    lat += (closest_coord["lat"] - lat) * adjustment_factor
                    lng += (closest_coord["lng"] - lng) * adjustment_factor
            
            # 약간의 자연스러운 변화 추가
            if 0 < i < num_points:
                lat += random.uniform(-0.0005, 0.0005)
                lng += random.uniform(-0.0005, 0.0005)
            
            coordinates.append({"lat": round(lat, 6), "lng": round(lng, 6)})
        
        return coordinates
    
    async def _fallback_route_calculation(self, request: AIRouteRequest) -> AIRouteResponse:
        """AI 모델 실패 시 대체 경로 계산"""
        logger.info("대체 경로 계산 알고리즘 실행")
        
        # 인프라 데이터 수집
        infrastructure = await self._collect_infrastructure_data(request)
        
        # 더미 응답 생성 (대체 알고리즘)
        result = await self._generate_dummy_ai_response(request, infrastructure)
        result["algorithm_version"] = "fallback_v1.0"
        result["confidence_score"] = 0.6  # 대체 알고리즘이므로 낮은 신뢰도
        
        return AIRouteResponse(result)
    
    def get_model_status(self) -> Dict[str, Any]:
        """AI 모델 상태 확인"""
        return {
            "model_url": self.model_url,
            "fallback_enabled": self.fallback_enabled,
            "status": "ready",  # TODO: 실제 모델 상태 확인
            "last_check": datetime.now().isoformat()
        } 