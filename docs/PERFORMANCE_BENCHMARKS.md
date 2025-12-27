# Performance Benchmarks

This document tracks memory usage, recursion time, module reuse, and throughput efficiency across workflow generations. Benchmarks are used to guide optimization, ensure deterministic execution, and evaluate system evolution.

## 🧠 Benchmark Metrics

| Metric                | Description                                                    | Notes                                                                 |
| --------------------- | -------------------------------------------------------------- | --------------------------------------------------------------------- |
| Recursion Time        | Total runtime per generation cycle                             | Measured from workflow initialization to final output persistence     |
| Cache Hits            | Number of reused modules or workflows                          | Indicates efficiency of modularization and memory reuse               |
| Memory Usage          | RAM consumption in MB                                          | Includes active data, memory store, and evaluation overhead           |
| Semantic Stability    | Average delta between iterations                               | Helps determine when recursion output has stabilized                  |
| IO Throughput         | Reads/writes per workflow cycle                                | Tracks template and output handling performance                       |
| Phase Completion Time | Per-phase runtime                                              | Identifies bottlenecks in initialization, evaluation, or regeneration |
| Evaluation Overhead   | Runtime of clarity, expandability, and translatability scoring | Monitors impact of metric calculations on total cycle                 |

## 📊 Recording & Reporting

* Benchmarks are collected in `ai_memory/benchmark_tracker.py`.
* Data is logged with timestamps, version IDs, and phase markers.
* CLI dashboard and visualization tools display performance trends.
* Metrics support adaptive optimization, such as caching strategies, async execution, and semantic delta stopping.

## 📌 Profiling Snapshots (2025-12-27)

**Methodology**

* Workloads: `campfire_workflow.json` and `technical_procedure_template.json` from `data/templates/`.
* Phases measured: load workflow, normalize task packaging, inheritance checks, schema validation, dependency graph build, mermaid render, evaluation scoring, meta metrics, and export artifacts.
* Timing: `time.perf_counter()` per phase.
* Memory: `tracemalloc` per phase (reported in KiB; captures Python allocation peaks).
* Schema validation attempts may include remote `$ref` resolution; the snapshot records any validation exception text.

**Artifacts**

* Snapshot JSON: [`data/profiling/workflow_profiling_2025-12-27.json`](../data/profiling/workflow_profiling_2025-12-27.json)
* Campfire outputs:
  * [`data/profiling/campfire_workflow/campfire_workflow.json`](../data/profiling/campfire_workflow/campfire_workflow.json)
  * [`data/profiling/campfire_workflow/campfire_workflow.md`](../data/profiling/campfire_workflow/campfire_workflow.md)
* Technical procedure outputs:
  * [`data/profiling/technical_procedure_template/unnamed_workflow.json`](../data/profiling/technical_procedure_template/unnamed_workflow.json)
  * [`data/profiling/technical_procedure_template/unnamed_workflow.md`](../data/profiling/technical_procedure_template/unnamed_workflow.md)

## ⚡ Optimization Integration

* Core stability and exception handling minimize runtime errors and infinite loops.
* Semantic intelligence and delta scoring inform adaptive recursion termination.
* Memory caching and garbage collection reduce overhead for large workflow sets.
* Multithreaded execution increases throughput for parallel workflow generation.
* Persistent memory analytics support long-term performance improvements.
