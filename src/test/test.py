import asyncio
import aiohttp
import random

from msgq.mq_config import MQConfig


async def test():
    async with aiohttp.ClientSession() as session:
        async with session.post(
                "http://127.0.0.1:8000/task/create",
                json={
                    "templateId": "ca0465b0-26ea-4312-b12b-22133c782a37",
                    "params": '{"applicationId":"29ac0602-80f6-4b7f-b2e9-8d33845b6cd5"}',
                    "uniqueId": str(random.randint(1000000, 9999999))
                }
        ) as response:
            print(await response.json())


async def kafka_producer_test():

    from msgq import Producer
    from msgq import Consumer

    config = MQConfig(MsgConfig.KAFKA)
    config.topic = "ca0465b0-26ea-4312-b12b-22133c782a37"
    config.groupName = "my_group_name"

    p = Producer().get_producer(config)
    await p.push({"test": "hello"})

    c = Consumer().get_consumer(config)
    async for msg in c.pull(10):
        print(msg)


if __name__ == '__main__':
    # asyncio.run(test())
    asyncio.run(kafka_producer_test())
