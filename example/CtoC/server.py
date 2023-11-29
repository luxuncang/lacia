import asyncio
from lacia.core.core import JsonRpc, Context
from lacia.core.proxy import ProxyObj
from lacia.network.server.aioserver import AioServer

def get_proxyobj(name: str):
    rpc = Context.rpc.get()
    return ProxyObj(rpc, name)

async def run_obj(obj: ProxyObj):
    return await obj

async def test_async_iter(n: int):
    name = Context.name.get()
    obj = ProxyObj(Context.rpc.get(), name)
    async for i in obj.test_async_iter(n):
        yield i

namespace = {
    "ping": lambda x: f"pong {x}",
    "get_proxyobj": get_proxyobj,
    "run_obj": run_obj,
    "test_async_iter": test_async_iter,
}


rpc = JsonRpc(name = "server_test", namespace=namespace)

async def main():
    await rpc.run_server(AioServer(path="/ws"))

asyncio.run(main())