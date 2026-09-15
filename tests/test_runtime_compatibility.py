import ast
from pathlib import Path
import re


PYPROJECT = Path(__file__).parents[1] / "pyproject.toml"
SUPPORTED_PYTHON_VERSIONS = ("3.9", "3.10", "3.11", "3.12", "3.13", "3.14")


def _pyproject_text():
    return PYPROJECT.read_text(encoding="utf-8")


def test_requires_python_retains_python_39_compatibility():
    match = re.search(
        r'^requires-python\s*=\s*"([^"]+)"', _pyproject_text(), re.MULTILINE
    )

    assert match is not None
    assert match.group(1) == ">=3.9"


def test_classifiers_declare_every_supported_python_runtime():
    match = re.search(
        r"(?ms)^classifiers\s*=\s*(\[.*?^\])", _pyproject_text()
    )

    assert match is not None
    classifiers = ast.literal_eval(match.group(1))
    python_classifiers = {
        classifier
        for classifier in classifiers
        if classifier.startswith("Programming Language :: Python :: 3.")
    }
    assert python_classifiers == {
        "Programming Language :: Python :: {}".format(version)
        for version in SUPPORTED_PYTHON_VERSIONS
    }
