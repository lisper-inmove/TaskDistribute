import random
import asyncio
from asyncio import gather
from multiprocessing import Process

from submodules.utils.redis_lock import redislock


async def Produce(name):
    print(f"{name} 尝试去获取锁")
    with redislock("my-test-lock", ttl=30, retryCount=10, retryDelay=0.2) as lock:
        if not lock:
            print(f"{name} 未获取到锁")
            return
        await asyncio.sleep(random.randint(1, 10) / 10)
        print(f"{name} 获取到锁,但是什么也不做")


def main():
    asyncio.run(Produce(random.randint(1, 1000)))


if __name__ == "__main__":
    processes = [Process(target=main) for _ in range(10)]
    for p in processes:
        p.start()
    for p in processes:
        p.join()
