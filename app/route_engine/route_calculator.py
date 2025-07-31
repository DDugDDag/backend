# backend\app\route_engine\route_calculator.py
"""
Route Calculator
대전 자전거 경로 계산 통합 클래스
"""

import sys
import os
import heapq
import math
import random
from typing import Dict, List, Tuple, Optional

from .cch import CustomizableContractionHierarchies, Graph, Vertex, Arc
from .daejeon_bike import get_bike_route_data, get_bike_storage_data
from .customer import CustomerPathFinder, ScenicPoint, RoutePreference


class RouteCalculator:
    """
    대전 자전거 경로 계산을 위한 통합 클래스
    """
    
    def __init__(self):
        """RouteCalculator 초기화"""
        self.graph: Optional[Graph] = None
        self.cch: Optional[CustomizableContractionHierarchies] = None
        self.customer_finder: Optional[CustomerPathFinder] = None
        self._initialized = False
    
    def initialize(self, num_routes: int = 500, num_storage: int = 50) -> bool:
        """
        경로 계산 엔진 초기화
        
        Args:
            num_routes: 가져올 자전거 도로 데이터 개수
            num_storage: 가져올 자전거 보관소 데이터 개수
            
        Returns:
            초기화 성공 여부
        """
        try:
            print("경로 계산 엔진 초기화 중...")
            
            # 1. 대전광역시 자전거 도로 데이터 가져오기
            bike_routes = self._fetch_bike_routes(num_of_rows=num_routes)
            if not bike_routes:
                print("자전거 도로 데이터를 가져오지 못했습니다.")
                return False
            
            # 2. 자전거 보관소 데이터 가져오기
            bike_storage = self._fetch_bike_storage(num_of_rows=num_storage)
            if bike_storage:
                print(f"자전거 보관소 {len(bike_storage)}개 데이터를 받았습니다.")
            
            # 3. 그래프 생성
            print("그래프 생성 중...")
            self.graph = self._create_bike_route_graph(bike_routes)
            print(f"그래프 생성 완료: {len(self.graph.vertices)}개의 정점, {len(self.graph.arcs)}개의 간선")
            
            # 4. 그래프 연결성 개선
            self._enhance_graph_connectivity(self.graph, distance_threshold=0.1)
            
            # 5. CCH 알고리즘 전처리
            print("CCH 알고리즘 전처리 중...")
            self.cch = self._preprocess_graph(self.graph)
            if not self.cch:
                print("CCH 알고리즘 전처리에 실패했습니다.")
                return False
            
            # 6. 사용자 맞춤형 경로 찾기 초기화
            self.customer_finder = CustomerPathFinder(self.graph)
            
            self._initialized = True
            print("경로 계산 엔진 초기화 완료!")
            return True
            
        except Exception as e:
            print(f"경로 계산 엔진 초기화 실패: {e}")
            return False
    
    def find_path(self, start_lat: float, start_lng: float, 
                  end_lat: float, end_lng: float) -> Optional[List[Dict]]:
        """
        두 지점 간의 최적 경로를 찾습니다.
        
        Args:
            start_lat: 출발지 위도
            start_lng: 출발지 경도
            end_lat: 도착지 위도
            end_lng: 도착지 경도
            
        Returns:
            경로 정보 리스트 또는 None
        """
        if not self._initialized:
            print("경로 계산 엔진이 초기화되지 않았습니다.")
            return None
        
        try:
            # 1. 가장 가까운 정점 찾기
            start_vertex_id = self._find_nearest_vertex(start_lat, start_lng)
            end_vertex_id = self._find_nearest_vertex(end_lat, end_lng)
            
            if start_vertex_id is None or end_vertex_id is None:
                print("출발지 또는 도착지 근처에 자전거 도로를 찾을 수 없습니다.")
                return None
            
            # 2. CCH 알고리즘으로 경로 찾기
            path = self._find_shortest_path(self.graph, self.cch, start_vertex_id, end_vertex_id)
            
            if not path:
                print("경로를 찾을 수 없습니다.")
                return None
            
            # 3. 경로 정보 변환
            route_info = self._convert_path_to_route_info(path)
            
            return route_info
            
        except Exception as e:
            print(f"경로 찾기 실패: {e}")
            return None
    
    def find_scenic_path(self, start_lat: float, start_lng: float, 
                        end_lat: float, end_lng: float,
                        preference: Optional[RoutePreference] = None) -> Optional[List[Dict]]:
        """
        경치가 좋은 경로를 찾습니다.
        
        Args:
            start_lat: 출발지 위도
            start_lng: 출발지 경도
            end_lat: 도착지 위도
            end_lng: 도착지 경도
            preference: 사용자 선호도 설정
            
        Returns:
            경로 정보 리스트 또는 None
        """
        if not self._initialized or not self.customer_finder:
            print("경로 계산 엔진이 초기화되지 않았습니다.")
            return None
        
        try:
            # 기본 선호도 설정
            if preference is None:
                preference = RoutePreference()
            
            # 가장 가까운 정점 찾기
            start_vertex_id = self._find_nearest_vertex(start_lat, start_lng)
            end_vertex_id = self._find_nearest_vertex(end_lat, end_lng)
            
            if start_vertex_id is None or end_vertex_id is None:
                return None
            
            # 사용자 맞춤형 경로 찾기
            path = self.customer_finder.find_scenic_path(start_vertex_id, end_vertex_id, preference)
            
            if not path:
                return None
            
            return self._convert_path_to_route_info(path)
            
        except Exception as e:
            print(f"경치 좋은 경로 찾기 실패: {e}")
            return None
    
    def _fetch_bike_routes(self, num_of_rows: int = 30) -> Optional[List]:
        """대전광역시 자전거 도로 데이터를 가져옵니다."""
        print("대전광역시 자전거 도로 데이터 요청 중...")
        bike_routes = get_bike_route_data(page_no=1, num_of_rows=num_of_rows)
        print("API 요청 완료")
        
        if bike_routes:
            print(f"자전거 도로 데이터 {len(bike_routes)}개를 받았습니다.")
            return bike_routes
        else:
            print("API 응답을 받지 못했습니다.")
            return None
    
    def _fetch_bike_storage(self, num_of_rows: int = 30) -> Optional[List]:
        """대전광역시 자전거 보관소 데이터를 가져옵니다."""
        print("대전광역시 자전거 보관소 데이터 요청 중...")
        bike_storage = get_bike_storage_data(page_no=1, num_of_rows=num_of_rows)
        print("API 요청 완료")
        
        if bike_storage:
            print(f"자전거 보관소 데이터 {len(bike_storage)}개를 받았습니다.")
            return bike_storage
        else:
            print("API 응답을 받지 못했습니다.")
            return None
    
    def _create_bike_route_graph(self, bike_routes: List) -> Graph:
        """자전거 도로 데이터로부터 그래프를 생성합니다."""
        graph = Graph()
        vertex_id_counter = 0
        coordinate_to_vertex = {}
        
        print(f"총 {len(bike_routes)}개의 자전거 도로 데이터를 처리합니다.")
        
        for route in bike_routes:
            try:
                # 위도, 경도 추출
                start_lat = float(route.get('strtpntLat', 0))
                start_lng = float(route.get('strtpntLot', 0))
                end_lat = float(route.get('endpntLat', 0))
                end_lng = float(route.get('endpntLot', 0))
                
                # 유효한 좌표인지 확인
                if start_lat == 0 or start_lng == 0 or end_lat == 0 or end_lng == 0:
                    continue
                
                # 시작점과 끝점에 대한 정점 생성 또는 찾기
                start_coord = (round(start_lat, 6), round(start_lng, 6))
                end_coord = (round(end_lat, 6), round(end_lng, 6))
                
                # 시작점 정점 처리
                if start_coord not in coordinate_to_vertex:
                    start_vertex = Vertex(id=vertex_id_counter, lat=start_lat, lon=start_lng)
                    graph.add_vertex(start_vertex)
                    coordinate_to_vertex[start_coord] = vertex_id_counter
                    vertex_id_counter += 1
                
                # 끝점 정점 처리
                if end_coord not in coordinate_to_vertex:
                    end_vertex = Vertex(id=vertex_id_counter, lat=end_lat, lon=end_lng)
                    graph.add_vertex(end_vertex)
                    coordinate_to_vertex[end_coord] = vertex_id_counter
                    vertex_id_counter += 1
                
                # 간선 생성
                start_vertex_id = coordinate_to_vertex[start_coord]
                end_vertex_id = coordinate_to_vertex[end_coord]
                
                # 거리 계산 (하버사인 공식)
                distance = self._calculate_distance(start_lat, start_lng, end_lat, end_lng)
                cost = int(distance * 1000)  # 미터 단위로 변환
                
                # 양방향 간선 추가
                start_vertex = graph.vertices[start_vertex_id]
                end_vertex = graph.vertices[end_vertex_id]
                
                arc1 = Arc(source=start_vertex, target=end_vertex, cost=cost)
                arc2 = Arc(source=end_vertex, target=start_vertex, cost=cost)
                
                graph.add_arc(arc1)
                graph.add_arc(arc2)
                
            except (ValueError, KeyError) as e:
                print(f"데이터 처리 오류: {e}")
                continue
        
        return graph
    
    def _enhance_graph_connectivity(self, graph: Graph, distance_threshold: float = 0.1):
        """그래프의 연결성을 개선합니다."""
        vertices = list(graph.vertices.values())
        added_edges = 0
        
        print(f"그래프 연결성 개선 중... (임계값: {distance_threshold}km)")
        
        for i, vertex1 in enumerate(vertices):
            for j, vertex2 in enumerate(vertices[i+1:], i+1):
                # 이미 연결된 정점들은 건너뛰기
                if (vertex1.id, vertex2.id) in graph.arcs:
                    continue
                
                # 거리 계산
                distance = self._calculate_distance(vertex1.lat, vertex1.lon, vertex2.lat, vertex2.lon)
                
                # 임계값 이내의 정점들을 연결
                if distance <= distance_threshold:
                    cost = int(distance * 1000)  # 미터 단위
                    
                    arc1 = Arc(source=vertex1, target=vertex2, cost=cost)
                    arc2 = Arc(source=vertex2, target=vertex1, cost=cost)
                    
                    graph.add_arc(arc1)
                    graph.add_arc(arc2)
                    added_edges += 2
        
        print(f"연결성 개선 완료: {added_edges}개의 간선이 추가되었습니다.")
    
    def _preprocess_graph(self, graph: Graph) -> Optional[CustomizableContractionHierarchies]:
        """그래프에 대해 CCH 알고리즘의 전처리 단계를 수행합니다."""
        try:
            # 정점 랭크 할당
            self._assign_vertex_ranks(graph)
            
            # CCH 객체 생성 및 전처리
            cch = CustomizableContractionHierarchies(graph)
            cch.metric_independent_preprocessing(len(graph.vertices))
            cch.customize()
            
            print("CCH 알고리즘 전처리 완료")
            return cch
            
        except Exception as e:
            print(f"CCH 전처리 실패: {e}")
            return None
    
    def _assign_vertex_ranks(self, graph: Graph):
        """그래프의 정점에 랭크를 할당합니다."""
        vertex_importance = {}
        
        # 각 정점의 중요도 계산 (인접 간선 수 기준)
        for vertex_id, vertex in graph.vertices.items():
            adjacent_arcs = 0
            for arc_key in graph.arcs:
                if arc_key[0] == vertex_id or arc_key[1] == vertex_id:
                    adjacent_arcs += 1
            vertex_importance[vertex_id] = adjacent_arcs
        
        # 중요도 순으로 정렬 (높은 중요도가 높은 랭크)
        sorted_vertices = sorted(vertex_importance.items(), key=lambda x: x[1], reverse=True)
        
        # 랭크 할당
        for rank, (vertex_id, importance) in enumerate(sorted_vertices):
            graph.vertices[vertex_id].rank = rank
    
    def _find_shortest_path(self, graph: Graph, cch: CustomizableContractionHierarchies, 
                           start_id: int, end_id: int) -> List[Arc]:
        """두 정점 간의 최단 경로를 찾습니다."""
        try:
            # CCH 알고리즘으로 경로 찾기
            path = cch.find_path(graph, start_id, end_id)
            if path:
                return path
            
            # CCH 실패 시 다익스트라 알고리즘 사용
            print("CCH 알고리즘 실패, 다익스트라 알고리즘으로 대체")
            return self._dijkstra(graph, start_id, end_id)
            
        except Exception as e:
            print(f"경로 찾기 오류: {e}")
            return []
    
    def _dijkstra(self, graph: Graph, start_id: int, end_id: int) -> List[Arc]:
        """다익스트라 알고리즘을 사용하여 최단 경로를 찾습니다."""
        distances = {vertex_id: float('inf') for vertex_id in graph.vertices}
        distances[start_id] = 0
        previous = {}
        visited = set()
        
        # 우선순위 큐 초기화
        pq = [(0, start_id)]
        
        while pq:
            current_distance, current_vertex = heapq.heappop(pq)
            
            if current_vertex in visited:
                continue
            
            visited.add(current_vertex)
            
            if current_vertex == end_id:
                break
            
            # 인접 정점들 확인
            for arc_key, arc in graph.arcs.items():
                if arc_key[0] == current_vertex:
                    neighbor = arc_key[1]
                    distance = current_distance + arc.cost
                    
                    if distance < distances[neighbor]:
                        distances[neighbor] = distance
                        previous[neighbor] = (current_vertex, arc)
                        heapq.heappush(pq, (distance, neighbor))
        
        # 경로 재구성
        if end_id not in previous:
            return []
        
        path = []
        current = end_id
        while current in previous:
            prev_vertex, arc = previous[current]
            path.append(arc)
            current = prev_vertex
        
        path.reverse()
        return path
    
    def _find_nearest_vertex(self, lat: float, lng: float) -> Optional[int]:
        """주어진 좌표에서 가장 가까운 정점을 찾습니다."""
        if not self.graph:
            return None
        
        min_distance = float('inf')
        nearest_vertex_id = None
        
        for vertex_id, vertex in self.graph.vertices.items():
            distance = self._calculate_distance(lat, lng, vertex.lat, vertex.lon)
            if distance < min_distance:
                min_distance = distance
                nearest_vertex_id = vertex_id
        
        return nearest_vertex_id
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """두 좌표 간의 거리를 계산합니다 (하버사인 공식, km 단위)."""
        R = 6371  # 지구 반지름 (km)
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def _convert_path_to_route_info(self, path: List[Arc]) -> List[Dict]:
        """경로를 API 응답 형식으로 변환합니다."""
        route_info = []
        total_distance = 0
        
        for i, arc in enumerate(path):
            total_distance += arc.cost / 1000  # km 단위로 변환
            
            route_info.append({
                "step": i + 1,
                "start_lat": arc.source.lat,
                "start_lng": arc.source.lon,
                "end_lat": arc.target.lat,
                "end_lng": arc.target.lon,
                "distance": arc.cost / 1000,  # km 단위
                "instruction": f"정점 {arc.source.id}에서 정점 {arc.target.id}로 이동"
            })
        
        # 요약 정보 추가
        if route_info:
            route_info.append({
                "summary": {
                    "total_distance": round(total_distance, 2),
                    "total_steps": len(path),
                    "estimated_time": round(total_distance / 15 * 60, 0)  # 15km/h 기준, 분 단위
                }
            })
        
        return route_info
