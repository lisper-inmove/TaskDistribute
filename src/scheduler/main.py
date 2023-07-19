import asyncio
import argparse
import signal

from scheduler.executor import Executor


def main():
    executor = Executor()
    signal.signal(signal.SIGUSR1, executor.signal_handler)
    asyncio.run(
        executor.run()
    )


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    main()
