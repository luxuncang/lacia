import inspect
from typing import Any, Dict, List
import textwrap


def schema_gen(name: str, environment: Dict[str, Any]):
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
                    schema_gen_function(name, key, signature, value.__doc__ or ""),
                    " " * 4,
                )
                + "\n"
            )
        else:
            result += f"\n    {key}: typing.Awaitable[{type(value).__name__}]\n"

    return result


def schema_gen_function(base: str, name: str, signature: inspect.Signature, doc: str):
    return_type = format_type(signature.return_annotation)
    result = f"""
class _Proxy_{name}(typing.Protocol):
    async def __call__(self, {', '.join(map(str, signature.parameters.values()))}) -> {return_type}: ...
""".strip()
    params: List[str] = []
    for arg, param in signature.parameters.items():
        if param.kind == inspect.Parameter.POSITIONAL_ONLY:
            raise ValueError(f"{arg} is positional only")
        params.append(
            f"def {arg}(self, value: {format_type(param.annotation)}, /) -> {base}._Proxy_{name}_collector: ..."
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


def format_type(type_: Any) -> str:
    if type_ is getattr(inspect, "_empty"):
        return "typing.Any"
    if isinstance(type_, type):
        return type_.__name__
    return str(type_)
