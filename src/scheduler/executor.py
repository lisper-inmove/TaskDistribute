import asyncio
import aiohttp
import json
import time
import signal

import proto.entities.task_pb2 as task_pb
from manager.task_manager import TaskManager
from manager.task_template_manager import TaskTemplateManager
from submodules.utils.logger import Logger
from submodules.utils.sys_env import SysEnv
from msgq.consumer import Consumer
from msgq.mq_config import MQConfig

logger = Logger()


class Executor:

    SIGUSR1 = 1 << 0

    def __init__(self):
        self.consumers = {}
        self.load_task_templates_time = 0
        self.signum = self.SIGUSR1

    def signal_handler(self, signum, frame):
        if signum == signal.SIGUSR1:
            self.signum |= self.SIGUSR1

    async def load_task_templates_handler(self):
        if not (self.signum & self.SIGUSR1):
            return
        self.load_task_templates_time = time.time()
        manager = TaskTemplateManager()
        taskTemplates = manager.list_task_template()
        async for template in taskTemplates:
            if self.consumers.get(template.id):
                continue
            config = MQConfig(SysEnv.get("MQ_TYPE"))
            config.isAsync = True
            config.topic = template.id
            config.groupName = f"{template.id}-group"
            config.consumerName = f"{template.id}-consumer"
            logger.info(f"Load TaskTemplate: {template.id} {template.name}")
            self.consumers.update({
                template.id: Consumer().get_consumer(config)
            })
        self.signum &= ~self.SIGUSR1

    async def run(self):
        await self.load_from_db()
        await self.run_as_consumer()

    async def load_from_db(self):
        taskManager = TaskManager()
        async for task in taskManager.list_created_task():
            await self.__process_task(task)

    async def run_as_consumer(self):
        while True:
            await self.load_task_templates_handler()
            for _, consumer in self.consumers.items():
                await asyncio.sleep(0.1)
                async for message in consumer.pull(10):
                    if not message:
                        continue
                    task = await self.parse_message(consumer, message)
                    flag = await self.__process_task(task)
                    if flag:
                        await consumer.ack(message)

    async def __process_task(self, task):
        taskManager = TaskManager()
        flag = await self.check_prepose_status(task)
        logger.info(f"Check task {task.id} prepose status: {flag}")
        if not flag:
            return False
        result = await self.set_task_finished(task)
        if not result:
            return False
        task.status = task_pb.Task.FINISHED
        await taskManager.update_task(task)
        logger.info(f"Set task {task.id} finished: {result}")
        return True

    async def parse_message(self, consumer, message):
        if consumer.config.type == MQConfig.KAFKA:
            return await self.__parse_message_with_kafka(message)
        elif consumer.config.type == MQConfig.REDIS:
            return await self.__parse_message_with_redis(message)
        elif consumer.config.type == MQConfig.PULSAR:
            return await self.__parse_message_with_pulsar(message)

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
                    logger.info(f"Task prepose status: {result}")
                    if result.get("code") == 0 and result.get("msg") == "成功":
                        return False
            except TimeoutError as ex:
                return False
        return False

    async def set_task_finished(self, task):
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
                    logger.info(f"Set task finish: {result}")
                    if result.get("code") == 0 and result.get("msg") == "成功":
                        return True
            except TimeoutError as ex:
                return False
        return False
