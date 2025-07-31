# backend\main.py
import os
import json
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import httpx
import random
import time
from datetime import datetime

# 환경 변수 로드
load_dotenv()
KAKAO_MAP_API_KEY = os.getenv("KAKAO_MAP_API_KEY", "YOUR_DEFAULT_KEY")
KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY", KAKAO_MAP_API_KEY)

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 앱에서는 허용할 출처를 제한하는 것이 좋습니다
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

# 마커 데이터 모델
class MarkerData:
    def __init__(self, id: str, title: str, description: str, lat: float, lng: float):
        self.id = id
        self.title = title
        self.description = description
        self.coordinate = {"latitude": lat, "longitude": lng}

@app.get("/map", response_class=HTMLResponse)
async def show_map(
    request: Request, 
    lat: float = 36.35, 
    lng: float = 127.38, 
    markers: Optional[str] = None
):
    marker_data = []
    if markers:
        try:
            marker_data = json.loads(markers)
        except:
            pass
    
    return templates.TemplateResponse("map.html", {
        "request": request,
        "lat": lat,
        "lng": lng,
        "api_key": KAKAO_MAP_API_KEY,
        "markers": marker_data
    })

@app.get("/api/search")
async def search_places(
    query: str, 
    lat: Optional[float] = None, 
    lng: Optional[float] = None,
    radius: Optional[int] = 5000,
    page: Optional[int] = 1,
    size: Optional[int] = 15
) -> List[dict]:
    """
    키워드로 장소를 검색합니다.
    """
    try:
        headers = {"Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"}
        params = {
            "query": query,
            "page": page,
            "size": size
        }
        
        # 위치 기반 검색 옵션 추가
        if lat is not None and lng is not None:
            params["y"] = lat
            params["x"] = lng
            params["radius"] = radius
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://dapi.kakao.com/v2/local/search/keyword.json",
                params=params,
                headers=headers
            )
            
            if response.status_code != 200:
                return JSONResponse(
                    status_code=response.status_code,
                    content={"error": f"카카오 API 요청 실패: {response.status_code}"}
                )
            
            data = response.json()
            
            # 검색 결과를 마커 형식으로 변환
            results = []
            for item in data.get("documents", []):
                marker = {
                    "id": item.get("id", str(hash(item.get("place_name", "")))),
                    "title": item.get("place_name", ""),
                    "description": f"{item.get('address_name', '') or item.get('road_address_name', '')}\n{item.get('phone', '')}",
                    "coordinate": {
                        "latitude": float(item.get("y", 0)),
                        "longitude": float(item.get("x", 0))
                    }
                }
                results.append(marker)
            
            return results
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"검색 중 오류 발생: {str(e)}"}
        )

# 새로 추가하는 API 엔드포인트들
@app.get("/api/health")
async def health_check():
    """
    서버 상태를 확인합니다.
    """
    return {
        "status": "ok",
        "message": "뚜따 API 서버가 정상 작동 중입니다.",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# 경로 찾기 API
@app.post("/api/find-path")
async def find_path(request: Dict[str, Any]):
    """
    출발지와 도착지 사이의 자전거 경로를 계산합니다.
    """
    try:
        # 요청에서 필요한 데이터 추출
        start_lat = request.get("start_lat")
        start_lng = request.get("start_lng")
        end_lat = request.get("end_lat")
        end_lng = request.get("end_lng")
        preferences = request.get("preferences", {})
        
        if not all([start_lat, start_lng, end_lat, end_lng]):
            return JSONResponse(
                status_code=400,
                content={"error": "출발지와 도착지 좌표가 필요합니다."}
            )
        
        # 현재는 가상의 경로 데이터를 생성합니다 (실제로는 외부 API 호출이나 알고리즘 사용)
        route_points = generate_route_points(start_lat, start_lng, end_lat, end_lng)
        
        # 경로 안내 생성
        instructions = generate_route_instructions(route_points)
        
        # 주변 자전거 대여소 생성
        nearby_stations = generate_nearby_stations(start_lat, start_lng, end_lat, end_lng)
        
        # 경로 요약 정보
        distance = calculate_distance(route_points)
        duration = calculate_duration(distance)
        
        # 응답 데이터 구성
        response_data = {
            "route_id": f"route_{int(time.time())}",
            "summary": {
                "distance": round(distance, 2),
                "duration": duration,
                "elevation_gain": random.randint(10, 100),
                "safety_score": random.randint(70, 95),
                "confidence_score": random.randint(80, 99),
                "algorithm_version": "1.0.0",
                "bike_stations": len(nearby_stations)
            },
            "route_points": route_points,
            "instructions": instructions,
            "nearby_stations": nearby_stations,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "preferences": preferences,
                "process_time": random.uniform(0.1, 1.5)
            }
        }
        
        return response_data
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"경로 계산 중 오류 발생: {str(e)}"}
        )

