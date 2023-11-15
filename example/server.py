import asyncio
from lacia.core.core import JsonRpc
from lacia.core.proxy import ProxyObj
from lacia.network.server.aioserver import AioServer

class Test:

    def __init__(self, a, b) -> None:
        self.a = a
        self.b = b
    
    def output(self, name):
        return f"hello: {name}"

def class_sum(obj: Test):
    return obj.a + obj.b

async def test_async(n: int):
    print('test_async', n)
    await asyncio.sleep(n)
    return n*n

async def test_async_iter(n: int):
    for i in range(n):
        await asyncio.sleep(1)
        yield i

    

namespace = {
    "ping": lambda x: f"pong {x}",
    "test_async": test_async,
    "test_async_iter": test_async_iter,
    "class_sum": class_sum,
    "Test": Test,
}

rpc = JsonRpc(name = "server_test", namespace=namespace)

async def reverse_call(name: str):
    res = await ProxyObj(rpc, name=name).ping(name)
    return res

rpc.add_namespace({
    "reverse_call": reverse_call,
})

async def main():
    await rpc.run_server(AioServer(path="/ws"))

asyncio.run(main())