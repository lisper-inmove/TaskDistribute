import asyncio
from submodules.utils.logger import Logger

logger = Logger()


class Watcher:

    def __init__(self, executor):
        self.executor = executor

    async def start(self):
        while True:
            await asyncio.sleep(1)
            logger.info(f"Watcher {len(self.executor.actors)} tasks")
            for _, actor in self.executor.actors.items():
                print(actor.task)
