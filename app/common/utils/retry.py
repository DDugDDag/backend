# app/api/utils/retry.py
import time
import logging
from functools import wraps
import requests
from app.api.utils.exceptions import APIException

logger = logging.getLogger(__name__)

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (requests.RequestException, APIException) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt)
                        logger.warning(f"API 호출 실패 (시도 {attempt + 1}/{max_retries}): {e}. {wait_time}초 후 재시도...")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"모든 재시도 실패: {e}")
            raise last_exception
        return wrapper
    return decorator

def create_session_with_retry() -> requests.Session:
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry

    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"],
        backoff_factor=1
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session
