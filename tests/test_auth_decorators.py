import inspect

import pytest

from conftest import assert_invocations, invocation_values, metadata, public_decorator


def test_authorizer_records_exactly_one_invocation():
    authorizer = public_decorator("authorizer")

    @authorizer("users")
    def handler():
        pass

    assert_invocations(handler, [("authorizer", ("users",), {})])


@pytest.mark.parametrize("key", [" users ", "Üsers-管理者"])
def test_authorizer_preserves_nonempty_keys_exactly(key):
    authorizer = public_decorator("authorizer")

    @authorizer(key)
    def handler():
        pass

    assert_invocations(handler, [("authorizer", (key,), {})])


@pytest.mark.parametrize(
    "args,kwargs",
    [
        ((), {}),
        (("users", "admins"), {}),
        ((), {"key": "users"}),
        (("users",), {"key": "admins"}),
        ((), {"unexpected": "users"}),
    ],
)
def test_authorizer_accepts_exactly_one_positional_argument(args, kwargs):
    authorizer = public_decorator("authorizer")

    with pytest.raises(TypeError):
        authorizer(*args, **kwargs)


@pytest.mark.parametrize(
    "key", [None, 1, b"users", ["users"], ("users",), {"key": "users"}, object()]
)
def test_authorizer_rejects_non_string_keys(key):
    authorizer = public_decorator("authorizer")

    with pytest.raises(TypeError):
        authorizer(key)


@pytest.mark.parametrize("key", ["", "   ", "\u2003\u2009"])
def test_authorizer_rejects_empty_or_whitespace_only_keys(key):
    authorizer = public_decorator("authorizer")

    with pytest.raises(ValueError):
        authorizer(key)


@pytest.mark.parametrize(
    "declaration",
    [
        lambda function: public_decorator("authorizer")("users")(function),
        lambda function: public_decorator("public")(function),
    ],
)
def test_auth_decorators_preserve_callable_identity_and_behavior(declaration):
    def handler(event: dict, context: object = None) -> dict:
        """Original documentation."""
        return event

    handler.custom_attribute = object()
    original_signature = inspect.signature(handler)
    custom_attribute = handler.custom_attribute

    decorated = declaration(handler)

    assert decorated is handler
    assert decorated.__name__ == "handler"
    assert decorated.__doc__ == "Original documentation."
    assert decorated.__annotations__ == handler.__annotations__
    assert inspect.signature(decorated) == original_signature
    assert decorated.custom_attribute is custom_attribute
    assert decorated({"ok": True}) == {"ok": True}


@pytest.mark.parametrize("name", ["authorizer", "public"])
def test_auth_decorators_preserve_async_callable_identity(name):
    async def handler(value: int) -> int:
        return value + 1

    decorator = public_decorator(name)
    decorated = (
        decorator("users")(handler) if name == "authorizer" else decorator(handler)
    )

    assert decorated is handler
    assert inspect.iscoroutinefunction(decorated)
    awaitable = decorated(1)
    assert inspect.isawaitable(awaitable)
    awaitable.close()


def test_bare_public_records_exactly_one_invocation():
    public = public_decorator("public")

    @public
    def handler():
        pass

    assert_invocations(handler, [("public", (), {})])


@pytest.mark.parametrize(
    "args,kwargs", [((), {}), ((object(), object()), {}), ((), {"unexpected": True})]
)
def test_public_rejects_factory_and_accidental_arguments(args, kwargs):
    public = public_decorator("public")

    with pytest.raises(TypeError):
        public(*args, **kwargs)


def test_public_parentheses_fail_as_decorator_syntax():
    public = public_decorator("public")

    with pytest.raises(TypeError):

        @public()
        def handler():
            pass


@pytest.mark.parametrize(
    "outer,inner",
    [
        ("public", "authorizer"),
        ("authorizer", "public"),
        ("public", "public"),
        ("authorizer", "authorizer"),
    ],
)
def test_auth_declarations_conflict_in_every_application_order(outer, inner):
    public = public_decorator("public")
    authorizer = public_decorator("authorizer")
    decorators = {"public": public, "authorizer": authorizer("users")}

    with pytest.raises(ValueError):

        @decorators[outer]
        @decorators[inner]
        def handler():
            raise AssertionError("decoration must fail before invocation")


