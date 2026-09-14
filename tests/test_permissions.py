import pytest

from conftest import assert_invocations, public_decorator


@pytest.mark.parametrize("access", ["read", "write"])
def test_dynamodb_logical_resource(access):
    grant = public_decorator("grant_dynamodb")

    @grant("orders", access)
    def handler():
        pass

    assert_invocations(handler, [("grant_dynamodb", ("orders", access), {})])


@pytest.mark.parametrize("access", ["read", "write"])
def test_dynamodb_physical_table(access):
    grant = public_decorator("grant_dynamodb")

    @grant(table_name="orders-prod", access=access)
    def handler():
        pass

    assert_invocations(
        handler,
        [("grant_dynamodb", (), {"table_name": "orders-prod", "access": access})],
    )


def test_dynamodb_explicit_logical_keyword_form():
    grant = public_decorator("grant_dynamodb")

    @grant(resource_key="orders", access="read")
    def handler():
        pass

    assert_invocations(
        handler,
        [("grant_dynamodb", (), {"resource_key": "orders", "access": "read"})],
    )


@pytest.mark.parametrize("access", ["read_write", "admin", ""])
def test_dynamodb_rejects_invalid_access_strings(access):
    grant = public_decorator("grant_dynamodb")
    with pytest.raises(ValueError):
        grant("orders", access)


@pytest.mark.parametrize("access", [None, 1, object()])
def test_dynamodb_rejects_non_string_access(access):
    grant = public_decorator("grant_dynamodb")
    with pytest.raises(TypeError):
        grant("orders", access)


@pytest.mark.parametrize("resource_key", ["", "   "])
def test_dynamodb_rejects_empty_logical_identifiers(resource_key):
    grant = public_decorator("grant_dynamodb")
    with pytest.raises(ValueError):
        grant(resource_key, "read")


@pytest.mark.parametrize("resource_key", [1, object()])
def test_dynamodb_rejects_non_string_logical_identifiers(resource_key):
    grant = public_decorator("grant_dynamodb")
    with pytest.raises(TypeError):
        grant(resource_key, "read")


@pytest.mark.parametrize("table_name", ["", "   "])
def test_dynamodb_rejects_empty_physical_identifiers(table_name):
    grant = public_decorator("grant_dynamodb")
    with pytest.raises(ValueError):
        grant(table_name=table_name, access="read")


def test_dynamodb_rejects_non_string_physical_identifier():
    grant = public_decorator("grant_dynamodb")
    with pytest.raises(TypeError):
        grant(table_name=42, access="read")


def test_dynamodb_requires_exactly_one_addressing_mode():
    grant = public_decorator("grant_dynamodb")
    with pytest.raises(ValueError):
        grant(access="read")
    with pytest.raises(ValueError):
        grant("orders", "read", table_name="orders-prod")


@pytest.mark.parametrize(
    "args,kwargs",
    [
        ((None, "read"), {}),
        ((), {"resource_key": None, "access": "read"}),
        ((), {"table_name": None, "access": "read"}),
    ],
)
def test_dynamodb_rejects_explicit_none_identifiers(args, kwargs):
    grant = public_decorator("grant_dynamodb")
    with pytest.raises(TypeError):
        grant(*args, **kwargs)


@pytest.mark.parametrize(
    "args,kwargs",
    [
        ((None, "read"), {"table_name": "orders-prod"}),
        ((), {"resource_key": None, "table_name": "orders-prod", "access": "read"}),
        ((), {"resource_key": "orders", "table_name": None, "access": "read"}),
    ],
)
def test_dynamodb_none_does_not_bypass_addressing_xor(args, kwargs):
    grant = public_decorator("grant_dynamodb")
    with pytest.raises(ValueError, match="requires exactly one"):
        grant(*args, **kwargs)


@pytest.mark.parametrize("keyword", ["index_name", "stream_arn"])
def test_dynamodb_rejects_index_and_stream_parameters(keyword):
    grant = public_decorator("grant_dynamodb")
    with pytest.raises(TypeError):
        grant("orders", "read", **{keyword: "not-part-of-this-contract"})


@pytest.mark.parametrize(
    "outer_resource,outer_access,inner_resource,inner_access",
    [("orders", "read", "customers", "write"), ("orders", "read", "orders", "write")],
)
def test_repeated_dynamodb_grants_preserve_boundaries_and_order(
    outer_resource, outer_access, inner_resource, inner_access
):
    grant = public_decorator("grant_dynamodb")

    @grant(outer_resource, outer_access)
    @grant(inner_resource, inner_access)
    def handler():
        pass

    assert_invocations(
        handler,
        [
            ("grant_dynamodb", (outer_resource, outer_access), {}),
            ("grant_dynamodb", (inner_resource, inner_access), {}),
        ],
    )


