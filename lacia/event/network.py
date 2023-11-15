
from graia.broadcast import Broadcast, Dispatchable, DispatcherInterface

class WsConnectEvent(Dispatchable):

    def __init__(self, websocket):
        self.websocket = websocket

    class Dispatcher:

        @staticmethod
        async def catch(interface: DispatcherInterface):
            if interface.name == "websocket":
                return interface.event.websocket
