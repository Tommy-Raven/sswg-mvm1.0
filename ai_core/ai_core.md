# ai_core — Orchestration Spine for SSWG MVM

The `ai_core` package is the orchestration backbone of the SSWG system.  
It glues together:

- **Workflows** (what we’re trying to do)
- **Modules** (how we do it in pieces)
- **Phases** (ordered slices of process)
- **Orchestrator** (the conductor)
- **Dependency mapping** (who depends on whom)

At the MVM stage, the emphasis is on *clarity and composability*, not on
cleverness. Everything is designed to be easy to inspect, test, and extend.

---

## Core Responsibilities

### 1. `workflow.py`

**Role:** Lightweight container for a single workflow instance.

Responsibilities:

- Hold the canonical workflow dict (schema-aligned with `workflow_schema.json`).
- Provide helpers to:
  - read/write metadata (purpose, audience, tags)
  - access modules and phases
  - attach evaluation results
- Stay as dumb as possible: no hidden side effects, no heavy logic.

The `Workflow` class is what other components pass around when they say
“this workflow”.

---

### 2. `module_registry.py`

**Role:** Registry of executable “modules” that implement workflow steps.

Responsibilities:

- Store module definitions keyed by `module_id`.
- Provide registration functions:
  - `register_module(module_id, func, metadata)`
- Provide lookup and listing functions:
  - `get(module_id)`
  - `list_modules()`
- Keep metadata that can be exported or visualized:
  - human descriptions
  - expected inputs/outputs
  - which phase the module belongs to

At MVM, this can be purely in-memory, populated by simple registration
calls at startup or in tests.

---

### 3. `phase_controller.py`

**Role:** Run modules in a defined phase in the right order.

Responsibilities:

- Given:
  - a `Workflow`
  - a list of phase definitions
  - a module registry
- It will:
  - determine which modules belong to the phase
  - sort them according to dependencies (using the dependency mapper)
  - execute them in order
  - collect outputs and attach them to the workflow context

At MVM, this can be a simple loop:
1. resolve module order
2. call each module with a context dict
3. merge results back into the workflow.

---

### 4. `orchestrator.py`

**Role:** High-level conductor for multi-phase execution.

Responsibilities:

- Define the **phase sequence** (e.g. `["init", "build", "refine", "evaluate"]`).
- For each phase:
  - ask `PhaseController` to run it
  - optionally call validation and evaluation layers
- Emit high-level telemetry/summary events:
  - which phases ran
  - which modules executed
  - basic outcomes

The orchestrator is the thing you’d call from a CLI or API to “run the
workflow pipeline”.

---

### 5. `dependency_graph.py` (core-level mapping)

**Role:** Light abstraction for dependency ordering in ai_core.

Even though there is a separate `ai_graph` package that focuses on graph
analysis and visualization, the core may expose a simplified mapping that:

- Wraps or delegates to `ai_graph.dependency_mapper.DependencyGraph`
- Provides a minimal interface that `PhaseController` can use to:
  - detect obvious cycles
  - compute a safe execution order
  - surface dependency issues early

For MVM, this can be a thin shim around the graph utilities with just
enough to sort modules by dependencies.

---

## Data Flow (MVM)

1. **Workflow Loaded/Created**  
   A `Workflow` instance is constructed from JSON or built programmatically.

2. **Modules Registered**  
   Implementations for module IDs are registered in `ModuleRegistry`.

3. **Orchestrator Runs**  
   Orchestrator iterates phases and uses `PhaseController` for each.

4. **PhaseController Executes Modules**  
   For a given phase:
   - Build dependency order.
   - Execute modules.
   - Update workflow context.

5. **Validation / Evaluation (via other packages)**  
   ai_validation and ai_evaluation are called at appropriate points.

6. **Export / History**  
   Final workflow is exported and evolution recorded outside ai_core.

---

## MVM Philosophy

- **Small surface, strong contracts:** keep public APIs simple and well-defined.
- **Composition over magic:** no hidden global state, no spooky behavior.
- **Easy to refactor later:** this layer should be resilient to future changes
  in schema or recursion strategies.

Update this document whenever core orchestration behavior changes in a
significant way.