@pytest.mark.parametrize("access", ["read", "write"])
def test_s3_logical_resource(access):
    grant = public_decorator("grant_s3")

    @grant("documents", access)
    def handler():
        pass

    assert_invocations(handler, [("grant_s3", ("documents", access), {})])


@pytest.mark.parametrize("access", ["read", "write"])
def test_s3_physical_bucket(access):
    grant = public_decorator("grant_s3")

    @grant(bucket_name="documents-prod", access=access)
    def handler():
        pass

    assert_invocations(
        handler,
        [("grant_s3", (), {"bucket_name": "documents-prod", "access": access})],
    )


def test_s3_explicit_logical_keyword_form():
    grant = public_decorator("grant_s3")

    @grant(resource_key="documents", access="read")
    def handler():
        pass

    assert_invocations(
        handler,
        [("grant_s3", (), {"resource_key": "documents", "access": "read"})],
    )


@pytest.mark.parametrize("access", ["read_write", "admin", ""])
def test_s3_rejects_invalid_access_strings(access):
    grant = public_decorator("grant_s3")
    with pytest.raises(ValueError):
        grant("documents", access)


@pytest.mark.parametrize("access", [None, 1, object()])
def test_s3_rejects_non_string_access(access):
    grant = public_decorator("grant_s3")
    with pytest.raises(TypeError):
        grant("documents", access)


@pytest.mark.parametrize("resource_key", ["", "   "])
def test_s3_rejects_empty_logical_identifiers(resource_key):
    grant = public_decorator("grant_s3")
    with pytest.raises(ValueError):
        grant(resource_key, "read")


@pytest.mark.parametrize("resource_key", [1, object()])
def test_s3_rejects_non_string_logical_identifiers(resource_key):
    grant = public_decorator("grant_s3")
    with pytest.raises(TypeError):
        grant(resource_key, "read")


@pytest.mark.parametrize("bucket_name", ["", "   "])
def test_s3_rejects_empty_physical_identifiers(bucket_name):
    grant = public_decorator("grant_s3")
    with pytest.raises(ValueError):
        grant(bucket_name=bucket_name, access="read")


def test_s3_rejects_non_string_physical_identifier():
    grant = public_decorator("grant_s3")
    with pytest.raises(TypeError):
        grant(bucket_name=42, access="read")


def test_s3_requires_exactly_one_addressing_mode():
    grant = public_decorator("grant_s3")
    with pytest.raises(ValueError):
        grant(access="read")
    with pytest.raises(ValueError):
        grant("documents", "read", bucket_name="documents-prod")


@pytest.mark.parametrize(
    "args,kwargs",
    [
        ((None, "read"), {}),
        ((), {"resource_key": None, "access": "read"}),
        ((), {"bucket_name": None, "access": "read"}),
    ],
)
def test_s3_rejects_explicit_none_identifiers(args, kwargs):
    grant = public_decorator("grant_s3")
    with pytest.raises(TypeError):
        grant(*args, **kwargs)


@pytest.mark.parametrize(
    "args,kwargs",
    [
        ((None, "read"), {"bucket_name": "documents-prod"}),
        ((), {"resource_key": None, "bucket_name": "documents-prod", "access": "read"}),
        ((), {"resource_key": "documents", "bucket_name": None, "access": "read"}),
    ],
)
def test_s3_none_does_not_bypass_addressing_xor(args, kwargs):
    grant = public_decorator("grant_s3")
    with pytest.raises(ValueError, match="requires exactly one"):
        grant(*args, **kwargs)


def test_repeated_s3_grants_preserve_boundaries_and_order():
    grant = public_decorator("grant_s3")

    @grant("documents", "read")
    @grant("archive", "write")
    def handler():
        pass

    assert_invocations(
        handler,
        [
            ("grant_s3", ("documents", "read"), {}),
            ("grant_s3", ("archive", "write"), {}),
        ],
    )


@pytest.mark.parametrize(
    "actions,resources",
    [
        (["events:PutEvents"], ["arn:one"]),
        (("events:PutEvents", "sns:Publish"), ("arn:one", "arn:two")),
    ],
)
def test_permission_accepts_non_empty_string_sequences(actions, resources):
    permission = public_decorator("permission")

    @permission(actions=actions, resources=resources)
    def handler():
        pass

    expected_kwargs = {"actions": tuple(actions), "resources": tuple(resources)}
    # Equality intentionally accepts either stored tuples or equivalent lists.
    name, args, kwargs = __import__("conftest").invocation_values(
        __import__("conftest").metadata(handler)[0]
    )
    assert (name, args) == ("permission", ())
    assert tuple(kwargs["actions"]) == expected_kwargs["actions"]
    assert tuple(kwargs["resources"]) == expected_kwargs["resources"]


