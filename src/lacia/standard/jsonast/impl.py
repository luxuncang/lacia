from typing import NamedTuple, Tuple, Dict, Optional, Any, Union, TypeVar

from lacia.standard.abcbase import BaseDataTrans

T = TypeVar("T")

class BaseJsonAst(NamedTuple):
    obj: Union[str, "JsonAst", None]
    method: Optional[str]
    args: Optional[Tuple[Any, ...]] # Optional[Tuple[Union[str, "JsonAst"], ...]]
    kwargs: Optional[Dict[str, Any]] # Optional[Dict[str, "JsonAst" | Any]]
    
    def todict(self):
        return {
            "obj": self.obj.todict() if isinstance(self.obj, JsonAst) else self.obj,
            "method": self.method,
            "args": tuple(
                arg.todict() if isinstance(arg, JsonAst) else arg for arg in self.args
            )
            if self.args
            else self.args,
            "kwargs": {
                k: v.todict() if isinstance(v, JsonAst) else v
                for k, v in self.kwargs.items()
            }
            if self.kwargs
            else self.kwargs,
        }

    @classmethod
    def fromdict(cls, d: dict):
        return cls(
            obj=cls.fromdict(d["obj"]) if cls.is_jsonast(d["obj"]) else d["obj"],
            method=d["method"],
            args=tuple(
                cls.fromdict(arg) if cls.is_jsonast(arg) else arg
                for arg in d["args"]
            )
            if d["args"]
            else d["args"],
            kwargs={
                k: cls.fromdict(v) if cls.is_jsonast(v) else v
                for k, v in d["kwargs"].items()
            }
            if d["kwargs"]
            else d["kwargs"],
        )
    
    @classmethod
    def is_jsonast(cls, obj: Any) -> bool:
        return isinstance(obj, dict) and "obj" in obj and "method" in obj and "args" in obj and "kwargs" in obj and len(obj) == 4

class JsonAst(BaseJsonAst, BaseDataTrans[dict]):

    def dumps(self) -> dict:
        return self.todict()
    
    @classmethod
    def loads(cls, obj: dict) -> "JsonAst":
        return cls.fromdict(obj)
