import pytest
import unittest.mock as mock
from unittest.mock import Mock, patch, MagicMock
import requests
from datetime import datetime

from app.api.external import TashuAPI, DuroonubiAPI, DaejeonBikeAPI
from app.api.utils import APIException, NetworkException, AuthenticationException, DataFormatException

class TestTashuAPI:
    """타슈 API 테스트"""
    
    def test_get_stations_success(self):
        """타슈 대여소 조회 성공 테스트"""
        # Mock 응답 데이터
        mock_response_data = {
            "stations": [
                {
                    "id": "ST001",
                    "name": "테스트 대여소",
                    "address": "테스트 주소",
                    "latitude": 36.332612,
                    "longitude": 127.434732,
                    "available_bikes": 5,
                    "total_docks": 10
                }
            ]
        }
        
        with patch('app.api.external.create_session_with_retry') as mock_create_session:
            # Mock 세션과 응답 설정
            mock_response = Mock()
            mock_response.ok = True
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            
            mock_session = Mock()
            mock_session.get.return_value = mock_response
            mock_create_session.return_value = mock_session
            
            # API 인스턴스 생성 및 테스트 실행
            tashu_api = TashuAPI(api_key="test_api_key")
            result = tashu_api.get_stations()
            
            # 검증
            assert len(result) == 1
            assert result[0]["station_id"] == "ST001"
            assert result[0]["name"] == "테스트 대여소"
            assert result[0]["lat"] == 36.332612
            assert result[0]["lng"] == 127.434732
    
    def test_get_stations_network_error_fallback(self):
        """타슈 대여소 조회 네트워크 오류 시 더미 데이터 반환 테스트"""
        with patch('app.api.external.create_session_with_retry') as mock_create_session:
            # Mock 세션에서 네트워크 오류 발생
            mock_session = Mock()
            mock_session.get.side_effect = requests.ConnectionError("Connection failed")
            mock_create_session.return_value = mock_session
            
            # API 인스턴스 생성 및 테스트 실행
            tashu_api = TashuAPI(api_key="test_api_key")
            result = tashu_api.get_stations()
            
            # 검증 (더미 데이터가 반환됨)
            assert len(result) == 3
            assert result[0]["station_id"] == "ST001"
    
    def test_get_stations_auth_error(self):
        """타슈 대여소 조회 인증 오류 테스트"""
        with patch('app.api.external.create_session_with_retry') as mock_create_session:
            # Mock 인증 실패 응답
            mock_response = Mock()
            mock_response.ok = False
            mock_response.status_code = 401
            
            mock_session = Mock()
            mock_session.get.return_value = mock_response
            mock_create_session.return_value = mock_session
            
            # API 인스턴스 생성 및 테스트 실행
            tashu_api = TashuAPI(api_key="test_api_key")
            
            with pytest.raises(AuthenticationException):
                tashu_api.get_stations()
    
    def test_get_station_status_success(self):
        """타슈 대여소 상태 조회 성공 테스트"""
        mock_response_data = {
            "station_id": "ST001",
            "available_bikes": 7,
            "total_docks": 12,
            "last_updated": "2023-05-15T14:30:00Z"
        }
        
        with patch('app.api.external.create_session_with_retry') as mock_create_session:
            mock_response = Mock()
            mock_response.ok = True
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            
            mock_session = Mock()
            mock_session.get.return_value = mock_response
            mock_create_session.return_value = mock_session
            
            tashu_api = TashuAPI(api_key="test_api_key")
            result = tashu_api.get_station_status("ST001")
            
            assert result["station_id"] == "ST001"
            assert result["available_bikes"] == 7
            assert result["total_docks"] == 12
            assert result["available_docks"] == 5
    
    def test_no_api_key(self):
        """API 키 없이 초기화 테스트"""
        with patch('app.api.external.create_session_with_retry'):
            api = TashuAPI(api_key="")
            result = api.get_stations()
            
            # API 키가 없으면 더미 데이터 반환
            assert len(result) == 3


class TestDuroonubiAPI:
    """두루누비 API 테스트"""
    
    def test_get_bike_paths_success(self):
        """두루누비 자전거 도로 조회 성공 테스트"""
        mock_response_data = {
            "bike_paths": [
                {
                    "path_id": "P001",
                    "name": "테스트 자전거도로",
                    "length": 5.2,
                    "path_type": "전용도로",
                    "coordinates": [
                        {"lat": 36.350971, "lng": 127.385288},
                        {"lat": 36.347563, "lng": 127.377091}
                    ]
                }
            ]
        }
        
        with patch('app.api.external.create_session_with_retry') as mock_create_session:
            mock_response = Mock()
            mock_response.ok = True
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            
            mock_session = Mock()
            mock_session.get.return_value = mock_response
            mock_create_session.return_value = mock_session
            
            duroonubi_api = DuroonubiAPI(api_key="test_api_key")
            result = duroonubi_api.get_bike_paths(36.350971, 127.385288)
            
            assert "bike_paths" in result
            assert len(result["bike_paths"]) == 1
            assert result["bike_paths"][0]["path_id"] == "P001"
            assert result["bike_paths"][0]["name"] == "테스트 자전거도로"
    
    def test_invalid_coordinates(self):
        """잘못된 좌표 입력 테스트"""
        with patch('app.api.external.create_session_with_retry'):
            duroonubi_api = DuroonubiAPI(api_key="test_api_key")
            
            with pytest.raises(DataFormatException):
                duroonubi_api.get_bike_paths(91.0, 127.385288)  # 위도 범위 초과
            
            with pytest.raises(DataFormatException):
                duroonubi_api.get_bike_paths(36.350971, 181.0)  # 경도 범위 초과
    
    def test_network_error_fallback(self):
        """두루누비 네트워크 오류 시 더미 데이터 반환 테스트"""
        with patch('app.api.external.create_session_with_retry') as mock_create_session:
            mock_session = Mock()
            mock_session.get.side_effect = requests.ConnectionError("Connection failed")
            mock_create_session.return_value = mock_session
            
            duroonubi_api = DuroonubiAPI(api_key="test_api_key")
            result = duroonubi_api.get_bike_paths(36.350971, 127.385288)
            
            # 더미 데이터 반환 확인
            assert "bike_paths" in result
            assert len(result["bike_paths"]) == 2  # 더미 데이터 개수


