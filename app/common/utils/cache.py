# app/common/utils/cache.py
import redis
import pickle
import logging
from app.core.config import REDIS_URL

logger = logging.getLogger(__name__)

# Redis 클라이언트 초기화
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=False)
    # Redis 연결 테스트
    redis_client.ping()
    logger.info("✅ Redis 연결 성공")
except redis.exceptions.ConnectionError as e:
    logger.error(f"❌ Redis 연결 실패: {e}")
    redis_client = None

def get_cache(key: str):
    """
    Redis에서 캐시 데이터를 가져옵니다.
    """
    if redis_client:
        cached_data = redis_client.get(key)
        if cached_data:
            return pickle.loads(cached_data)
    return None

def set_cache(key: str, value, ex: int = 3600):
    """
    Redis에 데이터를 캐싱합니다.
    """
    if redis_client:
        serialized_data = pickle.dumps(value)
        redis_client.set(key, serialized_data, ex=ex)

def get_redis_client():
    return redis_client
