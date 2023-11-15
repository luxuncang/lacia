from typing import NamedTuple, Tuple, Dict, Optional, Any, Union, TypeVar, TYPE_CHECKING

from lacia.standard.abcbase import BaseDataTrans

T = TypeVar("T")

if TYPE_CHECKING:
    from lacia.standard.jsonast import JsonAst

class BaseJsonAst(NamedTuple):
    obj: Union[str, "JsonAst", None]
    method: Optional[str]
    args: Optional[Tuple["JsonAst" | Any, ...]]
    kwargs: Optional[Dict[str, "JsonAst" | Any]]
    
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
            obj=cls.fromdict(d["obj"]) if isinstance(d["obj"], dict) else d["obj"],
            method=d["method"],
            args=tuple(
                cls.fromdict(arg) if isinstance(arg, dict) else arg
                for arg in d["args"]
            )
            if d["args"]
            else d["args"],
            kwargs={
                k: cls.fromdict(v) if isinstance(v, dict) else v
                for k, v in d["kwargs"].items()
            }
            if d["kwargs"]
            else d["kwargs"],
        )

class JsonAst(BaseJsonAst, BaseDataTrans[dict]):

    def dumps(self) -> dict:
        return self.todict()
    
    @classmethod
    def loads(cls, obj: dict) -> "JsonAst":
        return cls.fromdict(obj)
