from redis import Redis
from rq import Queue

redis_client = Redis(host='redis', port=6379)
queue = Queue(connection=redis_client)