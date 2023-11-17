import asyncio
from typing import Optional, Dict

import orjson
import bson
import aiohttp
from aiohttp import web, WSCloseCode

from lacia.network.abcbase import BaseServer, Connection
from lacia.logger import logger
from lacia.utils.tool import CallObj
from lacia.exception import JsonRpcWsConnectException

class AioServer(BaseServer[web.WebSocketResponse]):
    on_events = {}

    def __init__(
        self,
        path: str = "",
        host: str = "localhost",
        port: int = 8080,
        loop: Optional[asyncio.AbstractEventLoop] = None
    ) -> None:
        self.app = web.Application()
        self.active_connections: Connection[web.WebSocketResponse] = Connection()
        self.name_connections: Dict[str, web.WebSocketResponse] = {}
        self.loop = loop
        self.path = path
        self.host = host
        self.port = port

    def start(self) -> None: 
        self.app.add_routes([web.get(self.path, self.websocket_handler)])
        if self.loop is None: 
            self.loop = asyncio.get_event_loop()
        web.run_app(self.app, host=self.host, port=self.port, print=logger.info, loop=self.loop)  # type: ignore 

    async def websocket_handler(self, request):
        event = asyncio.Event()
        ws = web.WebSocketResponse(autoclose=False)
        await ws.prepare(request)
        self.active_connections.set_ws(ws, event)
        
        logger.success(f"{str(ws)} connected.")

        obj = self.on_events.get("connect")
        if not obj is None:
            await obj.method(ws, *obj.args, **obj.kwargs)

        await event.wait()
        return ws

    def disconnect(self, websocket: web.WebSocketResponse):
        for ws, event in self.active_connections.ws.items():
            if ws == websocket: 
                event.set()
                self.active_connections.clear_ws(ws)
                break

    async def receive(self, websocket: web.WebSocketResponse):
        try:
            async for data in websocket:
                if data.type == aiohttp.WSMsgType.close:
                    raise JsonRpcWsConnectException(str(data.data))
                else:
                    return data
        except Exception as e:
            await self.close_ws(websocket)
            raise JsonRpcWsConnectException(f"{self.__class__.__name__} closed.")

    async def receive_json(self, websocket: web.WebSocketResponse):
        data = await self.receive(websocket)
        if data and data.type == aiohttp.WSMsgType.TEXT:
            data = orjson.loads(data.data)
            return data
        elif data and data.type == aiohttp.WSMsgType.BINARY:
            data = bson.loads(data.data)
            return data
        raise JsonRpcWsConnectException("Invalid data type.")

    async def receive_bytes(self, websocket: web.WebSocketResponse):
        data = await self.receive(websocket)
        if data and data.type == aiohttp.WSMsgType.BINARY:
            return data.data

    async def iter_bytes(self, websocket: web.WebSocketResponse):
        try:
            while True:
                data = await self.receive_bytes(websocket)
                if data:
                    yield data
        except JsonRpcWsConnectException:
            logger.info(f"{str(websocket)} disconnected.")
        except Exception as e:
            logger.error(e)
            logger.info(f"{str(websocket)} disconnected.")
        finally:
            return

    async def iter_json(self, websocket: web.WebSocketResponse):
        try:
            while True:
                data = await self.receive_json(websocket)
                if data:
                    yield data
        except JsonRpcWsConnectException:
            logger.info(f"{str(websocket)} disconnected.")
        except Exception as e:
            print(e)
            logger.info(f"{str(websocket)} disconnected.")
        finally:
            return

    async def send_json(
        self, websocket: web.WebSocketResponse, message: dict, binary: bool = True
    ):
        if binary:
            return await websocket.send_bytes(bson.dumps(message))
        return await websocket.send_json(message)

    async def send_bytes(self, websocket: web.WebSocketResponse, message: bytes):
        return await websocket.send_bytes(message)

    async def close_ws(self, websocket: web.WebSocketResponse):
        name = str(websocket)
        obj = self.on_events.get("disconnect")
        if not obj is None:
            await obj.method(websocket, *obj.args, **obj.kwargs)
        self.disconnect(websocket)
        logger.info(f"{name} disconnected.")

    async def close(self):
        await self.app.shutdown()

    async def on_shutdown(self):
        for ws, event in self.active_connections.ws.items():
            await ws.close(code=WSCloseCode.GOING_AWAY, message=b"Server shutdown")
            event.set()

    def on(self, event: str, func, args: Optional[tuple] = None, kwargs: Optional[dict] = None) -> None:
        self.on_events[event] = CallObj(method=func, args=args, kwargs=kwargs)


