# Agent guidance

- Use `lambda-api-decorators-development` when available and load this package's `_agent/api-contract.json` and `_agent/behavior.md` before changing public behavior.
- Keep this runtime package free of AWS CDK imports and AWS calls.
- Any public API change updates the contract and focused tests in the same change.
- Never put package versions, tags, commits, or future releases in the contract.
- Required checks: focused contract tests, full `pytest`, `python -m compileall -q src tests`, distribution artifact inspection, and `git diff --check`.
