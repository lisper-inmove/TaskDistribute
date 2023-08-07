import asyncio
import aiohttp
import json
import signal

import proto.entities.task_pb2 as task_pb
from manager.task_manager import TaskManager
from manager.task_template_manager import TaskTemplateManager
from submodules.utils.logger import Logger
from submodules.utils.sys_env import SysEnv
from submodules.utils.idate import IDate
from submodules.utils.redis_lock import Redislock
from msgq.consumer import Consumer
from msgq.mq_config import MQConfig
from msgq.message import Message

logger = Logger()


class Actor:

    class Task:

        id: str
        addTime: int
        finishTime: int
        message: Message

        def __init__(self, **kargs):
            self.id = kargs.get("id")
            self.addTime = kargs.get("addTime")
            self.finishTime = kargs.get("finishTime")
            self.message = kargs.get("message")
            self.isFinished = False

        @property
        def finished(self):
            return self.isFinished

        @finished.setter
        def finished(self, isFinished):
            if not isFinished:
                return
            self.isFinished = isFinished
            self.finishTime = IDate.now_timestamp()

    def __init__(self, consumer):
        self.consumer = consumer
        self.tasks = {}

    def info(self, msg):
        logger.info(f"{self.consumer.config.groupName} -- {self.consumer.config.consumerName} -- {msg}")

    async def process(self):
        coros = []
        async for message in self.consumer.autoclaim(count=5):
            if message is None:
                continue
            coros.append(self.__process_message(message))
        async for message in self.consumer.pull(5):
            if message is None:
                continue
            coros.append(self.__process_message(message))
        for _, task in self.tasks.items():
            coros.append(self.__process_message(task.message))
        await asyncio.gather(*coros)

    async def __process_message(self, message):
        if message is None:
            return
        task = await self.parse_message(message)
        if not task:
            await self.consumer.ack(message)
            return True
        async with Redislock(task.id) as lock:
            if not lock:
                return
            if task.id not in self.tasks:
                self.tasks.update({
                    task.id: self.Task(
                        id=task.id,
                        addTime=IDate.now_timestamp(),
                        message=message
                    )
                })
            task.finished = await self.__process_message_without_lock(task)
            await self.__process_message_finish(task)

    async def __process_message_finish(self, task):
        if not task.finished:
            return
        taskManager = TaskManager()
        task.status = task_pb.Task.FINISHED
        await taskManager.update_task(task)
        self.info(f"{task.id} Set task finished: {task.finished}")
        await self.consumer.ack(task.message)
        if task.id in self.tasks:
            self.info(f"Remove task from self.tasks {task.id}")
            del self.tasks[task.id]

    async def __process_message_without_lock(self, task):
        flag = await self.check_prepose_status(task)
        self.info(f"{task.id} Check task prepose status: {flag}")
        if not flag:
            return False
        result = await self.set_task_finished(task)
        if not result:
            return False
        return True

    async def parse_message(self, message):
        if self.consumer.config.type == MQConfig.KAFKA:
            return await self.__parse_message_with_kafka(message)
        elif self.consumer.config.type in [
                MQConfig.REDIS,
                MQConfig.REDIS_CLUSTER,
        ]:
            return await self.__parse_message_with_redis(message)
        elif self.consumer.config.type == MQConfig.PULSAR:
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
        if not task:
            return True
        api = task.template.preposeStatusQueryApi
        params = json.loads(task.preposeParams)
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    api,
                    json=params,
                    timeout=30
                ) as response:
                    result = await response.json()
                    self.info(f"{task.id} Task prepose status: {result.get('code')} {result.get('msg')}")
                    if result.get("code") == 0 and result.get("msg") == "成功":
                        return True
            except TimeoutError as ex:
                logger.traceback(ex)
                return False
            except Exception as ex:
                logger.traceback(ex)
                return False
        return False

    async def set_task_finished(self, task):
        if not task:
            return True
        api = task.template.taskFinishSetApi
        params = json.loads(task.finishParams)
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    api,
                    json=params,
                    timeout=30
                ) as response:
                    result = await response.json()
                    self.info(f"{task.id} Set task finish: {result.get('code')} {result.get('msg')}")
                    if result.get("code") == 0 and result.get("msg") == "成功":
                        return True
            except TimeoutError as ex:
                logger.traceback(ex)
                return False
            except Exception as ex:
                logger.traceback(ex)
                return False
        return False


class Executor:

    SIGUSR1 = 1 << 0

    def __init__(self):
        self.actors = []
        self.signum = self.SIGUSR1

    async def run(self):
        await self.serve()

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
            if templateName and template.name != templateName:
                continue
            logger.info(f"Load TaskTemplate: {template.id} {template.name}")
            await self.__create_actors(template)
        self.signum &= ~self.SIGUSR1

    async def __create_actors(self, template):
        consumerRange = SysEnv.get("CONSUMER_RANGE", '0:1')
        consumerRange = consumerRange.split(':')
        coros = []
        for i in range(int(consumerRange[0]), int(consumerRange[1])):
            config = MQConfig(SysEnv.get("MQ_TYPE"))
            config.topic = template.id
            config.groupName = f"{template.id}-group"
            config.consumerName = f"{template.id}-consumer-{i}"
            config.partition = i
            coros.append(Consumer().get_consumer(config))
            logger.info(f"Create Consumer {config.topic} {config.groupName} {config.consumerName}")
        result = await asyncio.gather(*coros)
        for consumer in result:
            actor = Actor(consumer)
            self.actors.append(actor)

    async def serve(self):
        while True:
            await self.load_task_templates_handler()
            for actor in self.actors:
                await asyncio.sleep(0.05)
                await actor.process()
