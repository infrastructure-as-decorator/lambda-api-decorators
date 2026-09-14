"""Behavior-focused helpers for the decorator contract tests."""

from collections.abc import Mapping, Sequence

import pytest

import lambda_api_decorators as package


_NAMES = ("name", "decorator_name")
_ARGS = ("args", "positional_args")
_KWARGS = ("kwargs", "keyword_args")


def public_decorator(name):
    decorator = getattr(package, name, None)
    if decorator is None:
        pytest.fail("lambda_api_decorators must export {!r}".format(name))
    return decorator


def _field(record, candidates):
    if isinstance(record, Mapping):
        for candidate in candidates:
            if candidate in record:
                return record[candidate]
    for candidate in candidates:
        if hasattr(record, candidate):
            return getattr(record, candidate)
    raise AssertionError(
        "metadata invocation must expose one of: {}".format(", ".join(candidates))
    )


def invocation_values(record):
    """Return the public behavioral fields without requiring a record class."""
    name = _field(record, _NAMES)
    args = tuple(_field(record, _ARGS))
    raw_kwargs = _field(record, _KWARGS)
    kwargs = dict(raw_kwargs)
    return name, args, kwargs


def metadata(function):
    """Discover the one structured invocation collection attached to a handler.

    The contract deliberately does not require a metadata attribute or record
    class name. An implementation can use records or mappings, provided each
    entry exposes name/args/kwargs behavior.
    """
    candidates = []
    for _attribute, value in vars(function).items():
        if isinstance(value, (str, bytes, Mapping)) or not isinstance(value, Sequence):
            continue
        try:
            for record in value:
                invocation_values(record)
        except (AssertionError, TypeError, ValueError):
            continue
        candidates.append(value)

    assert len(candidates) == 1, (
        "handler must expose one package-scoped structured metadata collection"
    )
    return candidates[0]


def assert_invocations(function, expected):
    actual = [invocation_values(record) for record in metadata(function)]
    assert actual == expected
