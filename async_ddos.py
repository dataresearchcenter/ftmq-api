import asyncio

import requests
from codetiming import Timer

URL = "http://localhost:8000/entities?schema=Membership&nested=1&page={i}&limit=100"


async def task(i):
    with Timer(text=f"Page {i} elapsed time: {{:.1f}}"):
        res = requests.get(URL.format(i=i))
        assert res.ok


async def main():
    tasks = [asyncio.create_task(task(i)) for i in range(1, 100)]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
