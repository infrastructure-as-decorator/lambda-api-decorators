import pytest

from conftest import assert_invocations, public_decorator


@pytest.mark.parametrize(
    "decorator_name,path",
    [
        ("GET", "/orders"),
        ("POST", "/orders"),
        ("PUT", "/orders/{id}"),
        ("DELETE", "/orders/{id}"),
        ("ANY", "/{proxy+}"),
    ],
)
def test_http_decorator_records_its_invocation(decorator_name, path):
    decorator = public_decorator(decorator_name)

    @decorator(path)
    def handler():
        pass

    assert_invocations(handler, [(decorator_name, (path,), {})])


def test_stacked_http_decorators_preserve_lexical_order():
    GET = public_decorator("GET")
    POST = public_decorator("POST")

    @GET("/orders")
    @POST("/orders")
    def handler():
        pass

    assert_invocations(
        handler,
        [("GET", ("/orders",), {}), ("POST", ("/orders",), {})],
    )


@pytest.mark.parametrize(
    "decorator_name,args,kwargs",
    [
        ("runtime", ("python3.12",), {}),
        ("timeout", (30,), {}),
        ("memory_size", (512,), {}),
        ("role", ("api-role",), {}),
        ("vpc", ("application-vpc",), {}),
        ("environment", ("database", "application"), {"stage": "prod"}),
        ("layer", ("shared",), {"architecture": "arm64"}),
        ("security_group", ("lambda-sg", "database-sg"), {}),
        ("name", ("orders-handler",), {}),
        ("description", ("Handles orders",), {}),
    ],
)
def test_configuration_decorator_preserves_arguments(decorator_name, args, kwargs):
    decorator = public_decorator(decorator_name)

    @decorator(*args, **kwargs)
    def handler():
        pass

    assert_invocations(handler, [(decorator_name, args, kwargs)])


def test_repeated_configuration_decorators_are_not_flattened():
    layer = public_decorator("layer")

    @layer("outer")
    @layer("inner")
    def handler():
        pass

    assert_invocations(
        handler,
        [("layer", ("outer",), {}), ("layer", ("inner",), {})],
    )


def test_mixed_decorators_preserve_top_to_bottom_lexical_order():
    GET = public_decorator("GET")
    runtime = public_decorator("runtime")
    role = public_decorator("role")
    layer = public_decorator("layer")

    @GET("/orders")
    @runtime("python3.12")
    @role("api-role")
    @layer("shared")
    def handler():
        pass

    assert_invocations(
        handler,
        [
            ("GET", ("/orders",), {}),
            ("runtime", ("python3.12",), {}),
            ("role", ("api-role",), {}),
            ("layer", ("shared",), {}),
        ],
    )


def test_repeated_names_remain_ordered_when_mixed_with_other_decorators():
    layer = public_decorator("layer")
    runtime = public_decorator("runtime")

    @layer("outer")
    @runtime("python3.12")
    @layer("inner")
    def handler():
        pass

    assert_invocations(
        handler,
        [
            ("layer", ("outer",), {}),
            ("runtime", ("python3.12",), {}),
            ("layer", ("inner",), {}),
        ],
    )
