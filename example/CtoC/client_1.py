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
    name="client_test_1",
    namespace=namespace
)

async def main():

    client = AioClient(path="/ws")
    await rpc.run_client(client)

    c_obj = ProxyObj(rpc, "client_test_2")
    s_obj = ProxyObj(rpc)

    async for i in s_obj.test_async_iter(10):
        print(i)
    
    async for i in c_obj.test_async_iter(10):
        print(i)
    
    print(await s_obj.ping(c_obj.ping("hello")))
    print(await c_obj.ping(s_obj.ping("hello")))


loop = asyncio.get_event_loop()
loop.run_until_complete(main())