import asyncio
from lacia import JsonRpc, AioClient, logger, __version__
from laciaschema.CustomSchema import CustomSchema

expose = {
    'value': f'PyJsonRpc Client {__version__}',
    'open': lambda f: open(f, 'r', encoding = 'utf-8').read()
}

loop = asyncio.new_event_loop()

irpc = JsonRpc('/test', namespace=expose, loop=loop)
rpc = irpc.with_schema(CustomSchema)

async def main():
    await irpc.run_client(AioClient())

    res1 = await rpc.value
    res2 = await rpc.add(4, 4)
    res3 = await rpc.number().add(10).sub(10).value # type: ignore
    res4 = await rpc.repeat()

    logger.info(res1)
    logger.info(res2)
    logger.info(res3)
    logger.info(res4)

    async for i in rpc.async_generator(5):
        logger.info(i)

loop.run_until_complete(main())
loop.run_forever()
