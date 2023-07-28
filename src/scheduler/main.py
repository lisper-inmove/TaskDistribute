import asyncio
import argparse
import signal

from scheduler.executor import Executor
from scheduler.watcher import Watcher


async def main():
    executor = Executor()
    watcher = Watcher(executor)
    signal.signal(signal.SIGUSR1, executor.signal_handler)
    await asyncio.gather(
        executor.run(), watcher.start()
    )


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    asyncio.run(main())
