"""Public decorators for declaring Lambda API and configuration intent."""

from collections.abc import Sequence
from typing import Any, Callable, Tuple

from .metadata import _METADATA_ATTRIBUTE, declaration


_MISSING = object()
_VALID_ACCESS = ("read", "write")
_AUTH_DECLARATIONS = ("authorizer", "public")
_HTTP_DECLARATIONS = ("GET", "POST", "PUT", "DELETE", "ANY")


def _simple(name: str, *args: Any, **kwargs: Any) -> Callable:
    return declaration(name, tuple(args), tuple(kwargs.items()))


def _http(name: str, path: Any) -> Callable:
    decorate = declaration(name, (path,), ())

    def decorator(function):
        existing = vars(function).get(_METADATA_ATTRIBUTE, ())
        routes = [
            invocation
            for invocation in existing
            if invocation.name in _HTTP_DECLARATIONS
        ]
        if routes:
            found_routes = [
                (invocation.name, invocation.args[0]) for invocation in routes
            ]
            found_routes.append((name, path))
            found_routes.sort()
            rendered_routes = ", ".join(
                "{} {}".format(method, route) for method, route in found_routes
            )
            raise ValueError(
                "Lambda handler {!r} declares multiple routes: {}. "
                "Each handler must declare exactly one HTTP route.".format(
                    function.__name__, rendered_routes
                )
            )
        return decorate(function)

    return decorator


def _auth_declaration(name: str, args: Tuple[Any, ...]) -> Callable:
    decorate = declaration(name, args, ())

    def decorator(function):
        existing = vars(function).get(_METADATA_ATTRIBUTE, ())
        if any(invocation.name in _AUTH_DECLARATIONS for invocation in existing):
            raise ValueError("a callable may have only one authentication declaration")
        return decorate(function)

    return decorator


def GET(path):
    return _http("GET", path)


def PUT(path):
    return _http("PUT", path)


def POST(path):
    return _http("POST", path)


def DELETE(path):
    return _http("DELETE", path)


def ANY(path):
    return _http("ANY", path)


def authorizer(key, /):
    _validate_identifier(key, "key")
    return _auth_declaration("authorizer", (key,))


def public(function):
    return _auth_declaration("public", ())(function)


def memory_size(arg):
    return _simple("memory_size", arg)


def timeout(arg):
    return _simple("timeout", arg)


def environment(*eargs, **kwargs):
    return _simple("environment", *eargs, **kwargs)


def layer(*largs, **kwargs):
    return _simple("layer", *largs, **kwargs)


def runtime(arg):
    return _simple("runtime", arg)


def security_group(*sgargs):
    return _simple("security_group", *sgargs)


def vpc(arg):
    return _simple("vpc", arg)


def role(arg):
    return _simple("role", arg)


def description(arg):
    return _simple("description", arg)


def name(arg):
    return _simple("name", arg)


def _validate_identifier(value: Any, parameter: str) -> None:
    if not isinstance(value, str):
        raise TypeError("{} must be a string".format(parameter))
    if not value.strip():
        raise ValueError("{} must be a non-empty string".format(parameter))


def _validate_access(access: Any) -> None:
    if not isinstance(access, str):
        raise TypeError("access must be a string")
    if access not in _VALID_ACCESS:
        raise ValueError("access must be 'read' or 'write'")


def _grant(
    decorator_name: str,
    physical_parameter: str,
    positional: Tuple[Any, ...],
    resource_key: Any,
    access: Any,
    physical_name: Any,
) -> Callable:
    if len(positional) > 2:
        raise TypeError("{} accepts at most two positional arguments".format(decorator_name))
    if positional and resource_key is not _MISSING:
        raise TypeError("resource_key was supplied more than once")
    if len(positional) == 2 and access is not _MISSING:
        raise TypeError("access was supplied more than once")

    logical_name = positional[0] if positional else resource_key
    access_value = positional[1] if len(positional) == 2 else access
    has_logical = logical_name is not _MISSING
    has_physical = physical_name is not _MISSING

    if has_logical == has_physical:
        raise ValueError(
            "{} requires exactly one of resource_key or {}".format(
                decorator_name, physical_parameter
            )
        )
    if has_logical:
        _validate_identifier(logical_name, "resource_key")
    if has_physical:
        _validate_identifier(physical_name, physical_parameter)
    _validate_access(None if access_value is _MISSING else access_value)

    keyword_items = []
    if resource_key is not _MISSING:
        keyword_items.append(("resource_key", resource_key))
    if physical_name is not _MISSING:
        keyword_items.append((physical_parameter, physical_name))
    if access is not _MISSING:
        keyword_items.append(("access", access))
    return declaration(decorator_name, tuple(positional), tuple(keyword_items))


def grant_dynamodb(
    *args, resource_key=_MISSING, access=_MISSING, table_name=_MISSING
):
    """Declare read or cumulative write access to a DynamoDB table."""
    return _grant(
        "grant_dynamodb", "table_name", args, resource_key, access, table_name
    )


def grant_s3(*args, resource_key=_MISSING, access=_MISSING, bucket_name=_MISSING):
    """Declare read or cumulative write access to an S3 bucket."""
    return _grant("grant_s3", "bucket_name", args, resource_key, access, bucket_name)


def _string_sequence(value: Any, parameter: str) -> Tuple[str, ...]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise TypeError("{} must be a sequence of strings".format(parameter))
    if not value:
        raise ValueError("{} must not be empty".format(parameter))

    normalized = []
    for member in value:
        if not isinstance(member, str):
            raise TypeError("{} members must be strings".format(parameter))
        if not member.strip():
            raise ValueError("{} members must be non-empty strings".format(parameter))
        normalized.append(member)
    return tuple(normalized)


def permission(*, actions, resources):
    """Declare a minimal IAM action/resource permission statement."""
    normalized_actions = _string_sequence(actions, "actions")
    normalized_resources = _string_sequence(resources, "resources")
    return declaration(
        "permission",
        (),
        (("actions", normalized_actions), ("resources", normalized_resources)),
    )
