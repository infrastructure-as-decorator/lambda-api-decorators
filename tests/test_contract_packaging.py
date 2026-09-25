import json
import types
from pathlib import Path


def test_public_contract_is_present_and_version_free():
    contract_path = Path(__file__).parents[1] / "src/lambda_api_decorators/_agent/api-contract.json"
    behavior_path = contract_path.with_name("behavior.md")
    contract = json.loads(contract_path.read_text())
    assert contract["schema_version"] == "1.0"
    assert "version" not in contract
    assert behavior_path.read_text().strip()
    assert {"GET", "current_user", "CurrentUser", "CurrentUserError"}.issubset(contract["exports"])


def test_contract_declares_all_package_root_exports():
    import lambda_api_decorators as package

    contract_path = Path(__file__).parents[1] / "src/lambda_api_decorators/_agent/api-contract.json"
    exports = set(json.loads(contract_path.read_text())["exports"])
    package_exports = {name for name in vars(package) if not name.startswith("_") and not isinstance(getattr(package, name), types.ModuleType)}
    assert exports <= package_exports
