# Lambda API Decorators

**Define AWS Lambda API routes and configuration directly in your Python code using decorators.**

Lambda API Decorators provides Python decorators for defining API routes and AWS Lambda configuration alongside your Lambda handlers.

Instead of maintaining route and function configuration separately from your application code, you can declare HTTP methods, paths, runtimes, timeouts, memory, environment variables, layers, networking, and other Lambda settings directly on the handler.

Combined with **Lambda API Decorators CDK**, these definitions are used to automatically generate the corresponding AWS Lambda and Amazon API Gateway infrastructure with AWS CDK.

```python
from lambda_api_decorators import GET, runtime, name, memory_size
import json


@GET("/dogs")
@runtime("python3.11")
@name("LBD-DOGS-GET")
@memory_size(256)
def lambda_handler(event, context):
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Hello World from /dogs!"
        })
    }
```

## Installation

Install Lambda API Decorators from PyPI:

```bash
pip install lambda-api-decorators
```

To generate AWS infrastructure from the decorated Lambda handlers, install the CDK integration:

```bash
pip install lambda-api-decorators-cdk
```

## Available Decorators

### API Routes

Every Lambda API handler must define an HTTP method and endpoint path.

Available route decorators:

* `GET`
* `POST`
* `PUT`
* `DELETE`
* `ANY`

For example:

```python
@GET("/dogs")
def lambda_handler(event, context):
    ...
```

The route definition is used by the CDK integration to configure the corresponding Amazon API Gateway endpoint and Lambda integration.

### Lambda Configuration

Lambda API Decorators also allows Lambda configuration to be declared directly on the handler.

#### `timeout`

Defines the Lambda function timeout in seconds.

```python
@timeout(30)
```

#### `memory_size`

Defines the amount of memory allocated to the Lambda function.

```python
@memory_size(512)
```

#### `name`

Defines a custom name for the Lambda function.

```python
@name("LBD-DOGS-GET")
```

#### `description`

Defines the Lambda function description.

```python
@description("Returns the list of dogs")
```

#### `runtime`

References a runtime configuration defined by Lambda API Decorators CDK.

```python
@runtime("python3.11")
```

#### `role`

References an IAM role defined by Lambda API Decorators CDK.

```python
@role("api-role")
```

#### `vpc`

References a VPC configuration defined by Lambda API Decorators CDK.

```python
@vpc("application-vpc")
```

#### `environment`

Associates one or more environment configurations with the Lambda function.

```python
@environment("database", "application")
```

#### `layer`

Associates one or more Lambda Layers with the function.

```python
@layer("common-dependencies")
```

#### `security_group`

Associates one or more security group configurations with the Lambda function.

```python
@security_group("lambda-security-group")
```

The referenced runtimes, IAM roles, VPCs, environment configurations, layers, and security groups are defined in the AWS CDK application using **Lambda API Decorators CDK**.

## How It Works

Lambda API Decorators keeps API and Lambda configuration close to the application code:

```text
Python Lambda handlers
        │
        │  @GET, @POST, @runtime,
        │  @timeout, @memory_size, ...
        ▼
Lambda API Decorators
        │
        ▼
Lambda API Decorators CDK
        │
        ▼
AWS CDK
        │
        ├── AWS Lambda
        ├── Amazon API Gateway
        ├── IAM
        ├── VPC configuration
        └── other AWS resources
```

This allows your Lambda handlers to become the source of the API definition while AWS CDK remains responsible for generating and deploying the infrastructure.

## Related Projects

* **Lambda API Decorators CDK** — AWS CDK integration that generates Lambda and API Gateway infrastructure from decorated Python handlers.
* **Lambda API Decorators Examples** — Example applications demonstrating how to use Lambda API Decorators.

## License

See the repository license for details.
