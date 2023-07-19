import asyncio
import aiohttp
import json

import proto.entities.task_pb2 as task_pb
from manager.task_manager import TaskManager
from submodules.utils.logger import Logger
from msgq.consumer import Consumer

logger = Logger()


async def run():
    taskManager = TaskManager()
    while True:
        await asyncio.sleep(1)
        async for task in taskManager.list_created_task():
            flag = await check_prepose_status(task)
            logger.info(f"Check task {task.id} prepose status: {flag}")
            if not flag:
                continue
            result = await set_task_finished(task)
            task.status = task_pb.Task.FINISHED
            await taskManager.update_task(task)
            logger.info(f"Set task {task.id} finished: {result}")


async def check_prepose_status(task):
    api = task.template.preposeStatusQueryApi
    params = json.loads(task.params)
    async with aiohttp.ClientSession() as session:
        async with session.post(
                api,
                json=params
        ) as response:
            result = await response.json()
            logger.info(f"Task prepose status: {result}")
            if result.get("code") == 0 and result.get("msg") == "成功":
                return True
    return False


async def set_task_finished(task):
    api = task.template.taskFinishSetApi
    params = json.loads(task.params)
    async with aiohttp.ClientSession() as session:
        async with session.post(
                api,
                json=params
        ) as response:
            result = await response.json()
            logger.info(f"Set task finish: {result}")
            if result.get("code") == 0 and result.get("msg") == "成功":
                return True
    return False
