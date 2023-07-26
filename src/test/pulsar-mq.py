import asyncio
import aiohttp
import random
from asyncio import gather

from msgq.mq_config import MQConfig
from msgq import Producer as mP
from msgq import Consumer as mC

def create_config():
    config = MQConfig(MQConfig.PULSAR)
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
    await p.cleanup()


async def Consumer(suffix):
    config = create_config()
    config.consumerName = f"{config.consumerName}-{suffix}"
    c = mC().get_consumer(config)
    for i in range(0, 30):
        await asyncio.sleep(0.5)
        async for msg in c.pull(10):
            print(f"Consume-{suffix} >> {msg.value}")
            await c.ack(msg)
    await c.cleanup()


async def main():
    await gather(
        Producer(),
        Consumer(11),
        Consumer(22),
    )


if __name__ == '__main__':
    asyncio.run(main())
