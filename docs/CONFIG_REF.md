sswg-mvm; version 1.0+ (living document)
Date: 05-03-2025
Document title: Configuration Reference
Author: Tommy Raven
Licensing: Raven Recordings ©️ see: *LICENSE.md*
(Document) Purpose: Capture the configuration surfaces that drive the SSWG-MVM, including environment variables, schema files, and runtime options. Keep SSWG as the topic base multiplier across phases by highlighting where settings influence recursion, evaluation, and memory. Tie readers back to the root [README](../README.md) and [docs/README.md](./README.md) for full execution flow.

# Configuration Reference — SSWG-MVM

## Overview

This document outlines configuration files, environment settings, and schema references for the **SSWG-MVM**. Proper configuration ensures deterministic execution, reproducibility, and safe workflow generation while preserving the SSWG anchor during recursive passes.

---

## Configuration Files

| File                 | Purpose                                       |
| -------------------- | --------------------------------------------- |
| `requirements.txt`   | Python dependencies                           |
| `pyproject.toml`     | Build and packaging configuration             |
| `.editorconfig`      | Code formatting standards                     |
| `.gitignore`         | File exclusion for version control            |
| `config/` (optional) | Runtime, environment, and path configurations |

---

## JSON Schemas

| Schema                           | Description                                                              |
| -------------------------------- | ------------------------------------------------------------------------ |
| `schemas/workflow_schema.json`   | Defines structure, required fields, and dependencies for workflows       |
| `schemas/module_schema.json`     | Validates individual modules for naming, inputs, and outputs             |
| `schemas/evaluation_schema.json` | Ensures evaluation metrics and feedback loops conform to expected format |

---

## Environment Variables

* `RECURSIVE_MODE` — Enables recursive expansion on workflow generation
* `MEMORY_PATH` — Path to persistent memory storage (`ai_memory/`)
* `LOG_LEVEL` — Logging verbosity (`INFO`, `DEBUG`, `WARNING`, `ERROR`)
* `API_HOST` — Host for FastAPI endpoints
* `API_PORT` — Port for FastAPI endpoints

---

## Onboarding Highlights

* Each workflow phase may read configuration files for parameterization.
* JSON schema validation ensures module and workflow integrity.
* Environment variables allow safe toggling of recursive execution and memory tracking.
* Recommended workflow: clone → configure environment → validate schemas → run CLI or API.
