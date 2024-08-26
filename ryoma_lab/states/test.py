import asyncio
import types


async def helper9():
    await hello_world_message()


async def hello_world_message() -> str:
    await asyncio.sleep(1)
    return "Hello, world!"


async def main() -> None:
    message = await helper9()
    print(message)


asyncio.run(main())
