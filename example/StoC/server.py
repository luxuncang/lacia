import asyncio
import builtins

from aiohttp import web

from lacia.core.core import JsonRpc, Context
from lacia.network.server.aioserver import AioServer

async def get_ws():
    ws = Context.websocket.get()
    assert isinstance(ws, web.WebSocketResponse)
    return ws

namespace = {
    "get_ws": get_ws,
    "remote_builtins": builtins
}

rpc = JsonRpc(name = "server_test", namespace=namespace)

async def main():
    await rpc.run_server(AioServer(path="/ws"))

asyncio.run(main())
