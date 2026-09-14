"""Internal, CDK-free representation of decorator declarations."""

from dataclasses import dataclass
from typing import Any, Callable, Tuple, TypeVar


F = TypeVar("F", bound=Callable[..., Any])
_METADATA_ATTRIBUTE = "__lambda_api_decorator_invocations__"


@dataclass(frozen=True)
class DecoratorInvocation:
    """One decorator call, retained independently from every other call."""

    name: str
    args: Tuple[Any, ...]
    kwargs: Tuple[Tuple[str, Any], ...]


def declaration(
    name: str, args: Tuple[Any, ...], kwargs: Tuple[Tuple[str, Any], ...]
) -> Callable[[F], F]:
    """Create a decorator which prepends immutable declaration metadata."""
    invocation = DecoratorInvocation(name=name, args=args, kwargs=kwargs)

    def decorator(function: F) -> F:
        existing = getattr(function, _METADATA_ATTRIBUTE, ())
        setattr(function, _METADATA_ATTRIBUTE, (invocation,) + existing)
        return function

    return decorator
