# app/services/route/route_service.py

import logging
import asyncio
from typing import List, Dict, Any, Optional

from app.common.utils import calculate_distance, validate_coordinates, DataFormatException
# 서비스 레이어에 필요한 다른 서비스들을 import
from app.services.external.external_api import TashuAPI
from app.services.ai.ai_integration import AIRouteOptimizer
from app.route_engine import RouteCalculator, RoutePreference

logger = logging.getLogger(__name__)

class RouteService:
    """
    자전거 경로 찾기 비즈니스 로직을 담당하는 서비스 클래스.
    의존성 주입(Dependency Injection)을 통해 다른 서비스를 받아서 사용합니다.
    """
    def __init__(self, tashu_api: TashuAPI, ai_optimizer: AIRouteOptimizer, route_calculator: RouteCalculator):
        self.tashu_api = tashu_api
        self.ai_optimizer = ai_optimizer
        self.route_calculator = route_calculator
        self._calculator_initialized = False
        logger.info("RouteService 모듈 초기화 완료")
    
    async def _ensure_calculator_initialized(self):
        """CCH 알고리즘 엔진 초기화 보장"""
        if not self._calculator_initialized:
            logger.info("CCH 경로 계산 엔진 초기화 중...")
            success = self.route_calculator.initialize(num_routes=500, num_storage=50)
            if success:
                self._calculator_initialized = True
                logger.info("CCH 경로 계산 엔진 초기화 완료")
            else:
                logger.warning("CCH 경로 계산 엔진 초기화 실패, AI 모델만 사용")
    
    def find_path(self, start_lat: float, start_lng: float, end_lat: float, end_lng: float, preferences: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        동기적으로 출발지와 목적지 사이의 최적 자전거 경로를 찾는 함수
        CCH 알고리즘을 우선 사용하고, 실패 시 AI 모델 사용
        """
        logger.info(f"경로 찾기 요청: ({start_lat}, {start_lng}) -> ({end_lat}, {end_lng})")
        
        try:
            # 좌표 유효성 검증
            if not validate_coordinates(start_lat, start_lng) or not validate_coordinates(end_lat, end_lng):
                raise DataFormatException("유효하지 않은 좌표입니다")
            
            # 1. CCH 알고리즘 시도 (동기적 초기화)
            if not self._calculator_initialized:
                logger.info("CCH 경로 계산 엔진 동기 초기화 중...")
                success = self.route_calculator.initialize(num_routes=300, num_storage=30)
                if success:
                    self._calculator_initialized = True
                    logger.info("CCH 경로 계산 엔진 초기화 완료")
            
            if self._calculator_initialized:
                # CCH 알고리즘으로 경로 계산
                if preferences and preferences.get('scenic', False):
                    # 경치 좋은 경로 요청
                    route_preference = RoutePreference(
                        scenic_weight=preferences.get('scenic_weight', 0.7),
                        distance_weight=preferences.get('distance_weight', 0.3),
                        elevation_weight=preferences.get('elevation_weight', 0.2),
                        traffic_weight=preferences.get('traffic_weight', 0.8)
                    )
                    cch_route = self.route_calculator.find_scenic_path(
                        start_lat, start_lng, end_lat, end_lng, route_preference
                    )
                else:
                    # 최단 경로 요청
                    cch_route = self.route_calculator.find_path(
                        start_lat, start_lng, end_lat, end_lng
                    )
                
                if cch_route:
                    logger.info("CCH 알고리즘으로 경로 찾기 성공")
                    return self._convert_cch_route_to_response(cch_route, start_lat, start_lng, end_lat, end_lng)
                else:
                    logger.warning("CCH 알고리즘 경로 찾기 실패, 기본 경로 생성")
            
            # 2. CCH 실패 시 기본 경로 생성
            return self._generate_basic_route(start_lat, start_lng, end_lat, end_lng)
            
        except Exception as e:
            logger.error(f"경로 찾기 오류: {e}")
            return self._generate_basic_route(start_lat, start_lng, end_lat, end_lng)
    
    def _convert_cch_route_to_response(self, cch_route: List[Dict], start_lat: float, start_lng: float, end_lat: float, end_lng: float) -> Dict[str, Any]:
        """
        CCH 알고리즘 결과를 API 응답 형식으로 변환
        """
        if not cch_route:
            return self._generate_basic_route(start_lat, start_lng, end_lat, end_lng)
        
        # 요약 정보 추출
        summary_info = cch_route[-1] if cch_route and 'summary' in cch_route[-1] else {}
        route_steps = cch_route[:-1] if summary_info else cch_route
        
        # 경로 포인트 생성
        route_points = []
        for step in route_steps:
            route_points.append({
                "lat": step["start_lat"],
                "lng": step["start_lng"]
            })
        
        # 마지막 지점 추가
        if route_steps:
            route_points.append({
                "lat": route_steps[-1]["end_lat"],
                "lng": route_steps[-1]["end_lng"]
            })
        
        # 턴바이턴 안내 생성
        instructions = []
        for i, step in enumerate(route_steps):
            instructions.append({
                "step": step["step"],
                "type": "navigation",
                "description": step["instruction"],
                "distance": step["distance"],
                "duration": max(1, int(step["distance"] / 15 * 60)),  # 15km/h 기준
                "coordinate": {
                    "lat": step["start_lat"],
                    "lng": step["start_lng"]
                }
            })
        
        # 도착 안내 추가
        if route_steps:
            instructions.append({
                "step": len(instructions) + 1,
                "type": "arrival",
                "description": "목적지에 도착했습니다.",
                "distance": summary_info.get('total_distance', 0),
                "duration": summary_info.get('estimated_time', 0),
                "coordinate": {
                    "lat": end_lat,
                    "lng": end_lng
                }
            })
        
        return {
            "route_id": None,
            "summary": {
                "distance": summary_info.get('total_distance', 0),
                "duration": summary_info.get('estimated_time', 0),
                "elevation_gain": 0,  # CCH에서는 고도 정보 없음
                "safety_score": 0.8,  # 자전거 전용 도로 기준
                "confidence_score": 0.9,  # CCH 알고리즘 신뢰도
                "algorithm_version": "CCH_v1.0",
                "bike_stations": 0  # 추후 구현
            },
            "route_points": route_points,
            "instructions": instructions,
            "nearby_stations": [],  # 추후 구현
            "metadata": {
                "generated_at": "cch_algorithm",
                "preferences": preferences or {},
                "process_time": 0.5
            }
        }
    
    async def find_path_async(self, start_lat: float, start_lng: float, end_lat: float, end_lng: float, 
                             preferences: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        비동기적으로 출발지와 목적지 사이의 최적 자전거 경로를 찾는 함수.
        AI 모델을 사용하여 경로를 최적화합니다.
        """
        logger.info(f"경로 찾기 요청: ({start_lat}, {start_lng}) -> ({end_lat}, {end_lng})")
        
        try:
            # AI 모델 요청 객체 생성
            from app.services.ai.ai_integration import AIRouteRequest
            ai_request = AIRouteRequest(start_lat, start_lng, end_lat, end_lng, preferences)
            
            # AI 모델을 사용하여 최적 경로 찾기
            ai_response = await self.ai_optimizer.find_optimal_route(ai_request)
            
            # 주변 자전거 대여소 정보 추가
            nearby_stations = await self._get_nearby_stations_async(start_lat, start_lng, end_lat, end_lng)
            
            # 턴바이턴 안내 생성
            instructions = self._generate_turn_by_turn_instructions(ai_response.coordinates, nearby_stations)
            
            # 최종 응답 구성
            response = {
                "route_id": None,
                "summary": {
                    "distance": ai_response.total_distance,
                    "duration": ai_response.estimated_duration,
                    "elevation_gain": ai_response.elevation_gain,
                    "safety_score": ai_response.safety_score,
                    "confidence_score": ai_response.confidence_score,
                    "algorithm_version": ai_response.algorithm_version,
                    "bike_stations": len(nearby_stations)
                },
                "route_points": ai_response.coordinates,
                "instructions": instructions,
                "nearby_stations": nearby_stations,
                "metadata": {
                    "generated_at": ai_request.timestamp,
                    "preferences": preferences or {},
                    "process_time": ai_response.process_time
                }
            }
            
            logger.info(f"경로 찾기 완료: {ai_response.total_distance}km, {ai_response.estimated_duration}분")
            return response
            
        except DataFormatException as e:
            logger.error(f"입력 데이터 오류: {e}")
            raise
        except Exception as e:
            logger.error(f"경로 찾기 중 오류: {e}")
            return await self._generate_fallback_route(start_lat, start_lng, end_lat, end_lng)

    def get_ai_model_status(self) -> Dict[str, Any]:
        """AI 모델 상태 조회"""
        return self.ai_optimizer.get_model_status()

    
    def find_path(self, start_lat: float, start_lng: float, end_lat: float, end_lng: float, 
                preferences: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        동기적 경로 찾기 함수 (기존 API 호환성을 위해 유지)
        내부적으로 비동기 함수를 호출합니다.
        """
        logger.info("동기 경로 찾기 요청 -> 비동기 처리로 변환")
        
        try:
            # 새로운 이벤트 루프에서 비동기 함수 실행
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(
                    self.find_path_async(start_lat, start_lng, end_lat, end_lng, preferences)
                )
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"동기 경로 찾기 중 오류: {e}")
            # 이벤트 루프 오류 시 기본 동기 경로 반환
            return self._generate_basic_route(start_lat, start_lng, end_lat, end_lng)
    
    async def _get_nearby_stations_async(self, start_lat: float, start_lng: float, 
                                end_lat: float, end_lng: float) -> List[Dict[str, Any]]:
        """비동기적으로 출발지와 목적지 근처의 자전거 대여소를 찾는 함수"""
        logger.info("주변 자전거 대여소 검색")
        
        try:
            # 자전거 대여소 정보 조회
            stations = self.tashu_api.get_stations()
            
            # 각 대여소의 거리 계산
            for station in stations:
                station["distance_from_start"] = calculate_distance(
                    start_lat, start_lng, station["lat"], station["lng"]
                )
                station["distance_from_end"] = calculate_distance(
                    end_lat, end_lng, station["lat"], station["lng"]
                )
            
            # 출발지와 목적지에서 가까운 대여소 선택
            start_stations = sorted(stations, key=lambda x: x["distance_from_start"])[:3]
            end_stations = sorted(stations, key=lambda x: x["distance_from_end"])[:3]
            
            # 중복 제거 및 위치 정보 추가
            all_stations = []
            seen_ids = set()
            
            for station in start_stations:
                if station["station_id"] not in seen_ids:
                    station["location_type"] = "start"
                    station["location_description"] = "출발지 근처"
                    all_stations.append(station)
                    seen_ids.add(station["station_id"])
            
            for station in end_stations:
                if station["station_id"] not in seen_ids:
                    station["location_type"] = "end"
                    station["location_description"] = "목적지 근처"
                    all_stations.append(station)
                    seen_ids.add(station["station_id"])
            
            logger.info(f"주변 대여소 {len(all_stations)}개 검색 완료")
            return all_stations
            
        except Exception as e:
            logger.error(f"주변 대여소 검색 중 오류: {e}")
            return []
    
    def _generate_turn_by_turn_instructions(self, route_points: List[Dict[str, float]], 
                                        nearby_stations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """턴바이턴 안내 지시사항 생성"""
        logger.info("턴바이턴 안내 생성")
        
        instructions = []
        
        if not route_points or len(route_points) < 2:
            return instructions
        
        # 출발 안내
        instructions.append({
            "step": 1,
            "type": "start",
            "description": "출발지에서 자전거 경로를 시작합니다.",
            "distance": 0,
            "duration": 0,
            "coordinate": route_points[0]
        })
        
        # 출발지 근처 대여소 안내
        start_stations = [s for s in nearby_stations if s.get("location_type") == "start"]
        for i, station in enumerate(start_stations):
            instructions.append({
                "step": len(instructions) + 1,
                "type": "bike_station",
                "description": f"{station['name']} 대여소에서 자전거를 대여할 수 있습니다. "
                            f"현재 {station['available_bikes']}대 이용 가능",
                "distance": round(station["distance_from_start"], 2),
                "duration": max(1, int(station["distance_from_start"] / 5 * 60)),  # 5km/h 도보 속도
                "coordinate": {"lat": station["lat"], "lng": station["lng"]},
                "station_info": {
                    "station_id": station["station_id"],
                    "available_bikes": station["available_bikes"],
                    "total_docks": station["total_docks"]
                }
            })
        
        # 중간 경로 안내 생성
        total_distance = sum(
            calculate_distance(route_points[i]["lat"], route_points[i]["lng"], 
                            route_points[i+1]["lat"], route_points[i+1]["lng"])
            for i in range(len(route_points) - 1)
        )
        
        # 주요 구간별 안내
        if len(route_points) > 4:
            quarter_point = len(route_points) // 4
            half_point = len(route_points) // 2
            three_quarter_point = len(route_points) * 3 // 4
            
            key_points = [
                (quarter_point, "1/4 지점"),
                (half_point, "중간 지점"),
                (three_quarter_point, "3/4 지점")
            ]
            
            for point_idx, description in key_points:
                if point_idx < len(route_points):
                    segment_distance = sum(
                        calculate_distance(route_points[i]["lat"], route_points[i]["lng"], 
                                         route_points[i+1]["lat"], route_points[i+1]["lng"])
                        for i in range(point_idx)
                    )
                    
                    instructions.append({
                        "step": len(instructions) + 1,
                        "type": "waypoint",
                        "description": f"{description}에 도달했습니다. 계속 직진하세요.",
                        "distance": round(segment_distance, 2),
                        "duration": max(1, int(segment_distance / 15 * 60)),
                        "coordinate": route_points[point_idx]
                    })
        
        # 목적지 근처 대여소 안내
        end_stations = [s for s in nearby_stations if s.get("location_type") == "end"]
        for station in end_stations:
            instructions.append({
                "step": len(instructions) + 1,
                "type": "bike_station",
                "description": f"목적지 근처 {station['name']} 대여소에서 자전거를 반납할 수 있습니다.",
                "distance": round(total_distance - station["distance_from_end"], 2),
                "duration": max(1, int((total_distance - station["distance_from_end"]) / 15 * 60)),
                "coordinate": {"lat": station["lat"], "lng": station["lng"]},
                "station_info": {
                    "station_id": station["station_id"],
                    "available_docks": station.get("total_docks", 0) - station.get("available_bikes", 0),
                    "total_docks": station["total_docks"]
                }
            })
        
        # 도착 안내
        instructions.append({
            "step": len(instructions) + 1,
            "type": "arrival",
            "description": "목적지에 도착했습니다.",
            "distance": round(total_distance, 2),
            "duration": max(1, int(total_distance / 15 * 60)),
            "coordinate": route_points[-1]
        })
        
        logger.info(f"턴바이턴 안내 {len(instructions)}개 생성 완료")
        return instructions
    
    async def _generate_fallback_route(self, start_lat: float, start_lng: float, 
                                 end_lat: float, end_lng: float) -> Dict[str, Any]:
        """AI 모델 실패 시 기본 경로 생성"""
        logger.warning("기본 경로 생성 모드")
        
        distance = calculate_distance(start_lat, start_lng, end_lat, end_lng)
        duration = max(int(distance / 15 * 60), 5)
        
        # 간단한 직선 경로
        num_points = max(3, int(distance * 2))
        route_points = []
        
        for i in range(num_points + 1):
            ratio = i / num_points
            lat = start_lat + (end_lat - start_lat) * ratio
            lng = start_lng + (end_lng - start_lng) * ratio
            route_points.append({"lat": lat, "lng": lng})
        
        return {
            "route_id": None,
            "summary": {
                "distance": round(distance, 2),
                "duration": duration,
                "elevation_gain": 0,
                "safety_score": 0.5,
                "confidence_score": 0.3,
                "algorithm_version": "fallback_basic",
                "bike_stations": 0
            },
            "route_points": route_points,
            "instructions": [
                {
                    "step": 1,
                    "type": "start",
                    "description": "출발지에서 목적지로 직진하세요.",
                    "distance": 0,
                    "duration": 0,
                    "coordinate": route_points[0]
                },
                {
                    "step": 2,
                    "type": "arrival",
                    "description": "목적지에 도착했습니다.",
                    "distance": round(distance, 2),
                    "duration": duration,
                    "coordinate": route_points[-1]
                }
            ],
            "nearby_stations": [],
            "metadata": {
                "generated_at": "fallback",
                "preferences": {},
                "process_time": 0.1
            }
        }
    
    def _generate_basic_route(self, start_lat: float, start_lng: float, 
                            end_lat: float, end_lng: float) -> Dict[str, Any]:
        """동기적 기본 경로 생성 (이벤트 루프 없이)"""
        logger.warning("기본 동기 경로 생성")
        
        distance = calculate_distance(start_lat, start_lng, end_lat, end_lng)
        duration = max(int(distance / 15 * 60), 5)
        
        route_points = [
            {"lat": start_lat, "lng": start_lng},
            {"lat": end_lat, "lng": end_lng}
        ]
        
        return {
            "route_id": None,
            "summary": {
                "distance": round(distance, 2),
                "duration": duration,
                "elevation_gain": 0,
                "safety_score": 0.5,
                "confidence_score": 0.2,
                "algorithm_version": "basic_sync",
                "bike_stations": 0
            },
            "route_points": route_points,
            "instructions": [
                {
                    "step": 1,
                    "type": "start",
                    "description": "출발지에서 목적지로 이동하세요.",
                    "distance": 0,
                    "duration": 0,
                    "coordinate": route_points[0]
                },
                {
                    "step": 2,
                    "type": "arrival",
                    "description": "목적지에 도착했습니다.",
                    "distance": round(distance, 2),
                    "duration": duration,
                    "coordinate": route_points[-1]
                }
            ],
            "nearby_stations": [],
            "metadata": {
                "generated_at": "basic_sync",
                "preferences": {},
                "process_time": 0.05
            }
        }