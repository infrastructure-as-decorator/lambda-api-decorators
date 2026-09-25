# Runtime behavior

## Declarations

Decorators prepend immutable declaration metadata to the callable. A callable may declare exactly one HTTP route among `GET`, `POST`, `PUT`, `DELETE`, and `ANY`, and exactly one authentication declaration (`authorizer` or `public`). `@public` means the callable has no authorizer declaration; it does not authenticate or grant permissions.

## Identity

`current_user` reads identity claims that an API Gateway authorizer has already supplied. It supports REST-style `authorizer.claims` and HTTP API JWT-style `authorizer.jwt.claims`, requires a non-empty string `sub`, and returns an immutable claims mapping. It does not validate tokens or authorize actions. Missing or malformed context raises `CurrentUserError`.

## Permissions

`read` and `write` are the public access values for resource grants. A grant names either a logical `resource_key` or a physical resource name, never both. `write` is cumulative where the CDK implementation applies permissions. Registries resolve resources; they are not authorization decisions. Generic `permission` declares explicit IAM action/resource pairs.
