from msgq import Producer
from msgq import Consumer
from msgq import MsgConfig


def test():
    config = MsgConfig(MsgConfig.REDIS)
    config.host = "127.0.0.1"
    config.port = 6379
    config.stream_name = "test002"
    config.from_now_on = False
    config.block = 3

    producer = Producer().get_producer(config)
    consumer = Consumer().get_consumer(config)
    producer.push({"name": "inmove123"})
    print(consumer.pull(4))


if __name__ == '__main__':
    test()
