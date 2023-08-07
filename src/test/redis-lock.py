import random
import asyncio
from asyncio import gather
from multiprocessing import Process

from submodules.utils.redis_lock import Redislock


async def Produce(name):
    print(f"{name} 尝试去获取锁")
    async with Redislock("my-test-lock", ttl=30, retryCount=10, retryDelay=0.2) as lock:
        if not lock:
            print(f"{name} 未获取到锁")
            return
        await asyncio.sleep(random.randint(1, 10) / 10)
        print(f"{name} 获取到锁,但是什么也不做")


async def main():
    coros = []
    for i in range(0, 2):
        coros.append(Produce(i))
    asyncio.gather(
        *coros
    )


if __name__ == "__main__":
    asyncio.run(main())
