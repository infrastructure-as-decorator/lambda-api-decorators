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


HTTP_DECORATORS = ("GET", "POST", "PUT", "DELETE", "ANY")


@pytest.mark.parametrize("second_name", HTTP_DECORATORS)
def test_any_second_public_http_decorator_is_rejected(second_name):
    outer = public_decorator("GET")
    inner = public_decorator(second_name)

    def lambda_handler():
        pass

    with pytest.raises(ValueError, match="multiple routes"):
        outer("/outer")(inner("/inner")(lambda_handler))


@pytest.mark.parametrize(
    "outer_name,inner_name",
    [(outer, inner) for outer in HTTP_DECORATORS for inner in HTTP_DECORATORS if outer != inner],
)
def test_different_http_methods_are_rejected(outer_name, inner_name):
    outer = public_decorator(outer_name)
    inner = public_decorator(inner_name)

    def lambda_handler():
        pass

    with pytest.raises(ValueError):
        outer("/orders")(inner("/orders/search")(lambda_handler))


@pytest.mark.parametrize("decorator_name", HTTP_DECORATORS)
def test_two_routes_for_the_same_http_method_are_rejected(decorator_name):
    decorator = public_decorator(decorator_name)

    def lambda_handler():
        pass

    with pytest.raises(ValueError):
        decorator("/orders")(decorator("/archived-orders")(lambda_handler))


def test_route_error_is_independent_of_decorator_order_and_identifies_handler_routes():
    GET = public_decorator("GET")
    POST = public_decorator("POST")

    def lambda_handler():
        pass

    with pytest.raises(ValueError) as first:
        GET("/orders")(POST("/orders/search")(lambda_handler))

    def lambda_handler():
        pass

    with pytest.raises(ValueError) as second:
        POST("/orders/search")(GET("/orders")(lambda_handler))

    expected = (
        "Lambda handler 'lambda_handler' declares multiple routes: "
        "GET /orders, POST /orders/search. "
        "Each handler must declare exactly one HTTP route."
    )
    assert str(first.value) == expected
    assert str(second.value) == expected


def test_non_http_handler_metadata_remains_functional_with_one_route():
    GET = public_decorator("GET")
    runtime = public_decorator("runtime")
    permission = public_decorator("permission")

    @GET("/orders")
    @runtime("python3.12")
    @permission(actions=["orders:Read"], resources=["orders"])
    def lambda_handler(event):
        return event

    assert lambda_handler({"ok": True}) == {"ok": True}
    assert_invocations(
        lambda_handler,
        [
            ("GET", ("/orders",), {}),
            ("runtime", ("python3.12",), {}),
            (
                "permission",
                (),
                {"actions": ("orders:Read",), "resources": ("orders",)},
            ),
        ],
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
