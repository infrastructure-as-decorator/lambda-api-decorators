# Lambda API Decorators

Lightweight, CDK-free Python decorators for declaring AWS Lambda API routes
and configuration intent. The package records ordered metadata, preserves the
original callable, creates no infrastructure, and performs no request routing
at runtime. [Read the central documentation](https://infrastructure-as-decorator.github.io/)
for the complete architecture.

`lambda-api-decorators-cdk` can interpret this metadata to create independent
Lambda functions and connect them to API Gateway. Sharing a Python module does
not create a runtime router or imply one monolithic Lambda.

## Installation and compatibility

```bash
pip install lambda-api-decorators
```

The package supports Python 3.9–3.14 and has no runtime dependencies. The CDK
consumer is a separate package:

```bash
pip install lambda-api-decorators-cdk
```

The two packages are released and versioned independently.

## Quick start

This complete example declares one route, returns a proxy-compatible JSON
response, and adds configuration and permission metadata:

```python
import json

from lambda_api_decorators import GET, environment, permission, runtime


@GET("/health")
@runtime("python3.12")
@environment("production")
@permission(actions=["logs:CreateLogGroup"], resources=["*"])
def health(event, context):
    return {
        "statusCode": 200,
        "headers": {"content-type": "application/json"},
        "body": json.dumps({"status": "ok"}),
    }
```

The decorators leave `health` callable as a normal Python function. A
CDK-aware consumer reads its metadata when synthesizing infrastructure.

## Routes

The public HTTP decorators are `GET`, `POST`, `PUT`, `DELETE`, and `ANY`.
Each handler can declare at most one HTTP route. Applying a second route to
the same function raises `ValueError`.

Several independently decorated functions may share a module:

```python
from lambda_api_decorators import DELETE, GET, POST


@GET("/orders")
def list_orders(event, context):
    return {"statusCode": 200, "body": "[]"}


@POST("/orders")
def create_order(event, context):
    return {"statusCode": 201, "body": "{}"}


@DELETE("/orders/{order_id}")
def delete_order(event, context):
    return {"statusCode": 204, "body": ""}
```

`lambda-api-decorators-cdk` can turn these handlers into separate Lambdas.
There is no runtime routing layer and sharing a file does not make a single
Lambda or a route accumulator.

This is intentionally invalid:

```python
from lambda_api_decorators import GET, POST


@GET("/orders")
@POST("/orders")
def invalid_handler(event, context):
    return {"statusCode": 200, "body": "invalid"}
```

It raises `ValueError` while the decorators are applied.

## Lambda configuration metadata

The configuration decorators and their public argument shapes are:

```python
from lambda_api_decorators import (
    description,
    environment,
    layer,
    memory_size,
    name,
    role,
    runtime,
    security_group,
    timeout,
    vpc,
)


@runtime("python3.12")
@timeout(30)
@memory_size(512)
@name("orders-handler")
@description("Handles orders")
@role("orders-role")
@vpc("application-vpc")
@environment("production")
@layer("shared")
@security_group("orders-sg")
def configured_handler(event, context):
    return {"statusCode": 200, "body": "ok"}
```

The logical keys for roles, VPCs, environments, Layers, and security groups
are resolved by the infrastructure consumer. The runtime package does not
own or expose those registries and does not apply IAM or create AWS resources.

## Authentication

Use one authentication declaration per handler:

```python
from lambda_api_decorators import GET, authorizer, public


@GET("/users/me")
@authorizer("users")
def me(event, context):
    return {"statusCode": 200, "body": "{}"}


@GET("/health")
@public
def health(event, context):
    return {"statusCode": 200, "body": "ok"}
```

`@public` is used without parentheses. A handler accepts one authentication
declaration, and authentication is independent from its route declaration.

## `current_user`

`current_user(event)` reads claims already placed in an authorized API Gateway
event. It supports both shapes:

- REST API: `requestContext.authorizer.claims`
- HTTP API v2 JWT: `requestContext.authorizer.jwt.claims`

It returns a frozen `CurrentUser` with `subject`, optional `username`, and
read-only `claims`. `subject` comes from the `sub` claim. `username` prefers
`cognito:username` and then `username`. Malformed or missing identity data
raises `CurrentUserError`.

```python
from lambda_api_decorators import CurrentUser, CurrentUserError, current_user


def identify(event, context):
    try:
        user: CurrentUser = current_user(event)
    except CurrentUserError:
        return {"statusCode": 401, "body": "unauthorized"}
    return {"statusCode": 200, "body": user.subject}
```

This helper does not verify tokens, authenticate, authorize, or call AWS. It
only extracts and validates the supported claim shape.

## Permissions

DynamoDB and S3 grants accept a logical registry key or a physical name, and
an access value of `read` or `write`:

```python
from lambda_api_decorators import grant_dynamodb, grant_s3


@grant_dynamodb("orders", "read")
@grant_dynamodb("orders", "write")
@grant_s3("documents", "read")
def orders(event, context):
    return {"statusCode": 200, "body": "ok"}
```

The physical-name forms are also valid:

```python
from lambda_api_decorators import grant_dynamodb, grant_s3


@grant_dynamodb(table_name="orders-prod", access="read")
@grant_s3(bucket_name="documents-prod", access="read")
def physical_resources(event, context):
    return {"statusCode": 200, "body": "ok"}
```

Exactly one of the logical key (`resource_key`) and physical name must be
provided. `read` is a read grant; `write` represents the native cumulative
read/write grant. There is no third combined access value. These decorators record
intent and do not apply IAM by themselves.

For minimal custom IAM statements, use `permission`:

```python
from lambda_api_decorators import permission


@permission(actions=["events:PutEvents"], resources=["arn:aws:events:*:*:event-bus/orders"])
def publish(event, context):
    return {"statusCode": 202, "body": "accepted"}
```

Its contract is limited to `actions` and `resources`. It does not support
`conditions`, `principals`, `effect`, `not_actions`, or `sid`.

## Metadata model

Declarations are recorded in lexical order as independent invocations, while
the original callable and its behavior are preserved. This makes the metadata
straightforward to inspect without adding a runtime framework. The package is
deliberately CDK-free; infrastructure interpretation belongs to the separate
CDK package.

## Links

- [Documentation](https://infrastructure-as-decorator.github.io/)
- [Runtime package](https://github.com/infrastructure-as-decorator/lambda-api-decorators)
- [CDK package](https://github.com/infrastructure-as-decorator/lambda-api-decorators-cdk)
- [Integrated examples](https://github.com/infrastructure-as-decorator/lambda-api-decorators-examples)
- [Organization](https://github.com/infrastructure-as-decorator/)

## Releases

Tags are the source of the package version through `setuptools-scm`. Release
the runtime package independently from the CDK package:

```bash
git switch main
git pull --ff-only
git tag vX.Y.Z
git push origin vX.Y.Z
```

The release workflow validates the tag and uses PyPI trusted publishing.
