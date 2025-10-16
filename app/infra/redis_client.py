import redis
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

password = REDIS_PASSWORD if REDIS_PASSWORD else None

pool = redis.ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=password,
    decode_responses=True,
    max_connections=10,
)

redis_client = redis.Redis(connection_pool=pool)
