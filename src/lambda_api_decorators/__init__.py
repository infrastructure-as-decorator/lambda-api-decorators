"""CDK-free decorators for declaring Lambda API and configuration intent."""

from .decorators import (
    ANY,
    DELETE,
    GET,
    POST,
    PUT,
    description,
    environment,
    grant_dynamodb,
    grant_s3,
    layer,
    memory_size,
    name,
    permission,
    role,
    runtime,
    security_group,
    timeout,
    vpc,
)