@pytest.mark.parametrize(
    "outer_key,inner_key", [("users", "admins"), ("admins", "users")]
)
def test_different_authorizers_conflict_in_every_application_order(
    outer_key, inner_key
):
    authorizer = public_decorator("authorizer")

    with pytest.raises(ValueError):

        @authorizer(outer_key)
        @authorizer(inner_key)
        def handler():
            raise AssertionError("decoration must fail before invocation")


def test_repeated_unrelated_declarations_remain_valid():
    runtime = public_decorator("runtime")
    permission = public_decorator("permission")

    @runtime("python3.12")
    @runtime("python3.11")
    @permission(actions=["events:PutEvents"], resources=["arn:outer"])
    @permission(actions=["s3:GetObject"], resources=["arn:inner"])
    def handler():
        pass

    assert_invocations(
        handler,
        [
            ("runtime", ("python3.12",), {}),
            ("runtime", ("python3.11",), {}),
            (
                "permission",
                (),
                {"actions": ("events:PutEvents",), "resources": ("arn:outer",)},
            ),
            (
                "permission",
                (),
                {"actions": ("s3:GetObject",), "resources": ("arn:inner",)},
            ),
        ],
    )


@pytest.mark.parametrize(
    "auth_name,path", [("authorizer", "/admin"), ("public", "/health")]
)
@pytest.mark.parametrize("auth_outer", [False, True])
def test_auth_and_http_decorators_preserve_lexical_order(auth_name, path, auth_outer):
    GET = public_decorator("GET")
    auth = public_decorator(auth_name)
    auth = auth("admins") if auth_name == "authorizer" else auth

    def handler():
        pass

    if auth_outer:
        decorated = auth(GET(path)(handler))
        expected = [
            (auth_name, (("admins",) if auth_name == "authorizer" else ()), {}),
            ("GET", (path,), {}),
        ]
    else:
        decorated = GET(path)(auth(handler))
        expected = [
            ("GET", (path,), {}),
            (auth_name, (("admins",) if auth_name == "authorizer" else ()), {}),
        ]

    assert_invocations(decorated, expected)
    assert auth_name in [invocation_values(item)[0] for item in metadata(decorated)]


def test_auth_mixed_with_unrelated_declarations_preserves_boundaries_and_order():
    runtime = public_decorator("runtime")
    authorizer = public_decorator("authorizer")
    permission = public_decorator("permission")

    @runtime("python3.12")
    @authorizer("users")
    @permission(actions=["events:PutEvents"], resources=["arn:one"])
    def handler():
        pass

    assert_invocations(
        handler,
        [
            ("runtime", ("python3.12",), {}),
            ("authorizer", ("users",), {}),
            (
                "permission",
                (),
                {"actions": ("events:PutEvents",), "resources": ("arn:one",)},
            ),
        ],
    )
    assert [
        invocation_values(item)
        for item in metadata(handler)
        if invocation_values(item)[0] in {"authorizer", "public"}
    ] == [("authorizer", ("users",), {})]


@pytest.mark.parametrize("name", ["authorizer", "public"])
def test_auth_decorators_ignore_inherited_callable_metadata(name):
    class Handler:
        __lambda_api_decorator_invocations__ = ("unrelated class metadata",)

        def __call__(self):
            pass

    handler = Handler()
    decorator = public_decorator(name)
    decorated = (
        decorator("users")(handler) if name == "authorizer" else decorator(handler)
    )

    assert decorated is handler
    expected_args = ("users",) if name == "authorizer" else ()
    assert_invocations(handler, [(name, expected_args, {})])


def test_multiple_routes_with_authorizer_are_retained_in_lexical_order():
    GET = public_decorator("GET")
    POST = public_decorator("POST")
    authorizer = public_decorator("authorizer")

    @GET("/a")
    @POST("/b")
    @authorizer("users")
    def handler():
        pass

    assert_invocations(
        handler,
        [("GET", ("/a",), {}), ("POST", ("/b",), {}), ("authorizer", ("users",), {})],
    )
