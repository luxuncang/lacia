from __future__ import annotations

from enum import Enum

from typing import Dict, Any

Message = Dict[str, Any]

class JsonRpcCode(int, Enum):
    ParseError = -32700             
    InvalidRequest = -32600
    MethodNotFound = -32601
    InvalidParams = -32602
    InternalError = -32603
    ServerError = -32000
    StopAsyncIterationError = -32099

class RpcMessage:

    def __init__(self, data: Dict[str, Any]):
        self.data = data
    
    @property
    def jsonrpc(self) -> str:
        return self.data.get("jsonrpc", None)
    
    @property
    def id(self) -> Any:
        return self.data.get("id", None)

    @property
    def method(self):
        return self.data.get("method", {})

    @property
    def result(self) -> Any:
        return self.data.get("result", None)
    
    @property
    def error(self) -> Any:
        return self.data.get("error", None)
    
    @property
    def error_code(self) -> int:
        return self.data["error"]["code"]

    @property
    def error_msg(self) -> str:
        return self.data["error"]["message"]
    
    @property
    def is_error(self) -> bool:
        return "error" in self.data

    @property
    def is_request(self) -> bool:
        return "method" in self.data
    
    @property
    def is_response(self) -> bool:
        return "result" in self.data or "error" in self.data

    @property
    def is_auth(self) -> bool:

        return all(
            [
                self.method["obj"] == {'obj': None, 'method': '__getattr__', 'args': ['rpc_auto_register'], 'kwargs': {}},
            ]
        )