class TestDaejeonBikeAPI:
    """대전 자전거 API 테스트"""
    
    def test_get_bike_routes_success(self):
        """대전 자전거 노선 조회 성공 테스트"""
        mock_response_data = {
            "routes": [
                {
                    "route_id": "R001",
                    "name": "테스트 자전거길",
                    "length": 15.3,
                    "difficulty": "쉬움",
                    "description": "테스트용 자전거 코스입니다."
                }
            ]
        }
        
        with patch('app.api.external.create_session_with_retry') as mock_create_session:
            mock_response = Mock()
            mock_response.ok = True
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            
            mock_session = Mock()
            mock_session.get.return_value = mock_response
            mock_create_session.return_value = mock_session
            
            daejeon_api = DaejeonBikeAPI(api_key="test_api_key")
            result = daejeon_api.get_bike_routes()
            
            assert "routes" in result
            assert len(result["routes"]) == 1
            assert result["routes"][0]["route_id"] == "R001"
            assert result["routes"][0]["name"] == "테스트 자전거길"
            assert result["routes"][0]["length"] == 15.3
    
    def test_network_error_fallback(self):
        """대전 자전거 API 네트워크 오류 시 더미 데이터 반환 테스트"""
        with patch('app.api.external.create_session_with_retry') as mock_create_session:
            mock_session = Mock()
            mock_session.get.side_effect = requests.ConnectionError("Connection failed")
            mock_create_session.return_value = mock_session
            
            daejeon_api = DaejeonBikeAPI(api_key="test_api_key")
            result = daejeon_api.get_bike_routes()
            
            # 더미 데이터 반환 확인
            assert "routes" in result
            assert len(result["routes"]) == 3  # 더미 데이터 개수


class TestIntegration:
    """통합 테스트"""
    
    def test_all_apis_integration(self):
        """모든 API 통합 테스트 (더미 데이터)"""
        with patch('app.api.external.create_session_with_retry'):
            # API 인스턴스 생성 (빈 키로 더미 데이터 테스트)
            tashu = TashuAPI(api_key="")
            duroonubi = DuroonubiAPI(api_key="")
            daejeon = DaejeonBikeAPI(api_key="")
            
            # 모든 API 호출
            stations = tashu.get_stations()
            paths = duroonubi.get_bike_paths(36.350971, 127.385288)
            routes = daejeon.get_bike_routes()
            
            # 기본 검증
            assert isinstance(stations, list)
            assert len(stations) > 0
            
            assert isinstance(paths, dict)
            assert "bike_paths" in paths
            
            assert isinstance(routes, dict)
            assert "routes" in routes
            
            # 데이터 구조 검증
            for station in stations:
                assert "station_id" in station
                assert "name" in station
                assert "lat" in station
                assert "lng" in station
                assert isinstance(station["lat"], float)
                assert isinstance(station["lng"], float)
            
            for path in paths["bike_paths"]:
                assert "path_id" in path
                assert "name" in path
                assert "coordinates" in path
                assert isinstance(path["coordinates"], list)
            
            for route in routes["routes"]:
                assert "route_id" in route
                assert "name" in route
                assert "length" in route
                assert isinstance(route["length"], float)

    def test_error_handling_integration(self):
        """오류 처리 통합 테스트"""
        with patch('app.api.external.create_session_with_retry') as mock_create_session:
            # 네트워크 오류 발생 시뮬레이션
            mock_session = Mock()
            mock_session.get.side_effect = requests.ConnectionError("Connection failed")
            mock_create_session.return_value = mock_session
            
            # API 인스턴스 생성
            tashu = TashuAPI(api_key="test_key")
            duroonubi = DuroonubiAPI(api_key="test_key")
            daejeon = DaejeonBikeAPI(api_key="test_key")
            
            # 모든 API가 네트워크 오류 시에도 더미 데이터를 반환하는지 확인
            stations = tashu.get_stations()
            paths = duroonubi.get_bike_paths(36.350971, 127.385288)
            routes = daejeon.get_bike_routes()
            
            # 더미 데이터 반환 확인
            assert len(stations) == 3
            assert len(paths["bike_paths"]) == 2
            assert len(routes["routes"]) == 3


if __name__ == "__main__":
    pytest.main([__file__]) 