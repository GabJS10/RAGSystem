from config.redis_client import redis_client, queue
from rq import Worker


if __name__ == '__main__':
    worker = Worker([queue], connection=redis_client)
    worker.work()