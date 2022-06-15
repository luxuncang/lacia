# TODO 异常处理本地化

class WebSocketClosedError(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self) -> str:
        return super().__str__() + ": " + self.message


class JsonRpcException(Exception):
    def __init__(self, code: int, data, message) -> None:
        self.code = code
        self.data = data
        self.message = message

    def __str__(self) -> str:
        return f"{super().__str__()} {self.code} {self.data} {self.message}"


