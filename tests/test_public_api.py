import lambda_api_decorators as package


PUBLIC_DECORATORS = {
    "GET", "POST", "PUT", "DELETE", "ANY", "runtime", "timeout",
    "memory_size", "role", "vpc", "environment", "layer",
    "security_group", "name", "description", "grant_dynamodb",
    "grant_s3", "permission", "authorizer", "public",
}


def test_package_root_exports_all_public_decorators():
    missing = PUBLIC_DECORATORS.difference(vars(package))
    assert not missing
    assert all(callable(getattr(package, name)) for name in PUBLIC_DECORATORS)
