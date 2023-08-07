import asyncio
import aiohttp
import json
from asyncio import gather


async def send_post(session, i):
    await session.post(
        "http://127.0.0.1:8000/task/create",
        json={
            "templateId": "ca0465b0-26ea-4312-b12b-22133c782a37",
            "params": json.dumps({
                "applicationId": "29ac0602-80f6-4b7f-b2e9-8d33845b6cd5"
            }),
            "uniqueId": i
        }
    )

async def Produce():
    tasks = []
    async with aiohttp.ClientSession() as session:
        for i in range(0, 10):
            tasks.append(send_post(session, i))
        await asyncio.gather(*tasks)


async def main():
    await gather(
        Produce(),
    )


if __name__ == '__main__':
    asyncio.run(main())
