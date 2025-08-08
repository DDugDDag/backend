# app/api/schemas/route_schema.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# 사용자 스키마
class UserBase(BaseModel):
    username: str
    email: str
    nickname: str


class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    """사용자 정보 수정 요청 모델"""
    nickname: Optional[str] = Field(None, description="새로운 닉네임")
    
class UserResponse(UserBase):
    id: int
    created_at: datetime
    
class Config:
    from_attributes = True

# 경로 관련 스키마
class RouteRequest(BaseModel):
    """경로 찾기 요청 모델"""
    start_lat: float = Field(..., description="출발지 위도", ge=-90, le=90, example=36.3504)
    start_lng: float = Field(..., description="출발지 경도", ge=-180, le=180, example=127.3845)
    end_lat: float = Field(..., description="목적지 위도", ge=-90, le=90, example=36.3621)
    end_lng: float = Field(..., description="목적지 경도", ge=-180, le=180, example=127.3489)
    preferences: Optional[Dict[str, Any]] = Field(
        default={},
        description="""
        경로 탐색에 영향을 주는 사용자 설정.
        - `prioritize_safety`: `bool` 안전한 경로 우선 (기본값: `false`)
        - `avoid_hills`: `bool` 언덕 피하기 (기본값: `false`)
        """
    )

class RoutePoint(BaseModel):
    """경로상의 한 점을 나타내는 모델"""
    lat: float = Field(..., description="위도")
    lng: float = Field(..., description="경도")

class RouteSummary(BaseModel):
    """경로 요약 정보 모델"""
    distance: float = Field(..., description="총 거리 (km)")
    duration: int = Field(..., description="예상 소요 시간 (분)")
    elevation_gain: float = Field(default=0.0, description="고도 상승 (m)")
    safety_score: float = Field(default=0.5, description="안전도 점수 (0-1)")
    confidence_score: float = Field(default=0.5, description="AI 모델 신뢰도 (0-1)")
    algorithm_version: str = Field(default="unknown", description="사용된 알고리즘 버전")
    bike_stations: int = Field(default=0, description="주변 대여소 수")

class RouteMetadata(BaseModel):
    """경로 메타데이터 모델"""
    generated_at: str = Field(..., description="생성 시간")
    preferences: Dict[str, Any] = Field(default={}, description="사용된 설정")
    process_time: float = Field(default=0.0, description="처리 시간 (초)")

class StationInfo(BaseModel):
    """대여소 정보 모델"""
    station_id: str = Field(..., description="대여소 ID")
    available_bikes: int = Field(..., description="이용 가능한 자전거 수")
    total_docks: int = Field(..., description="총 도킹 스테이션 수")
    available_docks: Optional[int] = Field(None, description="이용 가능한 도킹 스테이션 수")

class RouteInstruction(BaseModel):
    """경로 안내 지시사항 모델"""
    step: int = Field(..., description="단계 번호")
    type: str = Field(..., description="지시사항 유형 (start, waypoint, bike_station, arrival)")
    description: str = Field(..., description="안내 내용")
    distance: float = Field(..., description="해당 지점까지의 거리 (km)")
    duration: int = Field(..., description="해당 지점까지의 예상 소요 시간 (분)")
    coordinate: RoutePoint = Field(..., description="해당 지점의 좌표")
    station_info: Optional[StationInfo] = Field(None, description="대여소 정보 (bike_station 타입일 때)")

class NearbyStation(BaseModel):
    """주변 대여소 정보 모델"""
    station_id: str = Field(..., description="대여소 ID")
    name: str = Field(..., description="대여소 이름")
    address: str = Field(..., description="대여소 주소")
    lat: float = Field(..., description="대여소 위도")
    lng: float = Field(..., description="대여소 경도")
    available_bikes: int = Field(..., description="이용 가능한 자전거 수")
    total_docks: int = Field(..., description="총 도킹 스테이션 수")
    distance_from_start: float = Field(..., description="출발지로부터의 거리 (km)")
    distance_from_end: float = Field(..., description="목적지로부터의 거리 (km)")
    location_type: str = Field(..., description="위치 유형 (start, end)")
    location_description: str = Field(..., description="위치 설명")
    last_updated: str = Field(..., description="마지막 업데이트 시간")

class RouteResponse(BaseModel):
    """경로 찾기 응답 모델"""
    route_id: Optional[str] = Field(None, description="경로 ID (저장된 경우)")
    summary: RouteSummary = Field(..., description="경로 요약 정보")
    route_points: List[RoutePoint] = Field(..., description="경로상의 좌표 목록")
    instructions: List[RouteInstruction] = Field(..., description="턴바이턴 안내")
    nearby_stations: List[NearbyStation] = Field(..., description="주변 대여소 정보")
    metadata: RouteMetadata = Field(..., description="메타데이터")
    
# 자전거 대여소 스키마
class BikeStationBase(BaseModel):
    station_id: str
    name: str
    address: str
    lat: float
    lng: float
    available_bikes: int

class BikeStationResponse(BaseModel):
    """자전거 대여소 응답 모델"""
    station_id: str = Field(..., description="대여소 ID")
    name: str = Field(..., description="대여소 이름")
    address: str = Field(..., description="대여소 주소")
    lat: float = Field(..., description="위도")
    lng: float = Field(..., description="경도")
    available_bikes: int = Field(..., description="이용 가능한 자전거 수")
    total_docks: int = Field(..., description="총 도킹 스테이션 수")
    last_updated: str = Field(..., description="마지막 업데이트 시간")

class AIModelStatusResponse(BaseModel):
    """AI 모델 상태 응답 모델"""
    model_url: str = Field(..., description="AI 모델 서버 URL")
    fallback_enabled: bool = Field(..., description="대체 알고리즘 활성화 여부")
    status: str = Field(..., description="모델 상태")
    last_check: str = Field(..., description="마지막 확인 시간")

class ErrorResponse(BaseModel):
    """오류 응답 모델"""
    error: str = Field(..., description="오류 유형")
    message: str = Field(..., description="오류 메시지")
    details: Optional[Dict[str, Any]] = Field(None, description="추가 오류 정보")

# 외부 API 응답 모델들
class ExternalBikePath(BaseModel):
    """외부 API 자전거 도로 모델"""
    path_id: str = Field(..., description="도로 ID")
    name: str = Field(..., description="도로 이름")
    length: float = Field(..., description="길이 (km)")
    path_type: str = Field(..., description="도로 유형")
    coordinates: List[RoutePoint] = Field(..., description="도로 좌표")

class ExternalBikeRoute(BaseModel):
    """외부 API 자전거 노선 모델"""
    route_id: str = Field(..., description="노선 ID")
    name: str = Field(..., description="노선 이름")
    length: float = Field(..., description="길이 (km)")
    difficulty: str = Field(..., description="난이도")
    description: str = Field(..., description="설명")

class BikePathsResponse(BaseModel):
    """자전거 도로 응답 모델"""
    bike_paths: List[ExternalBikePath] = Field(..., description="자전거 도로 목록")

class BikeRoutesResponse(BaseModel):
    """자전거 노선 응답 모델"""
    routes: List[ExternalBikeRoute] = Field(..., description="자전거 노선 목록") 