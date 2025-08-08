# back\tests\test_external_apis.py

import pytest
from unittest.mock import Mock, patch
import httpx
import asyncio
from datetime import datetime
from app.services.external.external_api import TashuAPI, DuroonubiAPI, DaejeonBikeAPI
from app.common.utils.exceptions import APIException, NetworkException, AuthenticationException, DataFormatException
from typing import List, Dict, Any

# httpx.AsyncClient를 Mocking하기 위한 패치 경로
HTTPX_CLIENT_PATH = 'app.services.external.external_api.httpx.AsyncClient'

# 공통 Mocking 함수
def setup_mock_client(mock_httpx_client: Mock, status_code: int = 200, json_data: Any = None, side_effect: Any = None):
    """httpx.AsyncClient의 응답을 설정하는 공통 함수"""
    mock_response = Mock()
    mock_response.status_code = status_code
    if json_data is not None:
        mock_response.json.return_value = json_data
    if status_code >= 400:
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "HTTP Error", request=Mock(), response=mock_response
        )
    else:
        mock_response.raise_for_status.return_value = None

    mock_client_instance = mock_httpx_client.return_value.__aenter__.return_value
    if side_effect:
        mock_client_instance.get.side_effect = side_effect
    else:
        mock_client_instance.get.return_value = mock_response

class TestTashuAPI:
    """타슈 API 테스트"""

    @pytest.mark.asyncio
    @patch(HTTPX_CLIENT_PATH)
    async def test_get_stations_success(self, mock_httpx_client):
        """타슈 대여소 조회 성공 테스트"""
        mock_response_data = {"stations": [{"id": "ST001", "name": "테스트 대여소", "latitude": 36.332612, "longitude": 127.434732, "available_bikes": 5, "total_docks": 10}]}
        setup_mock_client(mock_httpx_client, json_data=mock_response_data)
        
        tashu_api = TashuAPI(api_key="test_api_key")
        result = await tashu_api.get_stations()
        
        assert len(result) == 1
        assert result[0]["station_id"] == "ST001"

    @pytest.mark.asyncio
    @patch(HTTPX_CLIENT_PATH)
    async def test_get_stations_network_error_fallback(self, mock_httpx_client):
        """타슈 대여소 조회 네트워크 오류 시 더미 데이터 반환 테스트"""
        setup_mock_client(mock_httpx_client, side_effect=httpx.RequestError("Connection failed"))
        
        tashu_api = TashuAPI(api_key="test_api_key")
        result = await tashu_api.get_stations()
        
        assert len(result) == 3

    @pytest.mark.asyncio
    @patch(HTTPX_CLIENT_PATH)
    async def test_get_stations_auth_error(self, mock_httpx_client):
        """타슈 대여소 조회 인증 오류 테스트"""
        setup_mock_client(mock_httpx_client, status_code=401)
        
        tashu_api = TashuAPI(api_key="test_api_key")
        with pytest.raises(AuthenticationException):
            await tashu_api.get_stations()

    @pytest.mark.asyncio
    @patch(HTTPX_CLIENT_PATH)
    async def test_get_station_status_success(self, mock_httpx_client):
        """타슈 대여소 상태 조회 성공 테스트"""
        mock_response_data = {"station_id": "ST001", "available_bikes": 7, "total_docks": 12}
        setup_mock_client(mock_httpx_client, json_data=mock_response_data)
        
        tashu_api = TashuAPI(api_key="test_api_key")
        result = await tashu_api.get_station_status("ST001")
        
        assert result["station_id"] == "ST001"
        assert result["available_bikes"] == 7
        assert result["total_docks"] == 12

    @pytest.mark.asyncio
    @patch(HTTPX_CLIENT_PATH)
    async def test_no_api_key(self, mock_httpx_client):
        """API 키 없이 초기화 테스트"""
        api = TashuAPI(api_key="")
        result = await api.get_stations()
        
        assert len(result) == 3


