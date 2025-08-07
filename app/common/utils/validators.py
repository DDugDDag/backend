# app/api/utils/validators.py
from typing import Any, Dict

def validate_coordinates(lat: float, lng: float) -> bool:
    if not isinstance(lat, (int, float)) or not isinstance(lng, (int, float)):
        return False
    if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
        return False
    return True

def normalize_coordinates(lat: float, lng: float) -> tuple:
    return round(float(lat), 6), round(float(lng), 6)

def safe_get(data: dict, *keys, default=None):
    if not isinstance(data, dict):
        return default
    for key in keys:
        try:
            if key in data and data[key] is not None:
                return data[key]
        except (TypeError, KeyError):
            continue
    return default

def validate_api_response(response_data: Any, required_fields: list) -> bool:
    if not isinstance(response_data, dict):
        return False
    for field in required_fields:
        if field not in response_data:
            return False
    return True
