import asyncio
from lacia import JsonRpc, AioClient, logger

expose = {
    'open': open
}

loop = asyncio.new_event_loop()

rpc = JsonRpc('/remotefile', namespace=expose, loop=loop)

async def main():
    await rpc.run_client(AioClient())

    res = await rpc.repeat_open('client.py')

    logger.info(res)

loop.run_until_complete(main())
loop.run_forever()
