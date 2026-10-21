# Security and engineering verification

The [verification workflow](../.github/workflows/verify.yml) retains Python 3.12 and 3.13 on Linux and Windows. Every target installs the complete pinned runtime and developer toolchain, checks dependency compatibility, runs Ruff correctness/syntax rules over all source/scripts/tests, checks typed evidence/claim/empirical modules with mypy, runs tests and byte reproduction, and enforces branch-aware library coverage. This is engineering evidence. Economic and scientific claims remain subject to their own evidence and protocol gates.

## Reproduce the checks

Use a fresh virtual environment with Python 3.12 or 3.13:

```sh
python -m pip --isolated install --index-url https://pypi.org/simple --only-binary=:all: --no-deps -r requirements-lock.txt
python -m pip --isolated install --no-deps --no-build-isolation .
python -m pip check
python -m ruff check src scripts tests
python -m mypy
python -m coverage run scripts/reproduce.py --check
python -m coverage report
python -m pip_audit --strict --no-deps --disable-pip -r requirements-lock.txt
```

The [lock file](../requirements-lock.txt) pins all 46 runtime, build and developer distributions, including transitive dependencies. These are exact-version constraints, not a wheel-hash lock. PyPI wheel availability was checked for all four CI targets. Source builds are disabled during dependency installation, and project installation uses the already pinned build backend without dependency resolution. `pip check` detects incompatible or missing requirements. Dependency review is still necessary: exact versions and a clean advisory scan do not authenticate upstream packages or exclude undisclosed vulnerabilities.

Coverage measures every library module under `src/srl` with branches enabled. The 90% combined statement/branch threshold was chosen after measuring a 90.97% baseline, allowing a small regression margin across the supported platforms. No library module is omitted. CLI wrappers and tests are outside that library metric; their subprocess behavior is tested separately. Coverage does not measure assertion quality or establish scientific validity.

Mypy checks function bodies and requires annotations in the new evidence, claim and empirical modules. Older arithmetic/presentation modules remain covered by tests and whole-project Ruff checks; this is a stated typing boundary. Ruff selects `F` and `E9`, emphasizing undefined names, invalid syntax and related correctness findings. It is not a complete style or security review.

## Publication controls

GitHub's public-repository API was checked on 2026-10-21. Provider-pattern secret scanning, secret-scanning push protection, vulnerability alerts, Dependabot security updates and private vulnerability reporting were enabled and read back successfully. Non-provider-pattern scanning and validity checks were disabled in that snapshot; no broader detection is claimed. Repository settings can change independently of source files.

The verification workflow scans complete Git history with the MIT-licensed Gitleaks 8.30.1 CLI. Its Linux binary archive has an explicit upstream release SHA256, and findings are redacted. It uses the CLI directly without an organization action license or additional credential. The [CodeQL workflow](../.github/workflows/codeql.yml) analyzes Python with the security-extended query suite on pull requests, pushes to `main`, manual runs and a weekly schedule. CodeQL alone receives `security-events: write`; other jobs have read-only repository access. Checkout does not persist credentials. GitHub Actions are pinned to immutable commits verified against the official action repositories, with [Dependabot](../.github/dependabot.yml) proposing dependency/action updates for review.

Workflow files are configuration, not proof of a completed scan. Check the Actions results and security findings for the exact commit under review. Local checks confirmed no known vulnerabilities in the pinned dependency set and no Gitleaks findings in the then-current public history/working tree. The initial API snapshot returned no rulesets and `Branch not protected` for `main`; merge enforcement remains a separate setting. No scanner guarantees absence of secrets or vulnerabilities, and these controls do not authorize disclosure of third-party material.

For confidential reports, follow the [security policy](../SECURITY.md).
