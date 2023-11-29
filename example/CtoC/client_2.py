import asyncio
from lacia.core.core import JsonRpc
from lacia.core.proxy import ProxyObj
from lacia.network.client.aioclient import AioClient

async def test_async_iter(n: int):
    for i in range(n):
        await asyncio.sleep(1)
        yield i

namespace = {
    "ping": lambda x: f"pong {x}",
    "test_async_iter": test_async_iter,
}

rpc = JsonRpc(
    name="client_test_2",
    namespace=namespace
)

async def main():

    client = AioClient(path="/ws")
    await rpc.run_client(client)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.run_forever()