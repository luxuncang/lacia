from typing import NamedTuple, Tuple, Dict, Optional, Any, Union, TypeVar, List

from lacia.standard.abcbase import BaseDataTrans

T = TypeVar("T")

class BaseJsonAst(NamedTuple):
    obj: Union[str, "JsonAst", None, List[str]]
    method: Optional[str]
    args: Optional[Tuple[Any, ...]] # Optional[Tuple[Union[str, "JsonAst"], ...]]
    kwargs: Optional[Dict[str, Any]] # Optional[Dict[str, "JsonAst" | Any]]
    
    def todict(self):
        def handle_value(value):
            if isinstance(value, BaseJsonAst):
                return value.todict()
            elif isinstance(value, (list, tuple)):
                return type(value)(handle_value(v) for v in value)
            elif isinstance(value, dict):
                return {k: handle_value(v) for k, v in value.items()}
            else:
                return value

        return {
            "obj": handle_value(self.obj),
            "method": self.method,
            "args": handle_value(self.args),
            "kwargs": handle_value(self.kwargs),
        }

    @classmethod
    def fromdict(cls, d: dict):
        def handle_value(value):
            if isinstance(value, dict) and cls.is_jsonast(value):
                return cls.fromdict(value)
            elif isinstance(value, (list, tuple)):
                return type(value)(handle_value(v) for v in value)
            elif isinstance(value, dict):
                return {k: handle_value(v) for k, v in value.items()}
            else:
                return value

        return cls(
            obj=handle_value(d["obj"]), # type: ignore
            method=d["method"],
            args=handle_value(d["args"]),  # type: ignore
            kwargs=handle_value(d["kwargs"]),  # type: ignore
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