class TestDuroonubiAPI:
    """두루누비 API 테스트"""
    
    @pytest.mark.asyncio
    @patch(HTTPX_CLIENT_PATH)
    async def test_get_bike_paths_success(self, mock_httpx_client):
        """두루누비 자전거 도로 조회 성공 테스트"""
        mock_response_data = {"bike_paths": [{"path_id": "P001", "name": "테스트", "length": 5.2, "path_type": "전용", "coordinates": []}]}
        setup_mock_client(mock_httpx_client, json_data=mock_response_data)
        
        duroonubi_api = DuroonubiAPI(api_key="test_api_key")
        result = await duroonubi_api.get_bike_paths(36.35, 127.38)
        
        assert "bike_paths" in result
        assert len(result["bike_paths"]) == 1

    @pytest.mark.asyncio
    @patch(HTTPX_CLIENT_PATH)
    async def test_invalid_coordinates(self, mock_httpx_client):
        """잘못된 좌표 입력 테스트"""
        duroonubi_api = DuroonubiAPI(api_key="test_api_key")
        with pytest.raises(DataFormatException):
            await duroonubi_api.get_bike_paths(91.0, 127.38)

    @pytest.mark.asyncio
    @patch(HTTPX_CLIENT_PATH)
    async def test_network_error_fallback(self, mock_httpx_client):
        """두루누비 네트워크 오류 시 더미 데이터 반환 테스트"""
        setup_mock_client(mock_httpx_client, side_effect=httpx.RequestError("Connection failed"))
        
        duroonubi_api = DuroonubiAPI(api_key="test_api_key")
        result = await duroonubi_api.get_bike_paths(36.35, 127.38)
        
        assert "bike_paths" in result
        assert len(result["bike_paths"]) == 2


class TestDaejeonBikeAPI:
    """대전 자전거 API 테스트"""
    
    @pytest.mark.asyncio
    @patch(HTTPX_CLIENT_PATH)
    async def test_get_bike_routes_success(self, mock_httpx_client):
        """대전 자전거 노선 조회 성공 테스트"""
        mock_response_data = {"routes": [{"route_id": "R001", "name": "테스트", "length": 15.3, "difficulty": "쉬움", "description": "테스트"}]}
        setup_mock_client(mock_httpx_client, json_data=mock_response_data)
        
        daejeon_api = DaejeonBikeAPI(api_key="test_api_key")
        result = await daejeon_api.get_bike_routes()
        
        assert "routes" in result
        assert len(result["routes"]) == 1

    @pytest.mark.asyncio
    @patch(HTTPX_CLIENT_PATH)
    async def test_network_error_fallback(self, mock_httpx_client):
        """대전 자전거 API 네트워크 오류 시 더미 데이터 반환 테스트"""
        setup_mock_client(mock_httpx_client, side_effect=httpx.RequestError("Connection failed"))
        
        daejeon_api = DaejeonBikeAPI(api_key="test_api_key")
        result = await daejeon_api.get_bike_routes()
        
        assert "routes" in result
        assert len(result["routes"]) == 3


class TestIntegration:
    """통합 테스트"""
    
    @pytest.mark.asyncio
    @patch(HTTPX_CLIENT_PATH)
    async def test_all_apis_integration(self, mock_httpx_client):
        """모든 API 통합 테스트 (더미 데이터)"""
        # API 키가 없으므로 모두 더미 데이터를 반환
        tashu = TashuAPI(api_key="")
        duroonubi = DuroonubiAPI(api_key="")
        daejeon = DaejeonBikeAPI(api_key="")
        
        stations, paths, routes = await asyncio.gather(
            tashu.get_stations(),
            duroonubi.get_bike_paths(36.35, 127.38),
            daejeon.get_bike_routes()
        )
        
        assert isinstance(stations, list) and len(stations) > 0
        assert isinstance(paths, dict) and "bike_paths" in paths
        assert isinstance(routes, dict) and "routes" in routes


    @pytest.mark.asyncio
    @patch(HTTPX_CLIENT_PATH)
    async def test_error_handling_integration(self, mock_httpx_client):
        """오류 처리 통합 테스트"""
        # 네트워크 오류 발생 시뮬레이션
        setup_mock_client(mock_httpx_client, side_effect=httpx.RequestError("Connection failed"))
        
        tashu = TashuAPI(api_key="test_key")
        duroonubi = DuroonubiAPI(api_key="test_key")
        daejeon = DaejeonBikeAPI(api_key="test_key")
        
        stations = await tashu.get_stations()
        paths = await duroonubi.get_bike_paths(36.35, 127.38)
        routes = await daejeon.get_bike_routes()
        
        assert len(stations) == 3
        assert len(paths["bike_paths"]) == 2
        assert len(routes["routes"]) == 3
