from .basestandard import JsonRpcError, ProxyObj, Proxy, analysis_proxy, JsonRpcCode, Assign, T_Res, T_Req
from .jsonrpc2 import JsonRpc2Request, JsonRpc2Response, proxy_to_jsonrpc2, analysis_jsonrpc2_message
from .jsonrpcX import JsonRpcXRequest, JsonRpcXResponse, proxy_to_jsonrpcx, analysis_jsonrpcX_message

from ..typing import Generic, TypeVar

class Standard(Generic[T_Res, T_Req]):

    @staticmethod
    def json_to_request(json_data: dict):
        if json_data['jsonrpc'] == '2.0':
            return JsonRpc2Request(**json_data)
        if json_data['jsonrpc'] == 'X':
            return JsonRpcXRequest(**json_data)
        raise TypeError('jsonrpc must be 2.0 or X')

    @staticmethod
    def json_to_response(json_data: dict):
        if json_data['jsonrpc'] == '2.0':
            return JsonRpc2Response(**json_data)
        if json_data['jsonrpc'] == 'X':
            return JsonRpcXResponse(**json_data)
        raise TypeError('jsonrpc must be 2.0 or X')
