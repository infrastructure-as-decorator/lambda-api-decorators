import importlib
import inspect
import re
from collections.abc import Mapping
from dataclasses import FrozenInstanceError, fields, is_dataclass
from typing import Any, Mapping as TypingMapping, Optional, get_type_hints

import pytest

import lambda_api_decorators as package


@pytest.fixture
def identity_api():
    """Load the intended API without making a missing RED-stage module uncollectable."""
    try:
        module = importlib.import_module("lambda_api_decorators.identity")
    except ModuleNotFoundError:
        pytest.fail("lambda_api_decorators.identity must exist")

    missing = {
        name
        for name in ("CurrentUser", "CurrentUserError", "current_user")
        if not hasattr(module, name)
    }
    assert not missing
    return module.CurrentUser, module.CurrentUserError, module.current_user


def rest_event(claims):
    return {"requestContext": {"authorizer": {"claims": claims}}}


def jwt_event(claims):
    return {"requestContext": {"authorizer": {"jwt": {"claims": claims}}}}


def test_public_types_and_function_have_the_frozen_contract(identity_api):
    CurrentUser, CurrentUserError, current_user = identity_api

    assert is_dataclass(CurrentUser)
    assert [(field.name, field.type) for field in fields(CurrentUser)] == [
        ("subject", str),
        ("username", Optional[str]),
        ("claims", TypingMapping[str, Any]),
    ]
    assert issubclass(CurrentUserError, ValueError)
    hints = get_type_hints(current_user)
    assert hints == {"event": TypingMapping[str, Any], "return": CurrentUser}
    assert list(inspect.signature(current_user).parameters) == ["event"]


def test_rest_cognito_identity_happy_path(identity_api):
    CurrentUser, _, current_user = identity_api
    claims = {
        "sub": "rest-user-123",
        "cognito:username": "rest-user",
        "email": "rest@example.com",
        "custom:tenant": "tenant-a",
    }

    user = current_user(rest_event(claims))

    assert isinstance(user, CurrentUser)
    assert user.subject == "rest-user-123"
    assert user.username == "rest-user"
    assert dict(user.claims) == claims


def test_http_jwt_identity_happy_path(identity_api):
    CurrentUser, _, current_user = identity_api
    claims = {
        "sub": "jwt-user-456",
        "username": "jwt-user",
        "email": "jwt@example.com",
        "scope": "orders:read",
    }

    user = current_user(jwt_event(claims))

    assert isinstance(user, CurrentUser)
    assert user.subject == "jwt-user-456"
    assert user.username == "jwt-user"
    assert dict(user.claims) == claims


def test_subject_and_username_are_validated_but_not_normalized(identity_api):
    _, _, current_user = identity_api

    user = current_user(
        rest_event({"sub": " user-123 ", "cognito:username": " display-name "})
    )

    assert user.subject == " user-123 "
    assert user.username == " display-name "


@pytest.mark.parametrize(
    "optional_claims,expected",
    [
        ({"cognito:username": "cognito", "username": "generic"}, "cognito"),
        ({"username": "generic"}, "generic"),
        ({"cognito:username": "", "username": "generic"}, "generic"),
        ({"cognito:username": "   ", "username": "generic"}, "generic"),
        ({"cognito:username": 7, "username": "generic"}, "generic"),
        ({"cognito:username": None, "username": "generic"}, "generic"),
        ({"cognito:username": "cognito"}, "cognito"),
        ({}, None),
        ({"cognito:username": [], "username": None}, None),
    ],
)
def test_username_precedence_and_optional_malformed_values(
    identity_api, optional_claims, expected
):
    _, _, current_user = identity_api
    claims = {"sub": "subject"}
    claims.update(optional_claims)

    assert current_user(rest_event(claims)).username == expected


@pytest.mark.parametrize(
    "event,message",
    [
        (None, "event must be a mapping"),
        (42, "event must be a mapping"),
        ({}, "event.requestContext must be a mapping"),
        ({"requestContext": None}, "event.requestContext must be a mapping"),
        ({"requestContext": []}, "event.requestContext must be a mapping"),
        (
            {"requestContext": {}},
            "event.requestContext.authorizer must be a mapping",
        ),
        (
            {"requestContext": {"authorizer": None}},
            "event.requestContext.authorizer must be a mapping",
        ),
        (
            {"requestContext": {"authorizer": "invalid"}},
            "event.requestContext.authorizer must be a mapping",
        ),
    ],
)
def test_malformed_common_structure_raises_public_error(identity_api, event, message):
    _, CurrentUserError, current_user = identity_api

    with pytest.raises(CurrentUserError, match="^{}$".format(re.escape(message))):
        current_user(event)


@pytest.mark.parametrize("claims", [pytest.param(None, id="none"), pytest.param([], id="list")])
def test_malformed_rest_claims_raise_public_error(identity_api, claims):
    _, CurrentUserError, current_user = identity_api
    event = {"requestContext": {"authorizer": {"claims": claims}}}

    with pytest.raises(
        CurrentUserError,
        match=r"^event\.requestContext\.authorizer\.claims must be a mapping$",
    ):
        current_user(event)