@app.get("/api/bike-stations")
async def get_bike_stations(
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    radius: Optional[int] = 2000
):
    """
    주변 자전거 대여소 정보를 제공합니다.
    """
    try:
        # 샘플 자전거 대여소 데이터 생성
        stations = generate_nearby_stations(
            lat or 37.5662,
            lng or 126.9784,
            lat or 37.5662,
            lng or 126.9784,
            count=10
        )
        
        return stations
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"자전거 대여소 정보 조회 중 오류 발생: {str(e)}"}
        )

@app.get("/api/bike-stations/{station_id}")
async def get_bike_station_status(station_id: str):
    """
    특정 자전거 대여소의 상태를 확인합니다.
    """
    try:
        # 가상의 대여소 상태 데이터 생성
        return {
            "station_id": station_id,
            "name": f"뚜따 대여소 {station_id[-4:]}",
            "address": "서울특별시 중구 세종대로 110",
            "lat": 37.5662 + random.uniform(-0.01, 0.01),
            "lng": 126.9784 + random.uniform(-0.01, 0.01),
            "available_bikes": random.randint(0, 20),
            "total_docks": 20,
            "last_updated": datetime.now().isoformat(),
            "status": "운영중"
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"대여소 상태 조회 중 오류 발생: {str(e)}"}
        )

@app.get("/api/bike-paths")
async def get_bike_paths(
    lat: float,
    lng: float,
    radius: Optional[int] = 2000
):
    """
    주변의 자전거 도로 정보를 제공합니다.
    """
    try:
        # 가상의 자전거 도로 데이터 생성
        paths = []
        for i in range(5):
            path_points = []
            start_lat = lat + random.uniform(-0.01, 0.01)
            start_lng = lng + random.uniform(-0.01, 0.01)
            
            # 자전거 도로 경로 생성
            for j in range(10):
                path_points.append({
                    "lat": start_lat + random.uniform(-0.005, 0.005) * j/10,
                    "lng": start_lng + random.uniform(-0.005, 0.005) * j/10
                })
            
            paths.append({
                "id": f"path_{i}",
                "name": f"자전거도로 {i+1}",
                "type": random.choice(["전용도로", "겸용도로", "우선도로"]),
                "length": random.randint(500, 5000),
                "points": path_points
            })
        
        return paths
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"자전거 도로 정보 조회 중 오류 발생: {str(e)}"}
        )

@app.get("/")
def read_root():
    return {"message": "뚜따 API 서버가 실행 중입니다."}

# 경로 생성 도우미 함수들
def generate_route_points(start_lat, start_lng, end_lat, end_lng, points_count=20):
    """
    출발지와 도착지 사이의 경로 포인트를 생성합니다.
    """
    route_points = []
    for i in range(points_count):
        progress = i / (points_count - 1)
        lat = start_lat + (end_lat - start_lat) * progress
        lng = start_lng + (end_lng - start_lng) * progress
        
        # 약간의 무작위성 추가 (직선이 아닌 경로처럼 보이도록)
        if 0 < i < points_count - 1:
            # 중간 지점들에만 무작위성 추가
            lat += random.uniform(-0.002, 0.002)
            lng += random.uniform(-0.002, 0.002)
        
        route_points.append({
            "lat": lat,
            "lng": lng
        })
    
    return route_points

