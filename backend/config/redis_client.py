import os
from redis import Redis
from rq import Queue

redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = int(os.getenv("REDIS_PORT", 6379))
redis_password = os.getenv("REDIS_PASSWORD", None)

redis_client = Redis(host=redis_host, port=redis_port, password=redis_password)
queue = Queue(connection=redis_client)