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

    class Job:

        def __init__(self, task: task_pb.Task, message: Message):
            self.task = task
            self.message = message
            self.addTime = IDate.now_timestamp()
            self.isFinished = False

        @property
        def id(self):
            return self.task.id

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
        self.jobs = {}

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
        for _, task in self.jobs.items():
            coros.append(self.__process_message(task.message))
        await asyncio.gather(*coros)

    async def __process_message(self, message):
        if message is None:
            return
        job = await self.parse_message(message)
        if not job:
            await self.consumer.ack(message)
            return True
        async with Redislock(job.id) as lock:
            if not lock:
                return
            job.finished = await self.__process_message_without_lock(job)
            await self.__process_message_finish(job)

    async def __process_message_finish(self, job):
        if not job.finished:
            return
        taskManager = TaskManager()
        job.task.status = task_pb.Task.FINISHED
        await taskManager.update_task(job.task)
        self.info(f"{job.id} Set task finished: {job.finished}")
        await self.consumer.ack(job.message)
        if job.id in self.jobs:
            self.info(f"Remove task from self.jobs {job.id}")
            del self.jobs[job.id]

    async def __process_message_without_lock(self, job):
        flag = await self.check_prepose_status(job)
        self.info(f"{job.id} Check task prepose status: {flag}")
        if not flag:
            return False
        result = await self.set_task_finished(job)
        if not result:
            return False
        return True

    async def parse_message(self, message):
        if self.consumer.config.type == MQConfig.KAFKA:
            task = await self.__parse_message_with_kafka(message)
        elif self.consumer.config.type in [
                MQConfig.REDIS,
                MQConfig.REDIS_CLUSTER,
        ]:
            task = await self.__parse_message_with_redis(message)
        elif self.consumer.config.type == MQConfig.PULSAR:
            task = await self.__parse_message_with_pulsar(message)
        return self.Job(task, message)

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

    async def check_prepose_status(self, job):
        if not job:
            return True
        task = job.task
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
                    successAssert = self.success_assert(result, task)
                    if successAssert is not None:
                        return successAssert
                    if result.get("code") == 0 and result.get("msg") == "成功":
                        return True
            except TimeoutError as ex:
                logger.traceback(ex)
                return False
            except Exception as ex:
                logger.traceback(ex)
                return False
        return False

    async def set_task_finished(self, job):
        if not job:
            return True
        task = job.task
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
                    successAssert = self.success_assert(result, task)
                    if successAssert is not None:
                        return successAssert
                    if result.get("code") == 0 and result.get("msg") == "成功":
                        return True
            except TimeoutError as ex:
                logger.traceback(ex)
                return False
            except Exception as ex:
                logger.traceback(ex)
                return False
        return False

    def success_assert(self, result, task):
        if task.template.successAssert == "":
            return None
        successAssert = json.loads(task.template.successAssert)
        for key, value in successAssert.items():
            if task.get(key) != value:
                return False
        return True


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
