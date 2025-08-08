# back\tests\test_external_apis.py
import pytest
import unittest.mock as mock
from unittest.mock import Mock, patch, MagicMock
import httpx
from datetime import datetime

from app.services.external.external_api import TashuAPI, DuroonubiAPI, DaejeonBikeAPI
from app.common.utils.exceptions import APIException, NetworkException, AuthenticationException, DataFormatException

# httpx.AsyncClient를 모의(Mock)하기 위한 패치 경로
HTTPX_CLIENT_PATH = 'app.services.external.external_api.httpx.AsyncClient'


class TestTashuAPI:
    """타슈 API 테스트"""

    @patch(HTTPX_CLIENT_PATH)
    async def test_get_stations_success(self, mock_httpx_client):
        """타슈 대여소 조회 성공 테스트"""
        mock_response_data = {
            "stations": [{
                "id": "ST001", "name": "테스트 대여소", "address": "테스트 주소",
                "latitude": 36.332612, "longitude": 127.434732,
                "available_bikes": 5, "total_docks": 10
            }]
        }
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = mock_response_data
        
        mock_httpx_client.return_value.__aenter__.return_value.get.return_value = mock_response
        
        tashu_api = TashuAPI(api_key="test_api_key")
        result = await tashu_api.get_stations()
        
        assert len(result) == 1
        assert result[0]["station_id"] == "ST001"

    @patch(HTTPX_CLIENT_PATH)
    async def test_get_stations_network_error_fallback(self, mock_httpx_client):
        """타슈 대여소 조회 네트워크 오류 시 더미 데이터 반환 테스트"""
        mock_httpx_client.return_value.__aenter__.return_value.get.side_effect = httpx.RequestError("Connection failed")
        
        tashu_api = TashuAPI(api_key="test_api_key")
        result = await tashu_api.get_stations()
        
        assert len(result) == 3

    @patch(HTTPX_CLIENT_PATH)
    async def test_get_stations_auth_error(self, mock_httpx_client):
        """타슈 대여소 조회 인증 오류 테스트"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError("Auth Error", request=Mock(), response=mock_response)
        mock_response.status_code = 401
        
        mock_httpx_client.return_value.__aenter__.return_value.get.return_value = mock_response
        
        tashu_api = TashuAPI(api_key="test_api_key")
        with pytest.raises(AuthenticationException):
            await tashu_api.get_stations()

    @patch(HTTPX_CLIENT_PATH)
    async def test_get_station_status_success(self, mock_httpx_client):
        """타슈 대여소 상태 조회 성공 테스트"""
        mock_response_data = {"station_id": "ST001", "available_bikes": 7, "total_docks": 12, "last_updated": "2023-05-15T14:30:00Z"}
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = mock_response_data
        
        mock_httpx_client.return_value.__aenter__.return_value.get.return_value = mock_response
        
        tashu_api = TashuAPI(api_key="test_api_key")
        result = await tashu_api.get_station_status("ST001")
        
        assert result["station_id"] == "ST001"
        assert result["available_bikes"] == 7
        assert result["total_docks"] == 12

    @patch(HTTPX_CLIENT_PATH)
    async def test_no_api_key(self, mock_httpx_client):
        """API 키 없이 초기화 테스트"""
        api = TashuAPI(api_key="")
        result = await api.get_stations()
        
        assert len(result) == 3


class TestDuroonubiAPI:
    """두루누비 API 테스트"""
    
    @patch(HTTPX_CLIENT_PATH)
    async def test_get_bike_paths_success(self, mock_httpx_client):
        """두루누비 자전거 도로 조회 성공 테스트"""
        mock_response_data = {
            "bike_paths": [{"path_id": "P001", "name": "테스트 자전거도로", "length": 5.2, "path_type": "전용도로", "coordinates": []}]
        }
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = mock_response_data
        
        mock_httpx_client.return_value.__aenter__.return_value.get.return_value = mock_response
        
        duroonubi_api = DuroonubiAPI(api_key="test_api_key")
        result = await duroonubi_api.get_bike_paths(36.350971, 127.385288)
        
        assert "bike_paths" in result
        assert len(result["bike_paths"]) == 1

    @patch(HTTPX_CLIENT_PATH)
    async def test_invalid_coordinates(self, mock_httpx_client):
        """잘못된 좌표 입력 테스트"""
        duroonubi_api = DuroonubiAPI(api_key="test_api_key")
        with pytest.raises(DataFormatException):
            await duroonubi_api.get_bike_paths(91.0, 127.385288)

    @patch(HTTPX_CLIENT_PATH)
    async def test_network_error_fallback(self, mock_httpx_client):
        """두루누비 네트워크 오류 시 더미 데이터 반환 테스트"""
        mock_httpx_client.return_value.__aenter__.return_value.get.side_effect = httpx.RequestError("Connection failed")
        
        duroonubi_api = DuroonubiAPI(api_key="test_api_key")
        result = await duroonubi_api.get_bike_paths(36.350971, 127.385288)
        
        assert "bike_paths" in result
        assert len(result["bike_paths"]) == 2


class TestDaejeonBikeAPI:
    """대전 자전거 API 테스트"""
    
    @patch(HTTPX_CLIENT_PATH)
    async def test_get_bike_routes_success(self, mock_httpx_client):
        """대전 자전거 노선 조회 성공 테스트"""
        mock_response_data = {"routes": [{"route_id": "R001", "name": "테스트 자전거길", "length": 15.3, "difficulty": "쉬움", "description": "테스트용"}]}
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = mock_response_data
        
        mock_httpx_client.return_value.__aenter__.return_value.get.return_value = mock_response
        
        daejeon_api = DaejeonBikeAPI(api_key="test_api_key")
        result = await daejeon_api.get_bike_routes()
        
        assert "routes" in result
        assert len(result["routes"]) == 1

    @patch(HTTPX_CLIENT_PATH)
    async def test_network_error_fallback(self, mock_httpx_client):
        """대전 자전거 API 네트워크 오류 시 더미 데이터 반환 테스트"""
        mock_httpx_client.return_value.__aenter__.return_value.get.side_effect = httpx.RequestError("Connection failed")
        
        daejeon_api = DaejeonBikeAPI(api_key="test_api_key")
        result = await daejeon_api.get_bike_routes()
        
        assert "routes" in result
        assert len(result["routes"]) == 3


class TestIntegration:
    """통합 테스트"""
    
    @patch(HTTPX_CLIENT_PATH)
    async def test_all_apis_integration(self, mock_httpx_client):
        """모든 API 통합 테스트 (더미 데이터)"""
        # ... (로직 수정)
        
        # Mocking 로직은 위 개별 테스트와 유사하게 구성
        
        # 실제 httpx.get() 호출이 없도록 Mocking
        mock_httpx_client.return_value.__aenter__.return_value.get.side_effect = httpx.RequestError("Connection failed")

        tashu = TashuAPI(api_key="test_key")
        duroonubi = DuroonubiAPI(api_key="test_key")
        daejeon = DaejeonBikeAPI(api_key="test_key")
        
        stations = await tashu.get_stations()
        paths = await duroonubi.get_bike_paths(36.350971, 127.385288)
        routes = await daejeon.get_bike_routes()
        
        assert isinstance(stations, list)
        assert len(stations) > 0
        
        assert isinstance(paths, dict)
        assert "bike_paths" in paths
        
        assert isinstance(routes, dict)
        assert "routes" in routes


    @patch(HTTPX_CLIENT_PATH)
    async def test_error_handling_integration(self, mock_httpx_client):
        """오류 처리 통합 테스트"""
        mock_httpx_client.return_value.__aenter__.return_value.get.side_effect = httpx.RequestError("Connection failed")
        
        tashu = TashuAPI(api_key="test_key")
        duroonubi = DuroonubiAPI(api_key="test_key")
        daejeon = DaejeonBikeAPI(api_key="test_key")
        
        stations = await tashu.get_stations()
        paths = await duroonubi.get_bike_paths(36.350971, 127.385288)
        routes = await daejeon.get_bike_routes()
        
        assert len(stations) == 3
        assert len(paths["bike_paths"]) == 2
        assert len(routes["routes"]) == 3
