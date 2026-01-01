#!/usr/bin/env python3
"""
Reproducible benchmarking pipeline for sswg-mvm.

This script measures deterministic IO throughput, phase timing
proxies for the canonical 9-phase pipeline, and a deterministic
recursion loop. Outputs are written as a JSON artifact that mirrors
existing performance benchmark reports.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict

import yaml

from generator.pdl_validator import PDLValidationError, validate_pdl_file

PHASE_ORDER = (
    "normalize",
    "parse",
    "analyze",
    "generate",
    "validate",
    "compare",
    "interpret",
    "log",
)


@dataclass(frozen=True)
class BenchmarkConfig:
    pdl_path: Path
    schema_dir: Path
    output_path: Path
    run_id: str
    timestamp_utc: str
    io_read_iterations: int
    io_write_iterations: int
    phase_iterations: int
    recursion_iterations: int
    resolve_handlers: bool


def _hash_bytes(payload: bytes) -> str:
    digest = hashlib.sha256()
    digest.update(payload)
    return digest.hexdigest()


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_dataset(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _dataset_metadata(path: Path) -> Dict[str, Any]:
    payload = path.read_bytes()
    return {
        "path": str(path.resolve()),
        "bytes": len(payload),
        "lines": payload.count(b"\n") + (1 if payload else 0),
        "sha256": _hash_bytes(payload),
    }


def _format_timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _memory_bytes() -> int:
    if hasattr(os, "sysconf"):
        try:
            page_size = os.sysconf("SC_PAGE_SIZE")
            pages = os.sysconf("SC_PHYS_PAGES")
            if isinstance(page_size, int) and isinstance(pages, int):
                return page_size * pages
        except (ValueError, OSError):
            return 0
    return 0


def _environment_metadata() -> Dict[str, Any]:
    return {
        "os": platform.platform(),
        "kernel": platform.release(),
        "machine": platform.machine(),
        "cpu_model": platform.processor() or "unknown",
        "cpu_count": os.cpu_count() or 0,
        "memory_bytes": _memory_bytes(),
        "python_version": platform.python_version(),
    }


def _time_loop(iterations: int, func: Callable[[], None]) -> float:
    start = time.perf_counter()
    for _ in range(iterations):
        func()
    return time.perf_counter() - start


def _io_read_benchmark(payload: str, iterations: int) -> Dict[str, float]:
    payload_bytes = payload.encode("utf-8")

    def _read() -> None:
        _hash_bytes(payload_bytes)

    elapsed = _time_loop(iterations, _read)
    mb = len(payload_bytes) * iterations / (1024 * 1024)
    mb_s = mb / elapsed if elapsed > 0 else 0.0
    return {"mb_s": mb_s, "seconds": elapsed}


def _io_write_benchmark(payload: str, iterations: int) -> Dict[str, float]:
    payload_bytes = payload.encode("utf-8")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / "benchmark_payload.yaml"

        def _write() -> None:
            tmp_path.write_bytes(payload_bytes)

        elapsed = _time_loop(iterations, _write)
    mb = len(payload_bytes) * iterations / (1024 * 1024)
    mb_s = mb / elapsed if elapsed > 0 else 0.0
    return {"mb_s": mb_s, "seconds": elapsed}


def _phase_timings(
    *,
    payload: str,
    parsed: Dict[str, Any],
    config: BenchmarkConfig,
) -> Dict[str, float]:
    normalized = payload.strip()
    generated = json.dumps(parsed, sort_keys=True)

    def _normalize() -> None:
        _ = normalized.lower()

    def _parse() -> None:
        _ = yaml.safe_load(payload)

    def _analyze() -> None:
        _ = sum(len(str(k)) + len(str(v)) for k, v in parsed.items())

    def _generate() -> None:
        _ = json.dumps(parsed, sort_keys=True)

    def _validate() -> None:
        validate_pdl_file(
            config.pdl_path,
            schema_dir=config.schema_dir,
            resolve_handlers=config.resolve_handlers,
        )

    def _compare() -> None:
        _ = _hash_bytes(generated.encode("utf-8"))

    def _interpret() -> None:
        _ = f"phase-count:{len(parsed.get('phases', []))}"

    def _log() -> None:
        _ = {
            "run_id": config.run_id,
            "inputs_hash": _hash_bytes(payload.encode("utf-8")),
        }

    timings: Dict[str, float] = {}
    phase_funcs = {
        "normalize": _normalize,
        "parse": _parse,
        "analyze": _analyze,
        "generate": _generate,
        "validate": _validate,
        "compare": _compare,
        "interpret": _interpret,
        "log": _log,
    }

    for phase in PHASE_ORDER:
        func = phase_funcs[phase]
        elapsed = _time_loop(config.phase_iterations, func)
        avg = elapsed / config.phase_iterations if config.phase_iterations else 0.0
        timings[f"{phase}_total"] = elapsed
        timings[f"{phase}_avg"] = avg

    return timings


def _recursion_timing(parsed: Dict[str, Any], iterations: int) -> Dict[str, float]:
    def _recursion_cycle() -> None:
        digest = hashlib.sha256()
        for key in sorted(parsed.keys()):
            digest.update(str(key).encode("utf-8"))
            digest.update(str(parsed[key]).encode("utf-8"))
        _ = digest.hexdigest()

    elapsed = _time_loop(iterations, _recursion_cycle)
    avg = elapsed / iterations if iterations else 0.0
    return {"total": elapsed, "avg_per_iteration": avg}


def _build_output(config: BenchmarkConfig) -> Dict[str, Any]:
    payload = _read_dataset(config.pdl_path)
    parsed = yaml.safe_load(payload)
    if not isinstance(parsed, dict):
        raise ValueError("PDL dataset must parse to a mapping object")

    validate_pdl_file(
        config.pdl_path,
        schema_dir=config.schema_dir,
        resolve_handlers=config.resolve_handlers,
    )

    io_read = _io_read_benchmark(payload, config.io_read_iterations)
    io_write = _io_write_benchmark(payload, config.io_write_iterations)
    phase_timings = _phase_timings(payload=payload, parsed=parsed, config=config)
    recursion_timings = _recursion_timing(parsed, config.recursion_iterations)

    return {
        "anchor": {
            "anchor_id": "performance_benchmark_results",
            "anchor_version": "1.0.0",
            "scope": "benchmarking",
            "owner": "scripts.benchmark_pipeline",
            "status": "draft",
        },
        "run": {
            "timestamp_utc": config.timestamp_utc,
            "run_id": config.run_id,
            "working_directory": str(Path.cwd().resolve()),
            "inputs_hash": _hash_file(config.pdl_path),
        },
        "environment": _environment_metadata(),
        "dataset": _dataset_metadata(config.pdl_path),
        "configuration": {
            "io_read_iterations": config.io_read_iterations,
            "io_write_iterations": config.io_write_iterations,
            "phase_iterations": config.phase_iterations,
            "recursion_iterations": config.recursion_iterations,
            "resolve_handlers": config.resolve_handlers,
        },
        "throughput": {
            "io_read_mb_s": io_read["mb_s"],
            "io_write_mb_s": io_write["mb_s"],
            "io_read_seconds": io_read["seconds"],
            "io_write_seconds": io_write["seconds"],
        },
        "phase_timings_seconds": phase_timings,
        "recursion_timings_seconds": recursion_timings,
    }


def _parse_args() -> BenchmarkConfig:
    parser = argparse.ArgumentParser(
        description="Reproducible benchmark pipeline for sswg-mvm.",
    )
    parser.add_argument(
        "--pdl",
        type=Path,
        default=Path("pdl/example_full_9_phase.yaml"),
        help="Path to the PDL dataset file.",
    )
    parser.add_argument(
        "--schemas",
        type=Path,
        default=Path("schemas"),
        help="Directory containing PDL schemas.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output JSON path. Defaults to artifacts/performance/benchmarks_<timestamp>.json.",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default="local-run",
        help="Run identifier for report metadata.",
    )
    parser.add_argument(
        "--timestamp-utc",
        type=str,
        default=None,
        help="Override UTC timestamp (YYYY-MM-DDTHH:MM:SSZ).",
    )
    parser.add_argument(
        "--io-read-iterations",
        type=int,
        default=2000,
        help="Number of IO read iterations.",
    )
    parser.add_argument(
        "--io-write-iterations",
        type=int,
        default=500,
        help="Number of IO write iterations.",
    )
    parser.add_argument(
        "--phase-iterations",
        type=int,
        default=200,
        help="Number of iterations per phase timing.",
    )
    parser.add_argument(
        "--recursion-iterations",
        type=int,
        default=50,
        help="Number of iterations in recursion timing loop.",
    )
    parser.add_argument(
        "--resolve-handlers",
        action="store_true",
        default=True,
        help="Resolve handler paths during validation (default: enabled).",
    )
    parser.add_argument(
        "--no-resolve-handlers",
        dest="resolve_handlers",
        action="store_false",
        help="Disable handler resolution checks.",
    )

    args = parser.parse_args()
    timestamp_utc = args.timestamp_utc or _format_timestamp()
    output_path = args.output
    if output_path is None:
        output_dir = Path("artifacts/performance")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"benchmarks_{timestamp_utc.replace(':', '').replace('-', '').replace('Z', '')}.json"

    return BenchmarkConfig(
        pdl_path=args.pdl,
        schema_dir=args.schemas,
        output_path=output_path,
        run_id=args.run_id,
        timestamp_utc=timestamp_utc,
        io_read_iterations=args.io_read_iterations,
        io_write_iterations=args.io_write_iterations,
        phase_iterations=args.phase_iterations,
        recursion_iterations=args.recursion_iterations,
        resolve_handlers=args.resolve_handlers,
    )


def main() -> int:
    config = _parse_args()
    try:
        report = _build_output(config)
    except (OSError, ValueError, PDLValidationError, yaml.YAMLError) as exc:
        print(f"Benchmark pipeline failed: {exc}")
        return 1

    config.output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Benchmark report written to {config.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
