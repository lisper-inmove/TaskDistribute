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
                for _, job in actor.jobs.items():
                    logger.info(f"{job.id} {job.addTime} {IDate.now_timestamp() - job.addTime}")
