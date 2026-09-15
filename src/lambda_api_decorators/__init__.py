"""CDK-free decorators for declaring Lambda API and configuration intent."""

from .decorators import (
    ANY,
    DELETE,
    GET,
    POST,
    PUT,
    authorizer,
    description,
    environment,
    grant_dynamodb,
    grant_s3,
    layer,
    memory_size,
    name,
    permission,
    public,
    role,
    runtime,
    security_group,
    timeout,
    vpc,
)
from .identity import CurrentUser, CurrentUserError, current_user
