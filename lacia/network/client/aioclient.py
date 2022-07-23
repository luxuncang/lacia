import orjson
import aiohttp

from ..abcbase import BaseClient
from ...logs import logger
from ...exception import WebSocketClosedError
from ...typing import Message, Optional, AsyncGenerator


class AioClient(BaseClient):
    def __init__(self) -> None:
        self.session = aiohttp.ClientSession()

    async def start(self, path: str) -> "AioClient":
        self.ws = await self.session.ws_connect(f"http://{path}")
        logger.success(f"📡 {self.__class__.__name__} success connected: {path}.")
        return self

    async def receive(self):
        try:
            async for data in self.ws:
                if data.type == aiohttp.WSMsgType.close:
                    raise WebSocketClosedError(data.data)
                else:
                    return data
        except:
            if not 'data' in locals():
                await self.close()
                raise WebSocketClosedError(f"{self.__class__.__name__} closed.")

    async def receive_json(self):
        data = await self.receive()
        if data and data.type == aiohttp.WSMsgType.TEXT:
            data = orjson.loads(data.data)
            return data

    async def receive_bytes(self):
        data = await self.receive()
        if data and data.type == aiohttp.WSMsgType.BINARY:
            return data.data

    async def iter_json(self) -> AsyncGenerator[Message, None]:
        while True:
            data = await self.receive_json()
            if data:
                yield data

    async def iter_bytes(self):
        while True:
            data = await self.receive_bytes()
            if data:
                yield data

    async def send(self, message) -> None:
        return await self.send(message)

    async def send_bytes(self, message: bytes) -> None:
        return await self.ws.send_bytes(message)

    async def send_json(self, message: Message) -> None:
        return await self.ws.send_json(message)

    async def close(
        self, code: Optional[int] = None, reason: Optional[str] = None
    ) -> None:
        await self.ws.close()

    def closed(self) -> bool:
        return self.ws.closed
