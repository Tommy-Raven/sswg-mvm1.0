# ai_recursive — Recursive Refinement Layer (SSWG MVM)

The `ai_recursive` package is responsible for **iterative improvement** of
workflows:

- Generate multiple candidate variants.
- Compare them against the current version and each other.
- Merge the best ideas into a new child workflow.
- Record version lineage for future analysis.

At the MVM stage, recursion is intentionally conservative and transparent.

---

## Components

### 1. `variant_generator.py`

**Role:** Create alternative workflow variants from a base workflow.

MVM behavior:

- Accepts a workflow dict and a `num_variants` parameter.
- Returns a list of shallowly modified copies (e.g. different titles,
  small changes to metadata or module descriptions).
- Stubbed to be deterministic and safe; real generative logic can be
  plugged in later.

---

### 2. `version_diff_engine.py`

**Role:** Compare two workflow versions.

Responsibilities:

- Compute a structured diff between:
  - metadata
  - phases
  - modules
- Return a dict describing added/removed/changed elements.

Supports higher-level tools (history, version control, merge engine).

---

### 3. `merge_engine.py`

**Role:** Merge multiple variants into a single improved workflow.

MVM behavior:

- Start from a base workflow.
- For each variant:
  - merge metadata additions (non-conflicting keys)
  - prefer “longer” descriptions where appropriate
- Output a new workflow dict that preserves `workflow_id` and updates
  version/metadata explicitly.

Real-world merging logic can become more sophisticated over time.

---

### 4. `memory_adapter.py`

**Role:** Connect recursion with memory/history.

Responsibilities:

- Provide helpers to:
  - store variants in a memory store
  - retrieve previous versions
  - look up “best known” versions by id

At MVM, this is a thin wrapper that talks to `ai_memory` or
`generator/history` without creating a hard dependency tangle.

---

### 5. `version_control.py`

**Role:** Manage version naming and lineage.

Responsibilities:

- Provide `VersionController` with:
  - `next_child_version(parent_version)` helper
- Provide a convenience function:
  - `create_child_version(parent_workflow, child_body)` which:
    - assigns a new version string
    - records parent/child in history
    - returns the new workflow dict

This ties into `generator/history.py` for persistent lineage.

---

## MVM Philosophy for Recursion

- **Safety first:** recursion should not infinitely loop or mutate in
  unpredictable ways at this stage.
- **Transparency:** each new version should be traceable back to its
  parent and diff-able.
- **Pluggability:** actual generative “brain” can be swapped in later
  (LLMs, heuristic rules, etc.), but the infrastructure remains stable.
