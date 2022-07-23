import asyncio
from lacia import JsonRpc, AioServer


loop = asyncio.new_event_loop()

rpc = JsonRpc('/remotefile', loop=loop, debug=True)

async def repeat(filename):
    data = await rpc.open(filename, 'r', encoding='utf-8').read()
    return data

rpc.add_namespace('repeat_open', repeat)

rpc.run_server(AioServer())
