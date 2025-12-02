# Software Quality Activities

## What I did
- Added `fuzz.py` to automatically fuzz five methods (`makeChunks`, `days_between`, `dumpContentIntoFile`, `Average`, `Median`) with randomized inputs and capture issues instead of crashing.
- Instrumented five methods with forensic logging to trace inputs and edge cases in `mining/mining.py` and `empirical/report.py`.
- Created CI at `.github/workflows/ci.yml` to install dependencies, run the fuzzer, and compile sources on every push/PR.
- Documented repo usage in `README.md` and captured results here.

## Fuzzing results
- 200+ iterations per target; no crashes or unhandled exceptions.
- `makeChunks`: non-positive chunk sizes now emit warnings and return an empty iterator; all other inputs reconstructed correctly.
- `days_between` and `dumpContentIntoFile`: no issues detected.
- `Average` (24 findings) and `Median` (13 findings): when payloads contained only non-numeric values or were empty, the functions returned `NaN` and logged warnings. This behavior is now explicit, but callers should filter inputs or handle `NaN`.

## Logging integration
- `mining.dumpContentIntoFile` now logs bytes written and destination.
- `mining.makeChunks` logs chunking behavior and warns on invalid sizes.
- `mining.days_between` logs computed deltas and surfaces failures with stack traces.
- `report.Average` and `report.Median` log input validation details and warn when data is missing or non-numeric.

## How to run locally
```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python fuzz.py
```

## CI location
- Workflow: `.github/workflows/ci.yml`
- Job installs requirements, runs `python fuzz.py`, and compiles sources to catch syntax errors.

## Lessons learned
- Fuzzing simple utility methods quickly surfaces validation gaps and documents expected behavior on malformed inputs.
- Lightweight logging gives immediate forensic breadcrumbs without heavy dependencies.
- Keeping CI compact ensures fast feedback while still exercising the added instrumentation.