def test_permission_copies_mutable_inputs():
    permission = public_decorator("permission")
    actions = ["events:PutEvents"]
    resources = ["arn:one"]

    @permission(actions=actions, resources=resources)
    def handler():
        pass

    actions.append("sns:Publish")
    resources.append("arn:two")
    name, args, kwargs = __import__("conftest").invocation_values(
        __import__("conftest").metadata(handler)[0]
    )
    assert (name, args) == ("permission", ())
    assert tuple(kwargs["actions"]) == ("events:PutEvents",)
    assert tuple(kwargs["resources"]) == ("arn:one",)


@pytest.mark.parametrize("missing", ["actions", "resources"])
def test_permission_requires_both_keyword_arguments(missing):
    permission = public_decorator("permission")
    kwargs = {"actions": ["events:PutEvents"], "resources": ["arn:one"]}
    del kwargs[missing]
    with pytest.raises(TypeError):
        permission(**kwargs)


def test_permission_arguments_are_keyword_only():
    permission = public_decorator("permission")
    with pytest.raises(TypeError):
        permission(["events:PutEvents"], ["arn:one"])


@pytest.mark.parametrize("field", ["actions", "resources"])
@pytest.mark.parametrize("value", [[], ()])
def test_permission_rejects_empty_collections(field, value):
    permission = public_decorator("permission")
    kwargs = {"actions": ["events:PutEvents"], "resources": ["arn:one"], field: value}
    with pytest.raises(ValueError):
        permission(**kwargs)


@pytest.mark.parametrize("field", ["actions", "resources"])
@pytest.mark.parametrize("value", ["one-value", b"bytes", 42, object()])
def test_permission_rejects_non_sequence_or_bare_string_inputs(field, value):
    permission = public_decorator("permission")
    kwargs = {"actions": ["events:PutEvents"], "resources": ["arn:one"], field: value}
    with pytest.raises(TypeError):
        permission(**kwargs)


@pytest.mark.parametrize("field", ["actions", "resources"])
@pytest.mark.parametrize("member", [42, object()])
def test_permission_rejects_non_string_members(field, member):
    permission = public_decorator("permission")
    kwargs = {"actions": ["events:PutEvents"], "resources": ["arn:one"], field: [member]}
    with pytest.raises(TypeError):
        permission(**kwargs)


@pytest.mark.parametrize("field", ["actions", "resources"])
@pytest.mark.parametrize("member", ["", "   "])
def test_permission_rejects_empty_string_members(field, member):
    permission = public_decorator("permission")
    kwargs = {"actions": ["events:PutEvents"], "resources": ["arn:one"], field: [member]}
    with pytest.raises(ValueError):
        permission(**kwargs)


@pytest.mark.parametrize(
    "unsupported", ["effect", "conditions", "principals", "not_actions", "not_resources", "sid"]
)
def test_permission_rejects_advanced_iam_keywords(unsupported):
    permission = public_decorator("permission")
    with pytest.raises(TypeError):
        permission(
            actions=["events:PutEvents"],
            resources=["arn:one"],
            **{unsupported: "not-supported"}
        )


def test_repeated_permissions_preserve_boundaries_and_order():
    permission = public_decorator("permission")

    @permission(actions=["events:PutEvents"], resources=["arn:one"])
    @permission(actions=["sns:Publish"], resources=["arn:two"])
    def handler():
        pass

    assert_invocations(
        handler,
        [
            ("permission", (), {"actions": ("events:PutEvents",), "resources": ("arn:one",)}),
            ("permission", (), {"actions": ("sns:Publish",), "resources": ("arn:two",)}),
        ],
    )


def test_mixed_permission_stack_uses_one_ordered_metadata_sequence():
    GET = public_decorator("GET")
    runtime = public_decorator("runtime")
    dynamodb = public_decorator("grant_dynamodb")
    s3 = public_decorator("grant_s3")
    permission = public_decorator("permission")

    @GET("/orders")
    @runtime("python3.12")
    @dynamodb("orders", "write")
    @s3("documents", "read")
    @permission(actions=["events:PutEvents"], resources=["arn:one"])
    def handler(event, context):
        return event, context

    assert_invocations(
        handler,
        [
            ("GET", ("/orders",), {}),
            ("runtime", ("python3.12",), {}),
            ("grant_dynamodb", ("orders", "write"), {}),
            ("grant_s3", ("documents", "read"), {}),
            ("permission", (), {"actions": ("events:PutEvents",), "resources": ("arn:one",)}),
        ],
    )
