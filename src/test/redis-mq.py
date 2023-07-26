import asyncio
import aiohttp
import random
from asyncio import gather

from msgq.mq_config import MQConfig
from msgq import Producer as mP
from msgq import Consumer as mC
from msgq import GroupConsumer as mGC

def create_config():
    config = MQConfig(MQConfig.REDIS)
    config.topic = "ca0465b0-26ea-4312-b12b-22133c782a37"
    config.groupName = "my_group_name"
    config.consumerName = "my_consumer_name"
    return config


async def Producer():
    config = create_config()
    p = mP().get_producer(config)
    r = random.randint(1, 1000)
    for i in range(0, 30):
        await asyncio.sleep(random.randint(1, 5) / 10)
        await p.push({f"test-{i}-{r}": f"hello-{i}-{r}"})


async def Consumer():
    config = create_config()
    c = mC().get_consumer(config)
    for i in range(0, 30):
        await asyncio.sleep(0.5)
        async for msg in c.pull(10):
            print(f"Consume >> {msg.value}")
            await c.ack(msg)


async def GroupConsumer(suffix):
    config = create_config()
    config.consumerName = f"{config.consumerName}-{suffix}"
    gc = mGC().get_group_consumer(config)
    await gc.create_group()
    for i in range(0, 30):
        await asyncio.sleep(0.5)
        async for msg in gc.pull(10):
            print(f"GroupConsume-{suffix} >> {msg.value}")
            await gc.ack(msg)


async def main():
    await gather(
        Producer(),
        Consumer(),
        GroupConsumer(1),
        GroupConsumer(2),
        GroupConsumer(3),
    )


if __name__ == '__main__':
    asyncio.run(main())
