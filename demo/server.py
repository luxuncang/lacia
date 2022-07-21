import asyncio
from lacia import JsonRpc, AioServer, __version__

class number:

    def __init__(self) -> None:
        self.value = 0
    
    def add(self, i: int):
        self.value += i
        return self

    def sub(self, i: int):
        self.value -= i
        return self

async def async_generator(i = 10):
    for i in range(i):
        await asyncio.sleep(0.5)
        yield i

expose = {
    'add': lambda a, b: a + b,
    'sub': lambda a, b: a - b,
    'value': f'PyJsonRpc Server {__version__}',
    'number': number,
    'async_generator': async_generator,
}

loop = asyncio.new_event_loop()

rpc = JsonRpc('/test', namespace=expose, loop=loop, debug=True)

async def repeat():
    return await rpc.value
    # ws = rpc._server.active_connections[0]
    # res = await rpc.send_request_server(rpc.value, ws[0])
    # return res

rpc.add_namespace('repeat', repeat)

rpc.generate_pyi('CustomSchema') # Generate Pyi file

rpc.run_server(AioServer())
