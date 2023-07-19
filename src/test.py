import asyncio
from msgq import Producer
from msgq import Consumer
from msgq import GroupConsumer
from msgq import MsgConfig


async def test():
    config = MsgConfig(MsgConfig.REDIS)
    config.host = "127.0.0.1"
    config.port = 6379
    config.stream_name = "test003"
    config.from_now_on = True
    config.block = 3
    config.isAsync = True
    config.group_name = "group003"
    config.consumer_name = "consumer003"

    producer = Producer().get_producer(config)
    consumer = Consumer().get_consumer(config)
    groupConsumer = GroupConsumer().get_group_consumer(config)
    await groupConsumer.create_group()
    await producer.push({"name": "inmove123"})
    async for message in consumer.pull(4):
        print(message)
    async for message in groupConsumer.pull(3):
        print(message)
    print(await groupConsumer.pendings())
    async for message in groupConsumer.pending_range():
        print(message)
        # await groupConsumer.claim([message.get("message_id")])


if __name__ == '__main__':
    asyncio.run(test())
