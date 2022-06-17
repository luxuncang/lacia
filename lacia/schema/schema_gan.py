import inspect
from typing import Any, Dict, List
import textwrap


def schema_gen(name: str, environment: Dict[str, Any], mainname: str = "") -> str:
    result = f"""
import typing

class {name}:
""".strip()

    for key, value in environment.items():
        if inspect.isfunction(value):
            signature = inspect.signature(value)
            result += (
                "\n"
                + textwrap.indent(
                    schema_gen_function(
                        mainname if mainname else name,
                        key,
                        signature,
                        value.__doc__ or "",
                        mainname,
                        value,
                    ),
                    " " * 4,
                )
                + "\n"
            )
        elif inspect.isclass(value):
            main_name = f"{mainname if mainname else name}.{key}"
            res = schema_gen(key, obj_to_dict(value), main_name).split("\n")[1:]
            res[
                2
            ] = f"    def __await__(self) -> typing.Generator[typing.Any, typing.Any, {main_name}]: ..."
            result += "\n    ".join(res)
        else:
            result += f"\n    {key}: typing.Awaitable[{type(value).__name__}]\n"

    return result


def schema_gen_function(
    base: str,
    name: str,
    signature: inspect.Signature,
    doc: str,
    mainname: str,
    value: Any,
) -> str:
    return_type = format_type(signature.return_annotation, value)
    args = list(map(str, signature.parameters.values()))
    args = ", ".join(args) if base != mainname else ", ".join(args[1:])
    result = f"""
class _Proxy_{name}(typing.Protocol):
    async def __call__(self, {args}) -> {return_type}: ...
""".strip()
    params: List[str] = []
    for arg, param in signature.parameters.items():
        if param.kind == inspect.Parameter.POSITIONAL_ONLY:
            raise ValueError(f"{arg} is positional only")
        params.append(
            f"def {arg}(self, value: {format_type(param.annotation, value)}, /) -> {base}._Proxy_{name}_collector: ..."
        )

    parmas_str = "\n".join(params)
    result += "\n" + textwrap.indent(parmas_str, prefix=" " * 4) + "\n"

    result += f"""
class _Proxy_{name}_collector(typing.Protocol):
    def __await__(self) -> typing.Generator[typing.Any, typing.Any, {return_type}]: ...
""".strip()

    result += "\n" + textwrap.indent(parmas_str, prefix=" " * 4) + "\n"

    result += f"{name}: _Proxy_{name}"
    result += f'\n"""{doc}"""'

    return result


def format_type(type_: Any, value: Any) -> str:
    if type_ is getattr(inspect, "_empty"):
        return "typing.AsyncGenerator" if inspect.isasyncgenfunction(value) else "typing.Any"
    if isinstance(type_, type):
        return type_.__name__
    return str(type_)


def obj_to_dict(obj) -> Dict[str, Any]:
    return {
        k: v
        for k, v in obj.__dict__.items()
        if not k in ("__dict__", "__weakref__", "__doc__", "__annotations__")
    }
