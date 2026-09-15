import ast
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_DISTRIBUTIONS = {
    "aws-cdk-lib",
    "aws_cdk",
    "constructs",
    "jsii",
    "lambda-api-decorators-cdk",
    "boto3",
    "aws-lambda-powertools",
    "pydantic",
    "pyjwt",
}
FORBIDDEN_MODULES = {
    "aws_cdk",
    "constructs",
    "jsii",
    "lambda_api_decorators_cdk",
    "boto3",
    "aws_lambda_powertools",
    "pydantic",
    "jwt",
}


def test_runtime_dependencies_are_cdk_free():
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r"(?ms)^dependencies\s*=\s*\[(.*?)^\]", pyproject)
    assert match is not None
    dependencies = set(re.findall(r'["\u0027]([^"\u0027]+)["\u0027]', match.group(1).lower()))
    assert dependencies.isdisjoint(FORBIDDEN_DISTRIBUTIONS)


def test_production_source_has_no_cdk_imports():
    violations = []
    for path in (ROOT / "src").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules = [alias.name.split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules = [node.module.split(".")[0]]
            else:
                modules = []
            for module in modules:
                if module in FORBIDDEN_MODULES:
                    violations.append("{}:{}:{}".format(path, node.lineno, module))
    assert not violations


def test_package_import_succeeds_when_cdk_imports_are_blocked():
    script = """
import builtins

forbidden_modules = {forbidden_modules!r}
real_import = builtins.__import__


def reject_forbidden_imports(name, *args, **kwargs):
    if name.split('.')[0] in forbidden_modules:
        raise AssertionError('package attempted to import {{}}'.format(name))
    return real_import(name, *args, **kwargs)


builtins.__import__ = reject_forbidden_imports
import lambda_api_decorators
""".format(forbidden_modules=FORBIDDEN_MODULES)

    subprocess.run([sys.executable, "-c", script], check=True)