def test_missing_rest_claims_raise_public_error(identity_api):
    _, CurrentUserError, current_user = identity_api
    event = {"requestContext": {"authorizer": {}}}

    with pytest.raises(
        CurrentUserError,
        match=r"^event\.requestContext\.authorizer\.claims must be a mapping$",
    ):
        current_user(event)


@pytest.mark.parametrize("jwt", [pytest.param(None, id="none"), pytest.param([], id="list")])
def test_non_mapping_present_jwt_raises_public_error(identity_api, jwt):
    _, CurrentUserError, current_user = identity_api
    event = {"requestContext": {"authorizer": {"jwt": jwt}}}

    with pytest.raises(
        CurrentUserError,
        match=r"^event\.requestContext\.authorizer\.jwt must be a mapping$",
    ):
        current_user(event)


@pytest.mark.parametrize(
    "jwt", [{}, {"claims": None}, {"claims": "invalid"}], ids=["missing", "none", "string"]
)
def test_missing_or_malformed_jwt_claims_raise_public_error(identity_api, jwt):
    _, CurrentUserError, current_user = identity_api
    event = {"requestContext": {"authorizer": {"jwt": jwt}}}

    with pytest.raises(
        CurrentUserError,
        match=r"^event\.requestContext\.authorizer\.jwt\.claims must be a mapping$",
    ):
        current_user(event)


@pytest.mark.parametrize("jwt", [None, [], {}, {"claims": None}])
def test_malformed_present_jwt_never_falls_back_to_valid_rest_claims(
    identity_api, jwt
):
    _, CurrentUserError, current_user = identity_api
    authorizer = {"jwt": jwt, "claims": {"sub": "rest-subject"}}
    event = {"requestContext": {"authorizer": authorizer}}

    with pytest.raises(CurrentUserError):
        current_user(event)


def test_valid_jwt_claims_win_when_both_claim_paths_exist(identity_api):
    _, _, current_user = identity_api
    authorizer = {
        "jwt": {"claims": {"sub": "jwt-subject", "username": "jwt-user"}},
        "claims": {"sub": "rest-subject", "cognito:username": "rest-user"},
    }

    user = current_user({"requestContext": {"authorizer": authorizer}})

    assert user.subject == "jwt-subject"
    assert user.username == "jwt-user"


@pytest.mark.parametrize(
    "subject",
    [
        pytest.param(None, id="none"),
        pytest.param(7, id="integer"),
        pytest.param([], id="list"),
        pytest.param("", id="empty"),
        pytest.param("   ", id="ascii-whitespace"),
        pytest.param("\u2003\u2009", id="unicode-whitespace"),
    ],
)
def test_invalid_subject_raises_public_error(identity_api, subject):
    _, CurrentUserError, current_user = identity_api

    with pytest.raises(
        CurrentUserError,
        match=r"^authorizer claims must contain a non-empty string 'sub'$",
    ):
        current_user(rest_event({"sub": subject}))


def test_missing_subject_does_not_fall_back_to_other_identity_claims(identity_api):
    _, CurrentUserError, current_user = identity_api
    claims = {
        "cognito:username": "cognito-user",
        "username": "generic-user",
        "email": "user@example.com",
        "principalId": "principal",
    }

    with pytest.raises(
        CurrentUserError,
        match=r"^authorizer claims must contain a non-empty string 'sub'$",
    ):
        current_user(rest_event(claims))


def test_invalid_subject_uses_same_contract_for_jwt_claims(identity_api):
    _, CurrentUserError, current_user = identity_api

    with pytest.raises(CurrentUserError):
        current_user(jwt_event({"sub": "\t\n"}))


def test_claims_are_a_read_only_isolated_shallow_snapshot(identity_api):
    _, _, current_user = identity_api
    nested = {"roles": ["reader"]}
    claims = {"sub": "subject", "email": "original@example.com", "nested": nested}

    user = current_user(rest_event(claims))

    assert isinstance(user.claims, Mapping)
    assert user.claims["nested"] is nested
    with pytest.raises(TypeError):
        user.claims["email"] = "assigned@example.com"
    with pytest.raises(TypeError):
        del user.claims["email"]

    claims["email"] = "changed@example.com"
    claims["new"] = "new value"
    del claims["sub"]
    assert user.claims["email"] == "original@example.com"
    assert "new" not in user.claims
    assert user.claims["sub"] == "subject"


def test_current_user_fields_cannot_be_reassigned(identity_api):
    _, _, current_user = identity_api
    user = current_user(rest_event({"sub": "subject"}))

    with pytest.raises(FrozenInstanceError):
        user.subject = "replacement"


def test_current_user_depends_on_event_not_decorator_metadata(identity_api):
    _, CurrentUserError, current_user = identity_api
    event = rest_event({"sub": "same-subject"})

    def undecorated():
        pass

    @package.authorizer("users")
    def authorized():
        pass

    @package.public
    def public_handler():
        pass

    for handler in (undecorated, authorized, public_handler):
        assert current_user(event).subject == "same-subject"
        assert handler is not None

    with pytest.raises(CurrentUserError):
        current_user({"requestContext": {"authorizer": {}}})
