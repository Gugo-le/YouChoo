import redis

# Redis 클라이언트 설정
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# 데이터 확인
def get_redis_data():
    try:
        rankings = redis_client.zrevrange("text_rankings", 0, -1, withscores=True)
        for rank, (text, score) in enumerate(rankings, start=1):
            print(f"Rank {rank}: {text}, Similarity: {score}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_redis_data()