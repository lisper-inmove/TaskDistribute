import asyncio

from scheduler.executor import run


def main():
    asyncio.run(run())


if __name__ == '__main__':
    main()
