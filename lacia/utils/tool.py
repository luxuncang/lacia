
import asyncio
from typing import Callable

class CallObj:

    def __init__(self, method: Callable, args, kwargs):
        self.method = method
        self.args = args or ()
        self.kwargs = kwargs or {} 

    def add_args(self, *args):
        self.args = (*self.args, *args) # type: ignore
        return self

    def add_kwargs(self, **kwargs):
        self.kwargs = {**self.kwargs, **kwargs} # type: ignore
        return self

    async def __call__(self):
        if asyncio.iscoroutinefunction(self.method):
            return await self.method(*self.args, **self.kwargs)
        return self.method(*self.args, **self.kwargs)