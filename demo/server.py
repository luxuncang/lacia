import asyncio
from lacia import JsonRpc, AioServer, __version__

class Number:

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
    'Number': Number,
    'async_generator': async_generator,
}

loop = asyncio.new_event_loop()

rpc = JsonRpc('/test', namespace=expose, loop=loop, debug=True)

async def repeat():
    return await rpc.value

rpc.add_namespace('repeat', repeat)

rpc.generate_pyi('CustomSchema') # Generate Pyi file

rpc.run_server(AioServer())
