"""Runtime identity extraction from API Gateway authorizer context."""

from collections.abc import Mapping as MappingABC
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping, Optional


@dataclass(frozen=True)
class CurrentUser:
    """Identity claims supplied by an API Gateway authorizer."""

    subject: str
    username: Optional[str]
    claims: Mapping[str, Any]


class CurrentUserError(ValueError):
    """Raised when an event does not contain a valid supported identity."""


def _username(claims: Mapping[str, Any]) -> Optional[str]:
    for name in ("cognito:username", "username"):
        value = claims.get(name)
        if isinstance(value, str) and value.strip():
            return value
    return None


def current_user(event: Mapping[str, Any]) -> CurrentUser:
    """Extract identity from an already-authorized API Gateway event.

    This helper reads authorizer claims already present in the event. It does
    not authenticate the request, validate a token, or authorize an action.
    """
    if not isinstance(event, MappingABC):
        raise CurrentUserError("event must be a mapping")

    request_context = event.get("requestContext")
    if not isinstance(request_context, MappingABC):
        raise CurrentUserError("event.requestContext must be a mapping")

    authorizer = request_context.get("authorizer")
    if not isinstance(authorizer, MappingABC):
        raise CurrentUserError("event.requestContext.authorizer must be a mapping")

    if "jwt" in authorizer:
        jwt = authorizer.get("jwt")
        if not isinstance(jwt, MappingABC):
            raise CurrentUserError(
                "event.requestContext.authorizer.jwt must be a mapping"
            )
        claims = jwt.get("claims")
        if not isinstance(claims, MappingABC):
            raise CurrentUserError(
                "event.requestContext.authorizer.jwt.claims must be a mapping"
            )
    else:
        claims = authorizer.get("claims")
        if not isinstance(claims, MappingABC):
            raise CurrentUserError(
                "event.requestContext.authorizer.claims must be a mapping"
            )

    subject = claims.get("sub")
    if not isinstance(subject, str) or not subject.strip():
        raise CurrentUserError(
            "authorizer claims must contain a non-empty string 'sub'"
        )

    return CurrentUser(
        subject=subject,
        username=_username(claims),
        claims=MappingProxyType(dict(claims)),
    )
