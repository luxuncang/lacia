import sys
import atexit
import asyncio
import inspect
from pathlib import Path

from nest_asyncio import apply
from pydantic import BaseModel

from .typing import PyMode, Optional, Any, List, Callable, Dict


class CallObj(BaseModel):
    method: Callable
    args: tuple
    kwargs: dict

    def add_args(self, *args):
        self.args = (*self.args, *args)
        return self

    def add_kwargs(self, **kwargs):
        self.kwargs = {**self.kwargs, **kwargs}
        return self

    async def __call__(self):
        return await self.method(*self.args, **self.kwargs)


class LaciaGenerator:
    def __init__(self, obj) -> None:
        self.obj = obj


def get_func_bind(func: Callable, *args, **kwargs) -> Dict[str, Any]:
    """
    Get the function binding.
    """
    sig = inspect.signature(func)
    return {k: v for k, v in sig.bind(*args, **kwargs).arguments.items()}


def get_python_mode() -> PyMode:  # TODO: There is a bug when the main file and the interpreter working file are in the same directory
    """
    Get the python mode.
    """
    path = Path(sys.argv[0])
    if path.is_file():
        if Path(path.parent) == Path(sys.path[0]):
            return "SCRIPT"
        else:
            return "REPL"
    else:
        return "REPL"


def asyncio_loop_apply(loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
    return apply(loop)


async def run_obj(obj: Any, method: str, args: tuple = (), kwargs: dict = {}) -> Any:

    if method == "__getattr__":
        if args[0] == "__aiter__":
            return obj
        else:
            obj = getattr(obj, args[0])
        return obj
    elif method == "__call__":
        if asyncio.iscoroutinefunction(obj):
            res = await obj(*args, **kwargs)
        else:
            res = obj(*args, **kwargs)
        return res
    raise AttributeError("Method not found")


async def run_fm(fm: List[dict], namespace: dict):
    method = fm[0]
    if (
        method["method"] == "__getattr__"
        and method["args"][0] in namespace
        and (not method["kwargs"])
    ):
        obj = namespace[method["args"][0]]
    else:
        raise AttributeError("Method not found")
    for i in fm[1:]:
        obj = await run_obj(obj, i["method"], i["args"], i["kwargs"])
    if "i" in locals() and i["method"] == "__getattr__" and i["args"][0] == "__aiter__":  # type: ignore
        return LaciaGenerator(obj)
    return obj


def auto_close_loop():
    """
    Close the loop when the program exits.
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        return
    try:
        asyncio.runners._cancel_all_tasks(loop)  # type: ignore
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.run_until_complete(loop.shutdown_default_executor())
    finally:
        loop.close()


atexit.register(auto_close_loop)
