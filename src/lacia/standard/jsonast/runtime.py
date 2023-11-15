
import asyncio
from typing import Dict, Any, Type, TYPE_CHECKING

from lacia.standard.abcbase import BaseRunTime, BaseStandard, Namespace
from lacia.standard.jsonast.impl import JsonAst

if TYPE_CHECKING:
    from lacia.core.proxy import ProxyObj

class RunTime(BaseRunTime[JsonAst]):
    
    def __init__(self, namespace: Dict[str, Any]):
        self.namespace = namespace

    async def run(self, ast: JsonAst):
        if isinstance(ast, JsonAst):
            if isinstance(ast.obj, JsonAst):
                obj = await self.run(ast.obj)
            elif ast.obj is None:
                if not ast.args is None:
                    if len(ast.args) == 1 and isinstance(ast.args[0], str):
                        obj = self.namespace[ast.args[0]]
                    else:
                        raise TypeError(f"obj type error: {ast.obj}")
                else:
                    raise TypeError(f"obj type error: {ast.obj}")    
            elif isinstance(ast.obj, str):
                obj = self.namespace[ast.obj]
            else:
                raise TypeError(f"obj type error: {ast.obj}")
            if ast.method is None or ast.obj is None:
                return obj
            if not ast.args is None:
                if len(ast.args) == 1 and ast.method == "__getattr__" and isinstance(ast.args[0], str):
                    return getattr(obj, ast.args[0])
            func = getattr(obj, ast.method)
            if ast.args is None and ast.kwargs is None:
                return func
            if ast.method == "__anext__":
                return await func()
            
            args = []
            kwargs = {}
            for i in ast.args or ():
                args.append(await self.run(i))
            if ast.kwargs:
                for k,v in ast.kwargs.items():
                    kwargs[k] = await self.run(v)
            args = tuple(args)
            if ast.method == "__call__" and asyncio.iscoroutinefunction(obj):
                return await func(*args, **kwargs)
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            return func(*args, **kwargs)
        else:
            return ast

class Standard(BaseStandard[dict, JsonAst]):

    _jsonrpc = "jsonast"

    datatrans: Type[JsonAst] = JsonAst
    runtime: Type[RunTime] = RunTime

