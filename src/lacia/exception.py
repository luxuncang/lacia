
class JsonRpcJsonRpcException(Exception):
    ...

class JsonRpcInitException(JsonRpcJsonRpcException):
    ...

class JsonRpcWsException(JsonRpcJsonRpcException):
    ...

class JsonRpcWsConnectException(JsonRpcWsException):
    ...

class JsonRpcRuntimeException(JsonRpcWsException):
    ...