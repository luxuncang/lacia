from pydantic import BaseModel

from ...typing import Param, Optional, Union, List, Dict, Tuple, Literal
from ..basestandard import JsonRpcError, ProxyObj, analysis_proxy


class JsonRpcXRequest(BaseModel):
    """
    JSON-RPC X
    """
    jsonrpc: Literal['X'] = 'X'
    id: str
    method: List[Union[str, Tuple[tuple, dict]]]

class JsonRpcXResponse(BaseModel):
    """
    JSON-RPC X
    """
    jsonrpc: Literal['X'] = 'X'
    id: Optional[str] = None
    result: Optional[Param] = None
    error: Optional[JsonRpcError] = None

def proxy_to_jsonrpcx(proxy: ProxyObj):
    """
    JSON-RPC X
    """
    return list(proxy)

def analysis_jsonrpcX_message(message: JsonRpcXRequest):
    return analysis_proxy(message.method)