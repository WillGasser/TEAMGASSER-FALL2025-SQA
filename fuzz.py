"""
Lightweight fuzzer for selected functions in the MLForensics project.

Targets:
 - mining.mining.makeChunks
 - mining.mining.days_between
 - mining.mining.dumpContentIntoFile
 - empirical.report.Average
 - empirical.report.Median
"""
from __future__ import annotations

import datetime as dt
import logging
import math
import os
import random
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List

# Ensure the project modules are importable when this script runs from repo root.
BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR / "MLForensics" / "MLForensics-farzana"
sys.path.append(str(PROJECT_DIR))

from mining import mining  # type: ignore  # namespace package without __init__
from empirical import report  # type: ignore  # namespace package without __init__


logging.basicConfig(
    level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s"
)
logger = logging.getLogger("fuzz")
random.seed(int(os.environ.get("FUZZ_SEED", "1337")))


def record_issue(
    issues: List[Dict[str, Any]],
    function_name: str,
    detail: str,
    payload: Any,
    error: Exception | None = None,
) -> None:
    issue = {"function": function_name, "detail": detail, "payload": payload}
    if error:
        issue["error"] = repr(error)
    issues.append(issue)


def fuzz_make_chunks(iterations: int = 200) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    for _ in range(iterations):
        list_len = random.randint(0, 40)
        data = [random.randint(-1000, 1000) for _ in range(list_len)]
        size = random.choice([0, -1, random.randint(1, max(1, list_len))])
        try:
            chunks = list(mining.makeChunks(data, size))
            flattened = [elem for chunk in chunks for elem in chunk]
            if size <= 0 and chunks != []:
                record_issue(
                    issues,
                    "makeChunks",
                    "Expected empty result when chunk size is non-positive",
                    {"size": size, "len": len(data), "result_len": len(chunks)},
                )
            if size > 0 and flattened != data:
                record_issue(
                    issues,
                    "makeChunks",
                    "Chunk reconstruction mismatch",
                    {"size": size, "original_len": len(data), "flattened_len": len(flattened)},
                )
        except Exception as exc:  # pragma: no cover - defensive fuzz logging
            record_issue(
                issues,
                "makeChunks",
                "Exception during chunking",
                {"size": size, "len": len(data)},
                exc,
            )
    return issues


def fuzz_days_between(iterations: int = 200) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    for _ in range(iterations):
        start_year = random.randint(1990, 2030)
        start_date = dt.datetime(
            start_year,
            random.randint(1, 12),
            random.randint(1, 28),
            random.randint(0, 23),
            random.randint(0, 59),
        )
        delta_days = random.randint(-1000, 1000)
        end_date = start_date + dt.timedelta(days=delta_days)
        try:
            result = mining.days_between(start_date, end_date)
            if result < 0:
                record_issue(
                    issues,
                    "days_between",
                    "Negative delta returned",
                    {"start": start_date.isoformat(), "end": end_date.isoformat(), "result": result},
                )
        except Exception as exc:  # pragma: no cover - defensive fuzz logging
            record_issue(
                issues,
                "days_between",
                "Exception during computation",
                {"start": start_date.isoformat(), "end": end_date.isoformat()},
                exc,
            )
    return issues


def fuzz_dump_content(iterations: int = 50) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    with tempfile.TemporaryDirectory() as temp_dir:
        for _ in range(iterations):
            content = "".join(chr(random.randint(32, 126)) for _ in range(random.randint(0, 2048)))
            file_path = Path(temp_dir) / f"fuzz-{random.randint(0, 999999)}.txt"
            try:
                written_size = int(mining.dumpContentIntoFile(content, str(file_path)))
                on_disk = file_path.stat().st_size
                if written_size != on_disk:
                    record_issue(
                        issues,
                        "dumpContentIntoFile",
                        "Reported size mismatch",
                        {"reported": written_size, "actual": on_disk, "path": str(file_path)},
                    )
            except Exception as exc:  # pragma: no cover - defensive fuzz logging
                record_issue(
                    issues,
                    "dumpContentIntoFile",
                    "Exception during write",
                    {"path": str(file_path), "len": len(content)},
                    exc,
                )
    return issues


def _generate_numeric_list() -> List[Any]:
    # Mix of ints, floats, and occasional non-numeric noise to stress input validation.
    options: List[Any] = [
        random.randint(-1000, 1000),
        random.random() * random.randint(-10, 10),
        "",
        None,
        "noise",
    ]
    return [random.choice(options) for _ in range(random.randint(0, 20))]


def fuzz_average(iterations: int = 200) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    for _ in range(iterations):
        payload = _generate_numeric_list()
        try:
            result = report.Average(payload)
            if isinstance(result, float) and math.isnan(result) and payload:
                record_issue(
                    issues,
                    "Average",
                    "Average returned NaN for payload with data",
                    payload,
                )
        except Exception as exc:  # pragma: no cover - defensive fuzz logging
            record_issue(issues, "Average", "Exception during average", payload, exc)
    return issues


def fuzz_median(iterations: int = 200) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    for _ in range(iterations):
        payload = _generate_numeric_list()
        try:
            result = report.Median(payload)
            if isinstance(result, float) and math.isnan(result) and payload:
                record_issue(
                    issues,
                    "Median",
                    "Median returned NaN for payload with data",
                    payload,
                )
        except Exception as exc:  # pragma: no cover - defensive fuzz logging
            record_issue(issues, "Median", "Exception during median", payload, exc)
    return issues


def main() -> int:
    fuzzers = [
        ("makeChunks", fuzz_make_chunks),
        ("days_between", fuzz_days_between),
        ("dumpContentIntoFile", fuzz_dump_content),
        ("Average", fuzz_average),
        ("Median", fuzz_median),
    ]
    all_issues: List[Dict[str, Any]] = []
    for name, func in fuzzers:
        logger.info("Starting fuzzer for %s", name)
        issues = func()
        if issues:
            logger.warning("Found %s potential issues while fuzzing %s", len(issues), name)
            all_issues.extend(issues)
        else:
            logger.info("No issues detected for %s", name)
    if all_issues:
        logger.info("Fuzzing completed with %s total findings.", len(all_issues))
        for issue in all_issues:
            logger.info("Issue: %s", issue)
    else:
        logger.info("Fuzzing completed with no findings.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
