# TEAMGASSER-FALL2025-SQA

- Team name: TEAMGASSER
- Team members: Will Gasser

## What this repo contains

- `MLForensics/MLForensics-farzana/` - provided project materials used for the assignment.
- `fuzz.py` - lightweight fuzzer that exercises five target methods and logs any anomalies.
- `SQA-REPO.md` - report summarizing quality activities and findings.
- `.github/workflows/ci.yml` - GitHub Actions workflow that installs dependencies and runs the fuzzer on every push or pull request.

## Running locally

```bash
python -m pip install -r requirements.txt
python fuzz.py
```

## CI build location

- GitHub Actions workflow: `.github/workflows/ci.yml` (builds appear in the Actions tab of this repo)
