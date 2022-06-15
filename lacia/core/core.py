import asyncio
import uuid
from typing import Callable
from json.decoder import JSONDecodeError

from pydantic.error_wrappers import ValidationError

from .abcbase import BaseJsonRpc, JsonRpcMode
from ..standard import (
    Proxy,
    ProxyObj,
    Assign,
    proxy_to_jsonrpc2,
    proxy_to_jsonrpcx,
    analysis_jsonrpc2_message,
    analysis_jsonrpcX_message,
    Standard,
    JsonRpc2Request,
    JsonRpc2Response,
    JsonRpcXRequest,
    JsonRpcXResponse,
    JsonRpcError,
    JsonRpcCode,
)
from ..logs import logger
from ..exception import WebSocketClosedError
from ..utils import run_fm, asyncio_loop_apply
from ..typing import Any, Dict, Optional, Union, Param, TYPE_CHECKING, AsyncGenerator

if TYPE_CHECKING:
    from ..network.client.aioclient import AioClient, BaseClient
    from ..network.server.aioserver import AioServer, BaseServer
    from ..core.core import JsonRpc

    Server = Union[AioServer, BaseServer]
    Client = Union[AioClient, BaseClient]


class JsonRpc(BaseJsonRpc, Proxy):  # TODO： Server 和 Client 分离
    def __init__(
        self,
        path: str = "",
        host: str = "localhost",
        port: int = 8080,
        execer: bool = True,
        jsonrpc_mode: JsonRpcMode = JsonRpcMode.Auto,
        namespace: Dict[str, Any] = {},
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ):
        self._PATH = path
        self._HOST = host
        self._PORT = port
        self._Execer = execer
        self._JsonRpcMode = jsonrpc_mode
        self._namespace = namespace
        self._loop = loop or asyncio.get_event_loop()
        asyncio_loop_apply(self._loop)  # TODO: 不兼容审查

    def run_server(self, server: "Server"):
        self._server = server
        self._server.set_on_ws(self.__listening_client, self)
        server.start(self._PATH, self._HOST, self._PORT, self._loop)

    async def run_client(self, client: "Client"):
        self._client = client
        await client.start(path=f"http://{self._HOST}:{self._PORT}{self._PATH}")
        self._loop.create_task(self.__listen_server())

    async def __listening_client(self, websocket) -> None:
        logger.info("🛰️ listening client")
        try:
            async for message in self._server.iter_json(websocket):
                try:
                    message_type = self.auto_request_response(message)
                    if message_type == "request":
                        msg = Standard.json_to_request(message)
                        if msg.id in Assign.future:
                            Assign.post_data(msg, False)
                        else:
                            self._loop.create_task(self.__exce_rpc(msg, websocket))
                    elif message_type == "response":
                        msg = Standard.json_to_response(message)
                        Assign.post_data(msg)  # type: ignore
                except ValidationError as e:
                    await self.__send_error_response(
                        websocket, JsonRpcCode.InvalidRequest, str(e), message
                    )
        except JSONDecodeError as e:
            logger.exception(e)
            await self.__send_error_response(websocket, JsonRpcCode.ParseError, str(e))
        except Exception as e:
            logger.exception(e)
            f: Callable = self._Eevents.get("Exception", None)
            if f:
                self._loop.create_task(f(e))  # type: ignore

    async def __listen_server(self) -> None:
        logger.info("🛰️ listening server")
        try:
            async for message in self._client.iter_json():
                try:
                    message_type = self.auto_request_response(message)
                    if message_type == "request":
                        msg = Standard.json_to_request(message)
                        if msg.id in Assign.future:
                            Assign.post_data(msg, False)
                        else:
                            self._loop.create_task(self.__exce_rpc(msg, self._client))
                    elif message_type == "response":
                        msg = Standard.json_to_response(message)
                        Assign.post_data(msg)  # type: ignore
                except ValidationError as e:
                    await self.__send_error_response(
                        self._client, JsonRpcCode.InvalidRequest, str(e), message
                    )
        except JSONDecodeError as e:
            logger.exception(e)
            await self.__send_error_response(self.ws, JsonRpcCode.ParseError, str(e))
        except WebSocketClosedError as e:
            logger.debug(str(e))
        except Exception as e:
            logger.exception(e)
            f: Callable = self._Eevents.get("Exception", None)
            if f:
                self._loop.create_task(f(e))  # type: ignore

    async def __exce_rpc(
        self, message: Union[JsonRpc2Request, JsonRpcXRequest], websocket
    ) -> Any:
        logger.info(f"⚙️ try exce_rpc: {message}")
        try:
            if not self.execer:
                raise AttributeError("execer is not set correctly")
            if isinstance(message, JsonRpc2Request):
                fm = list(analysis_jsonrpc2_message(message))
            elif isinstance(message, JsonRpcXRequest):
                fm = list(analysis_jsonrpcX_message(message))
            else:
                raise TypeError("message is not correctly")
            result = await run_fm(fm, self._namespace)
            if (not isinstance(result, (int, dict, tuple, list, str, bool))) and result != None:
                await self.__handle_aiter(result, websocket, message)
            else:
                await self.__send_result(websocket, message, result)
        except AttributeError as e:
            logger.exception(e)
            await self.__send_error_response(
                websocket, JsonRpcCode.MethodNotFound, str(e), message.dict()
            )
        except TypeError as e:
            logger.exception(e)
            await self.__send_error_response(
                websocket, JsonRpcCode.ParseError, str(e), message.dict()
            )
        except Exception as e:
            logger.exception(e)
            await self.__send_error_response(
                websocket, JsonRpcCode.InternalError, str(e), message.dict()
            )

    async def __send_result(
        self, websocket, message: Union[JsonRpc2Request, JsonRpcXRequest], result: Param
    ) -> None:
        if isinstance(message, JsonRpc2Request):
            await websocket.send_json(
                JsonRpc2Response(id=message.id, result=result).dict(exclude={"error"})
            )
        elif isinstance(message, JsonRpcXRequest):
            await websocket.send_json(
                JsonRpcXResponse(id=message.id, result=result).dict(exclude={"error"})
            )
        else:
            raise TypeError("message is not correctly")

    async def __send_request(self, proxy: ProxyObj):
        if hasattr(self, "_client"):
            if not self._client.closed():
                request = self.auto_standard(proxy)
                await self._client.send_json(request.dict())
                return await Assign.receiver(request.id)
        raise AttributeError("client is not running")

    async def __send_request_client(self, proxy: ProxyObj):
        request = self.auto_standard(proxy)
        # await proxy.__self._client.send_json()
        await self._client.send_json(request.dict())
        return await Assign.receiver(request.id)

    async def send_request_server(self, proxy: ProxyObj, websocket):
        request = self.auto_standard(proxy)
        await self._server.send_json(websocket, request.dict())
        return await Assign.receiver(request.id)

    async def __send_error_response(
        self, websocket, error: JsonRpcCode, error_data: str, message: dict = {}
    ) -> None:
        logger.error(f"🚨 error: {error} {error._name_} {message}")
        if self._JsonRpcMode in (JsonRpcMode.Auto, JsonRpcMode.JsonRpc2):
            response = JsonRpc2Response(
                id=message.get("id", None),
                error=JsonRpcError(code=error, message=error._name_, data=error_data),
            ).dict(exclude={"result"})
        elif self._JsonRpcMode in (JsonRpcMode.Auto, JsonRpcMode.JsonRpcX):
            response = JsonRpcXResponse(
                id=message.get("id", None),
                error=JsonRpcError(code=error, message=error._name_, data=error_data),
            ).dict(exclude={"result"})
        else:
            raise ValueError("JsonRpcMode is not set correctly")
        await websocket.send_json(response)

    async def __handle_aiter(self, result, websocket, message: Union[JsonRpc2Request, JsonRpcXRequest]):
        async for r in result():
            await self.__send_result(websocket, message, r)
            await Assign.receiver(message.id, False)
        await self.__send_error_response(websocket, JsonRpcCode.StopAsyncIterationError, "", message.dict())

    def auto_standard(self, proxy: ProxyObj):  # TODO: 重构
        try:
            method, params = proxy_to_jsonrpc2(proxy)
        except TypeError:
            method = proxy_to_jsonrpcx(proxy)
        uid = str(uuid.uuid1())
        loc = locals()
        if self._JsonRpcMode == JsonRpcMode.Auto:
            return (
                JsonRpc2Request(id=uid, method=method, params=params)  # type: ignore
                if "params" in loc
                else JsonRpcXRequest(id=uid, method=method)  # type: ignore
            )
        elif self._JsonRpcMode == JsonRpcMode.JsonRpc2:
            if "params" in loc:
                return JsonRpc2Request(id=uid, method=method, params=params)  # type: ignore
        elif self._JsonRpcMode == JsonRpcMode.JsonRpcX:
            if "params" in loc:
                return JsonRpc2Request(id=uid, method=method, params=params)  # type: ignore
            else:
                return JsonRpcXRequest(id=uid, method=method)  # type: ignore
        raise ValueError("JsonRpcMode is not set correctly")

    def auto_request_response(self, message: dict):
        if 'method' in message:
            return 'request'
        if 'result' in message or 'error' in message:
            return 'response'
        raise JSONDecodeError("message is not correctly", '', 0)

    async def __aenter__(self) -> "JsonRpc":
        ...

    async def __aexit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        ...

    def add_namespace(self, name: str, v: Any):
        self._namespace[name] = v