def generate_route_instructions(route_points):
    """
    경로 포인트에 기반한 경로 안내를 생성합니다.
    """
    instructions = []
    
    # 첫 안내: 출발
    instructions.append({
        "step": 1,
        "type": "start",
        "description": "출발 지점에서 시작하세요.",
        "distance": 0,
        "duration": 0,
        "coordinate": route_points[0]
    })
    
    # 중간 안내
    direction_types = ["straight", "left", "right", "slight-left", "slight-right"]
    instruction_templates = [
        "{}m 직진하세요.",
        "왼쪽으로 회전하세요.",
        "오른쪽으로 회전하세요.",
        "약간 왼쪽으로 회전하세요.",
        "약간 오른쪽으로 회전하세요."
    ]
    
    step = 2
    total_distance = 0
    
    # 중간 지점마다 안내 생성
    for i in range(1, len(route_points) - 1, 3):  # 모든 포인트가 아닌 일부만 안내로 사용
        if i >= len(route_points) - 1:
            break
            
        # 거리 계산 (간단한 계산, 실제로는 더 정확한 방법 필요)
        segment_distance = random.randint(100, 500)
        total_distance += segment_distance
        
        # 소요 시간 계산 (평균 속도 15km/h 가정)
        duration = int(segment_distance / 250)  # 약 15km/h = 250m/분
        
        direction_index = random.randint(0, len(direction_types) - 1)
        description = instruction_templates[direction_index]
        
        if direction_index == 0:  # straight 타입인 경우 거리 포함
            description = description.format(segment_distance)
        
        instructions.append({
            "step": step,
            "type": direction_types[direction_index],
            "description": description,
            "distance": segment_distance,
            "duration": duration,
            "coordinate": route_points[i]
        })
        
        step += 1
    
    # 마지막 안내: 도착
    instructions.append({
        "step": step,
        "type": "finish",
        "description": "목적지에 도착했습니다.",
        "distance": 0,
        "duration": 0,
        "coordinate": route_points[-1]
    })
    
    return instructions

def generate_nearby_stations(start_lat, start_lng, end_lat, end_lng, count=5):
    """
    출발지와 도착지 주변의 자전거 대여소를 생성합니다.
    """
    stations = []
    
    # 출발지 주변 대여소
    for i in range(count // 2):
        station_lat = start_lat + random.uniform(-0.005, 0.005)
        station_lng = start_lng + random.uniform(-0.005, 0.005)
        
        stations.append({
            "station_id": f"start_station_{i}",
            "name": f"출발지 주변 대여소 {i+1}",
            "address": "서울특별시 중구",
            "lat": station_lat,
            "lng": station_lng,
            "available_bikes": random.randint(0, 20),
            "total_docks": 20,
            "distance_from_start": random.randint(50, 500),
            "distance_from_end": random.randint(1000, 5000),
            "location_type": "start",
            "location_description": "출발지 주변",
            "last_updated": datetime.now().isoformat()
        })
    
    # 도착지 주변 대여소
    for i in range(count - count // 2):
        station_lat = end_lat + random.uniform(-0.005, 0.005)
        station_lng = end_lng + random.uniform(-0.005, 0.005)
        
        stations.append({
            "station_id": f"end_station_{i}",
            "name": f"도착지 주변 대여소 {i+1}",
            "address": "서울특별시 중구",
            "lat": station_lat,
            "lng": station_lng,
            "available_bikes": random.randint(0, 20),
            "total_docks": 20,
            "distance_from_start": random.randint(1000, 5000),
            "distance_from_end": random.randint(50, 500),
            "location_type": "end",
            "location_description": "도착지 주변",
            "last_updated": datetime.now().isoformat()
        })
    
    return stations

def calculate_distance(route_points):
    """
    경로 포인트들의 총 거리를 계산합니다. (단위: km)
    매우 간단한 계산으로, 실제로는 하버사인 공식 등 더 정확한 방법 사용
    """
    total_distance = 0
    for i in range(len(route_points) - 1):
        # 간단한 유클리드 거리 계산 (실제로는 위도/경도 거리 계산에 적합하지 않음)
        lat1, lng1 = route_points[i]["lat"], route_points[i]["lng"]
        lat2, lng2 = route_points[i+1]["lat"], route_points[i+1]["lng"]
        
        # 지구 반경 약 6371km
        # 간단한 거리 계산을 위해 스케일링
        distance = ((lat1 - lat2)**2 + (lng1 - lng2)**2)**0.5 * 111  # 1도 당 약 111km
        total_distance += distance
    
    return total_distance

def calculate_duration(distance_km):
    """
    거리를 기반으로 소요 시간을 계산합니다. (단위: 분)
    평균 자전거 속도를 15km/h로 가정
    """
    return int(distance_km * 60 / 15)  # 15km/h = 0.25km/분

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 