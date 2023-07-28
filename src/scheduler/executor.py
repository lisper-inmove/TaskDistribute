import asyncio
import aiohttp
import json
import time
import signal
import itertools

import proto.entities.task_pb2 as task_pb
from manager.task_manager import TaskManager
from manager.task_template_manager import TaskTemplateManager
from submodules.utils.logger import Logger
from submodules.utils.sys_env import SysEnv
from msgq.consumer import Consumer
from msgq.mq_config import MQConfig

logger = Logger()


class Actor:

    def __init__(self, task, consumer, message):
        self.task = task
        self.message = message
        self.consumer = consumer

    @property
    def is_finished(self):
        return self.task.status == task_pb.Task.FINISHED


class Executor:

    SIGUSR1 = 1 << 0

    def __init__(self):
        self.consumers = {}
        self.actors = {}
        self.signum = self.SIGUSR1

    def signal_handler(self, signum, frame):
        if signum == signal.SIGUSR1:
            self.signum |= self.SIGUSR1

    async def load_task_templates_handler(self):
        if not (self.signum & self.SIGUSR1):
            return
        manager = TaskTemplateManager()
        taskTemplates = manager.list_task_template()
        templateName = SysEnv.get('TEMPLATE_NAME')
        async for template in taskTemplates:
            if self.consumers.get(template.id):
                continue
            if templateName and template.name != templateName:
                continue
            logger.info(f"Load TaskTemplate: {template.id} {template.name}")
            consumers = await self.__create_consumers(template)
            self.consumers.update({
                template.id: consumers
            })
        self.signum &= ~self.SIGUSR1

    async def __create_consumers(self, template):
        consumerRange = SysEnv.get("CONSUMER_RANGE", '0:1')
        consumerRange = consumerRange.split(':')
        consumers = []
        for i in range(int(consumerRange[0]), int(consumerRange[1])):
            config = MQConfig(SysEnv.get("MQ_TYPE"))
            config.topic = template.id
            config.groupName = f"{template.id}-group"
            config.consumerName = f"{template.id}-consumer-{i}"
            config.partition = i
            consumer = Consumer().get_consumer(config)
            logger.info(f"Create Consumer {config.topic} {config.groupName} {config.consumerName}")
            consumers.append(consumer)
        consumers = await asyncio.gather(*consumers)
        return consumers

    async def run(self):
        await self.serve()

    async def serve(self):
        while True:
            await self.load_task_templates_handler()
            for _, consumers in self.consumers.items():
                await asyncio.sleep(0.05)
                tasks = [self.__process_per_consumer(consumer)
                         for consumer in consumers]
                await asyncio.gather(*tasks)

    async def __process_per_consumer(self, consumer):
        async for message in consumer.autoclaim():
            if not message:
                continue
            actor = await self.parse_message(consumer, message)
            self.actors.update({actor.task.id: actor})

        async for message in consumer.pull(10):
            if not message:
                continue
            logger.info(f"{consumer.config.consumerName} process start")
            if not message:
                continue
            actor = await self.parse_message(consumer, message)
            if actor.task is None:
                await actor.consumer.ack(actor.message)
                continue
            self.actors.update({actor.task.id: actor})
        coros = []
        for _, actor in self.actors.items():
            if actor.consumer is not consumer:
                continue
            coros.append(self.__process_task(actor, self.__task_finish))
        asyncio.gather(*coros)

    async def __task_finish(self, actor):
        if actor.is_finished:
            del self.actors[actor.task.id]
            await actor.consumer.ack(actor.message)
        logger.info(f"{actor.consumer.config.consumerName} process finished {actor.is_finished}")

    async def __process_task(self, actor, callback):
        if not actor:
            return True
        taskManager = TaskManager()
        flag = await self.check_prepose_status(actor.task)
        logger.info(f"{actor.task.id} Check task prepose status: {flag}")
        if not flag:
            return False
        result = await self.set_task_finished(actor.task)
        if not result:
            return False
        actor.task.status = task_pb.Task.FINISHED
        await taskManager.update_task(actor.task)
        logger.info(f"{actor.task.id} Set task finished: {result}")
        await callback(actor)
        return True

    async def parse_message(self, consumer, message):
        if consumer.config.type == MQConfig.KAFKA:
            task = await self.__parse_message_with_kafka(message)
        elif consumer.config.type == MQConfig.REDIS:
            task = await self.__parse_message_with_redis(message)
        elif consumer.config.type == MQConfig.PULSAR:
            task = await self.__parse_message_with_pulsar(message)
        return Actor(task, consumer, message)

    async def __parse_message_with_redis(self, message):
        message = message.value
        taskId = message[1].get(b'id').decode()
        manager = TaskManager()
        task = await manager.get_task_by_id(taskId)
        return task

    async def __parse_message_with_kafka(self, message):
        message = message.value.value
        message = json.loads(message.decode())
        manager = TaskManager()
        return await manager.get_task_by_id(message.get("id"))

    async def __parse_message_with_pulsar(self, message):
        message = message.value.value()
        message = json.loads(message.decode())
        manager = TaskManager()
        return await manager.get_task_by_id(message.get("id"))

    async def check_prepose_status(self, task):
        if not task:
            return True
        api = task.template.preposeStatusQueryApi
        params = json.loads(task.params)
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    api,
                    json=params,
                    timeout=30
                ) as response:
                    result = await response.json()
                    logger.info(f"{task.id} Task prepose status: {result.get('code')} {result.get('msg')}")
                    if result.get("code") == 0 and result.get("msg") == "成功":
                        return True
            except TimeoutError as ex:
                return False
        return False

    async def set_task_finished(self, task):
        if not task:
            return True
        api = task.template.taskFinishSetApi
        params = json.loads(task.params)
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    api,
                    json=params,
                    timeout=30
                ) as response:
                    result = await response.json()
                    logger.info(f"{task.id} Set task finish: {result.get('code')} {result.get('msg')}")
                    if result.get("code") == 0 and result.get("msg") == "成功":
                        return True
            except TimeoutError as ex:
                return False
        return False
