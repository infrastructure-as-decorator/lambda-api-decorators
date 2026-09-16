# Lambda API Decorators

**Declare AWS Lambda API routes, authentication, and configuration directly in Python.**

Lambda API Decorators is a small, CDK-free Python library. Its decorators record
API and Lambda configuration on your handler without wrapping or replacing the
callable. An infrastructure tool such as
[Lambda API Decorators CDK](https://github.com/lambda-api-decorators/lambda-api-decorators-cdk)
can consume those declarations to build AWS Lambda and API Gateway resources.

## Installation

Install the decorators package from PyPI:

```bash
pip install lambda-api-decorators
```

If you want to generate AWS infrastructure from the declarations, install the
optional CDK integration separately:

```bash
pip install lambda-api-decorators-cdk
```

The package supports Python 3.9 through Python 3.14 and has no runtime CDK
dependency.

## Quick start

```python
import json

from lambda_api_decorators import GET, memory_size, runtime, timeout


@GET("/dogs")
@runtime("python3.12")
@timeout(30)
@memory_size(256)
def lambda_handler(event, context):
    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Hello from /dogs"}),
    }
```

The decorators retain their normal function behavior. They only attach an
ordered collection of declarations for an infrastructure consumer to inspect.
You can stack multiple route and configuration decorators on one handler.

## API routes

The route decorators are:

* `GET(path)`
* `POST(path)`
* `PUT(path)`
* `DELETE(path)`
* `ANY(path)`

```python
@GET("/dogs")
def list_dogs(event, context):
    ...


@POST("/dogs")
def create_dog(event, context):
    ...
```

## Lambda configuration

The following decorators declare Lambda properties or references to resources
defined by the infrastructure integration:

* `runtime(value)`
* `timeout(seconds)`
* `memory_size(megabytes)`
* `name(value)`
* `description(value)`
* `role(resource_key)`
* `vpc(resource_key)`
* `environment(*resource_keys, **values)`
* `layer(*resource_keys, **values)`
* `security_group(*resource_keys)`

For example:

```python
from lambda_api_decorators import (
    GET,
    environment,
    layer,
    name,
    role,
    security_group,
    vpc,
)


@GET("/orders")
@name("orders-api")
@role("api-role")
@vpc("application-vpc")
@security_group("lambda-security-group")
@environment("database", "application")
@layer("common-dependencies")
def get_orders(event, context):
    ...
```

The meaning of resource keys is defined by the infrastructure consumer. This
package does not create or look up AWS resources itself.

## Authentication

Use `authorizer(key)` to associate a route with an authorizer configuration, or
use the bare `@public` decorator for a public route. A handler can have only
one authentication declaration.

```python
from lambda_api_decorators import GET, authorizer, public


@GET("/profile")
@authorizer("users")
def profile(event, context):
    ...


@GET("/health")
@public
def health(event, context):
    ...
```

`current_user(event)` extracts an already-validated identity from API Gateway
authorizer claims. It supports REST API claims and HTTP API JWT claims:

```python
from lambda_api_decorators import current_user


def profile(event, context):
    user = current_user(event)
    return {"statusCode": 200, "body": user.subject}
```

The returned `CurrentUser` contains `subject`, an optional `username`, and a
read-only snapshot of `claims`. `current_user` does not authenticate tokens or
authorize actions; malformed or missing identity data raises
`CurrentUserError`.

## Permissions

Declare resource access with the convenience decorators `grant_dynamodb` and
`grant_s3`. Address a resource by its logical `resource_key` or by its physical
name, and choose `read` or `write` access:

```python
from lambda_api_decorators import GET, grant_dynamodb, grant_s3


@GET("/documents")
@grant_dynamodb("orders", "read")
@grant_s3(bucket_name="documents-prod", access="read")
def documents(event, context):
    ...
```

For an explicit IAM action/resource statement, use `permission`:

```python
from lambda_api_decorators import permission


@permission(
    actions=["events:PutEvents"],
    resources=["arn:aws:events:us-east-1:123456789012:event-bus/orders"],
)
def publish_order(event, context):
    ...
```

`grant_dynamodb`, `grant_s3`, and `permission` only declare intent. The
infrastructure integration is responsible for translating that intent into
IAM policies.

## How it fits together

```text
Python handler
    │  @GET, @authorizer, @runtime, @permission, ...
    ▼
Lambda API Decorators
    │  ordered, CDK-free declarations
    ▼
Infrastructure consumer (for example Lambda API Decorators CDK)
    ▼
AWS Lambda, API Gateway, IAM, VPC, and other resources
```

## Related projects

* [Lambda API Decorators CDK](https://github.com/lambda-api-decorators/lambda-api-decorators-cdk) — CDK integration that consumes handler declarations.
* [Lambda API Decorators Examples](https://github.com/lambda-api-decorators/lambda-api-decorators-examples) — example applications.

## Releasing

The Git tag is the source of truth for this package's version. Maintainers
create and push a semantic-version tag from `main`:

```bash
git checkout main
git pull

git tag v0.2.0
git push origin v0.2.0
```

Pushing the tag starts the release workflow, and `v0.2.0` becomes Python package
version `0.2.0`. Versions in this repository are independent from
`lambda-api-decorators-cdk`.

Publishing uses PyPI trusted publishing. The PyPI project must have a trusted
publisher configured for this repository, the `release.yml` workflow, and the
`pypi` GitHub environment.

## License

See [LICENSE](LICENSE) for details.
