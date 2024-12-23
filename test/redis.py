import redis

# Redis 연결
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# Redis 연결 확인
try:
    redis_client.ping()
    print("Redis 연결 성공!")
except Exception as e:
    print(f"Redis 연결 실패: {e}")