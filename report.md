# Report

## Setup
- Unpacked the project and set the repo name.
- Wrote a short README and added the quality notes file.

## Fuzzing
- Implemented `fuzz.py` to target five functions: `makeChunks`, `days_between`, `dumpContentIntoFile`, `Average`, and `Median`.
- Used randomized inputs and collected issues instead of crashing.
- Findings: `Average` and `Median` return `NaN` when payloads have no numeric values. Other targets did not crash.

## Logging
- Added logging to five methods:
  - `dumpContentIntoFile` logs bytes written and path.
  - `makeChunks` logs chunk size use and warns on non-positive sizes.
  - `days_between` logs day deltas and exceptions.
  - `Average` and `Median` log when inputs are empty or non-numeric.
- This helps trace inputs and outputs when something goes wrong.

## Continuous integration
- Added GitHub Actions workflow to install requirements, run `python fuzz.py`, and compile the code.
- Builds show up in the Actions tab for this repo.

## Lessons learned
- Simple fuzzing surfaces weak spots quickly without heavy setup.
- Light logging gives enough context to debug without stepping through code.
- Keeping CI small makes runs fast and easy to fix.
