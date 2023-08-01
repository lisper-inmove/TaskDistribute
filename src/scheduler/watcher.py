import asyncio
from submodules.utils.logger import Logger
from submodules.utils.idate import IDate

logger = Logger()


class Watcher:

    def __init__(self, executor):
        self.executor = executor

    async def start(self):
        while True:
            await asyncio.sleep(1)
            for actor in self.executor.actors:
                for _, task in actor.tasks.items():
                    logger.info(f"{task.id} {task.addTime} {IDate.now_timestamp() - task.addTime}")
