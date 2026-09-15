import lambda_api_decorators as package


PUBLIC_DECORATORS = {
    "GET", "POST", "PUT", "DELETE", "ANY", "runtime", "timeout",
    "memory_size", "role", "vpc", "environment", "layer",
    "security_group", "name", "description", "grant_dynamodb",
    "grant_s3", "permission", "authorizer", "public",
}

PUBLIC_IDENTITY_API = {"CurrentUser", "CurrentUserError", "current_user"}


def test_package_root_exports_all_public_decorators():
    missing = PUBLIC_DECORATORS.difference(vars(package))
    assert not missing
    assert all(callable(getattr(package, name)) for name in PUBLIC_DECORATORS)


def test_package_root_exports_identity_api_from_identity_module():
    identity = __import__("lambda_api_decorators.identity", fromlist=["identity"])

    missing = PUBLIC_IDENTITY_API.difference(vars(package))
    assert not missing
    assert all(getattr(package, name) is getattr(identity, name) for name in PUBLIC_IDENTITY_API)
