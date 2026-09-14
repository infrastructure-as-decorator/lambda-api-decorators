import inspect

import pytest

from conftest import assert_invocations, metadata, public_decorator


IDENTITY_CASES = [
    ("GET", ("/orders",), {}),
    ("POST", ("/orders",), {}),
    ("PUT", ("/orders/{id}",), {}),
    ("DELETE", ("/orders/{id}",), {}),
    ("ANY", ("/{proxy+}",), {}),
    ("runtime", ("python3.12",), {}),
    ("timeout", (30,), {}),
    ("memory_size", (512,), {}),
    ("role", ("api-role",), {}),
    ("vpc", ("application-vpc",), {}),
    ("environment", ("database",), {}),
    ("layer", ("shared",), {}),
    ("security_group", ("lambda-sg",), {}),
    ("name", ("orders-handler",), {}),
    ("description", ("Handles orders",), {}),
    ("grant_dynamodb", ("orders", "read"), {}),
    ("grant_s3", ("documents", "read"), {}),
    ("permission", (), {"actions": ["events:PutEvents"], "resources": ["arn:one"]}),
]


@pytest.mark.parametrize("decorator_name,args,kwargs", IDENTITY_CASES)
def test_every_decorator_returns_exact_original_function(decorator_name, args, kwargs):
    decorator = public_decorator(decorator_name)

    def handler(event: dict, context: object = None) -> dict:
        """Original documentation."""
        return event

    handler.custom_attribute = object()
    original_signature = inspect.signature(handler)
    custom_attribute = handler.custom_attribute

    decorated = decorator(*args, **kwargs)(handler)

    assert decorated is handler
    assert decorated.__name__ == "handler"
    assert decorated.__doc__ == "Original documentation."
    assert decorated.__annotations__ == handler.__annotations__
    assert inspect.signature(decorated) == original_signature
    assert decorated.custom_attribute is custom_attribute
    assert decorated({"ok": True}) == {"ok": True}


def test_decorator_does_not_intercept_raised_exceptions():
    runtime = public_decorator("runtime")
    error = RuntimeError("handler failure")

    def handler():
        raise error

    decorated = runtime("python3.12")(handler)
    with pytest.raises(RuntimeError) as raised:
        decorated()
    assert raised.value is error


def test_decorator_preserves_async_function_identity_and_awaitability():
    runtime = public_decorator("runtime")

    async def handler(value: int) -> int:
        return value + 1

    decorated = runtime("python3.12")(handler)
    assert decorated is handler
    assert inspect.iscoroutinefunction(decorated)
    awaitable = decorated(1)
    assert inspect.isawaitable(awaitable)
    awaitable.close()


def test_metadata_is_isolated_between_functions():
    runtime = public_decorator("runtime")

    @runtime("python3.12")
    def first():
        pass

    @runtime("python3.11")
    def second():
        pass

    assert metadata(first) is not metadata(second)
    assert_invocations(first, [("runtime", ("python3.12",), {})])
    assert_invocations(second, [("runtime", ("python3.11",), {})])


def test_decorating_another_function_does_not_mutate_existing_metadata():
    layer = public_decorator("layer")

    @layer("first")
    def first():
        pass

    snapshot = tuple(metadata(first))

    @layer("second")
    def second():
        pass

    assert tuple(metadata(first)) == snapshot
    assert metadata(first) is not metadata(second)


def test_metadata_collection_cannot_be_externally_mutated():
    runtime = public_decorator("runtime")

    @runtime("python3.12")
    def handler():
        pass

    declarations = metadata(handler)
    assert not hasattr(declarations, "append")
    with pytest.raises(TypeError):
        declarations[0] = declarations[0]


def test_decorating_callable_does_not_accumulate_class_inherited_metadata():
    class Handler:
        __lambda_api_decorator_invocations__ = ("unrelated class metadata",)

        def __call__(self):
            pass

    handler = Handler()
    decorated = public_decorator("runtime")("python3.12")(handler)

    assert decorated is handler
    assert_invocations(handler, [("runtime", ("python3.12",), {})])


def test_metadata_payload_contains_only_cdk_free_python_values():
    permission = public_decorator("permission")

    @permission(actions=["events:PutEvents"], resources=["arn:one"])
    def handler():
        pass

    name, args, kwargs = next(iter(map(__import__("conftest").invocation_values, metadata(handler))))
    assert isinstance(name, str)
    assert isinstance(args, tuple)
    assert set(kwargs) == {"actions", "resources"}
    assert all(isinstance(item, str) for item in kwargs["actions"])
    assert all(isinstance(item, str) for item in kwargs["resources"])
