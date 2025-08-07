# app/api/utils/standardizers.py
from app.common.utils.validators import safe_get, validate_coordinates, normalize_coordinates
from app.common.utils.exceptions import DataFormatException
import logging

logger = logging.getLogger(__name__)

def standardize_station_data(raw_data: dict) -> dict:
    try:
        lat = safe_get(raw_data, 'lat', default=0.0)
        lng = safe_get(raw_data, 'lng', default=0.0)
        if not validate_coordinates(lat, lng):
            raise DataFormatException(f"잘못된 좌표: lat={lat}, lng={lng}")
        lat, lng = normalize_coordinates(lat, lng)
        return {
            "station_id": safe_get(raw_data, 'station_id', default=''),
            "name": safe_get(raw_data, 'name', default=''),
            "address": safe_get(raw_data, 'address', default=''),
            "lat": lat,
            "lng": lng,
            "available_bikes": safe_get(raw_data, 'available_bikes', default=0),
            "total_docks": safe_get(raw_data, 'total_docks', default=0),
            "last_updated": safe_get(raw_data, 'last_updated', default='')
        }
    except Exception as e:
        logger.error(f"대여소 표준화 실패: {e}")
        raise DataFormatException(str(e))

def standardize_bike_path_data(raw_data: dict) -> dict:
    try:
        coordinates = safe_get(raw_data, 'coordinates', default=[])
        normalized_coords = []
        for coord in coordinates:
            lat = safe_get(coord, 'lat', default=0.0)
            lng = safe_get(coord, 'lng', default=0.0)
            if validate_coordinates(lat, lng):
                lat, lng = normalize_coordinates(lat, lng)
                normalized_coords.append({"lat": lat, "lng": lng})
        return {
            "path_id": safe_get(raw_data, 'path_id', default=''),
            "name": safe_get(raw_data, 'name', default=''),
            "length": safe_get(raw_data, 'length', default=0.0),
            "path_type": safe_get(raw_data, 'path_type', default=''),
            "coordinates": normalized_coords
        }
    except Exception as e:
        logger.error(f"자전거 도로 표준화 실패: {e}")
        raise DataFormatException(str(e))
