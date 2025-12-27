#!/usr/bin/env python3
"""
ai_core/workflow.py — Core workflow container for SSWG MVM.

This class is deliberately hybrid:

- Legacy / generator usage:
    wf = Workflow(workflow_id, params)
    wf.run_all_phases()
    wf.results[...]

- MVM / orchestrator usage:
    wf = Workflow(workflow_dict)          # dict is schema-aligned
    wf.id
    wf.get_default_phases()
    wf.get_modules_for_phase(phase_id)
    wf.get_context() / wf.update_context(...)
    wf.to_dict()

This keeps existing generator/main.py working while enabling the new
ai_core orchestrator + phase controller API.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional


class Workflow:
    """
    Core workflow container.

    Internally tracks:
    - workflow_id
    - params (legacy generation parameters)
    - metadata, phases, modules, evaluation, recursion
    - context (mutable during execution)
    - results (legacy phase results from run_all_phases)
    """

    # ------------------------------------------------------------------ #
    # Construction
    # ------------------------------------------------------------------ #
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Overloaded constructor to support both usage modes:

        1) Legacy:
            Workflow(workflow_id: str, params: dict)

        2) Dict / schema-based:
            Workflow(workflow_dict: dict)
        """
        self.workflow_id: str = ""
        self.params: Dict[str, Any] = {}
        self.results: Dict[str, Any] = {}

        # Schema-style fields (for orchestrator)
        self.version: str = "0.0.0"
        self.schema_version: str = "1.0.0"
        self.metadata: Dict[str, Any] = {}
        self.phases: List[Dict[str, Any]] = []
        self.modules: List[Dict[str, Any]] = []
        self.outputs: List[Dict[str, Any]] = []
        self.evaluation: Dict[str, Any] = {}
        self.recursion: Dict[str, Any] = {}
        self.dependency_graph: Dict[str, Any] = {}
        self.dependency_index: Dict[str, Any] = {}
        self.causal_ledger: List[Dict[str, Any]] = []
        self.inheritance: Dict[str, Any] = {}
        self.context: Dict[str, Any] = {}

        if args and isinstance(args[0], dict):
            # Mode 2: Workflow(workflow_dict)
            if len(args) != 1:
                raise TypeError("Workflow(dict) expects a single positional argument")
            data: Dict[str, Any] = args[0]
            self._init_from_dict(data)
        elif len(args) == 2 and isinstance(args[0], str) and isinstance(args[1], dict):
            # Mode 1: Workflow(workflow_id, params)
            wf_id, params = args
            self._init_from_id_and_params(wf_id, params)
        else:
            raise TypeError(
                "Workflow(...) expects either (workflow_id: str, params: dict) "
                "or (workflow_dict: dict)."
            )

    def _init_from_id_and_params(self, workflow_id: str, params: Dict[str, Any]) -> None:
        """Legacy / generator initialization path."""
        self.workflow_id = workflow_id
        self.params = dict(params)

        # Legacy behavior didn't explicitly model phases/modules/context;
        # we keep those defaults empty. run_all_phases() will populate
        # self.results with placeholder data, as before.

    def _init_from_dict(self, data: Dict[str, Any]) -> None:
        """Schema-style initialization from a workflow dict."""
        self.workflow_id = data.get("workflow_id") or data.get("id") or "unnamed_workflow"
        self.version = str(data.get("version", "0.0.0"))
        self.schema_version = str(data.get("schema_version", "1.0.0"))

        self.metadata = data.get("metadata", {}) or {}
        if "title" not in self.metadata:
            self.metadata["title"] = data.get("title") or "Untitled Workflow"
        if "description" not in self.metadata:
            self.metadata["description"] = data.get("description") or "Generated workflow."

        self.phases = data.get("phases", []) or []
        if not self.phases:
            self.phases = [
                {
                    "id": "P1",
                    "title": "Initialization",
                    "description": "Initialize workflow context and inputs.",
                    "tasks": [
                        {
                            "id": "T1",
                            "description": "Initialize workflow inputs.",
                            "inputs": ["seed"],
                            "outputs": ["initialized_context"],
                        }
                    ],
                }
            ]
        self.modules = data.get("modules", []) or []
        self.outputs = data.get("outputs", []) or []
        self.evaluation = data.get("evaluation", {}) or {}
        self.recursion = data.get("recursion", {}) or {}
        self.dependency_graph = data.get("dependency_graph", {}) or {}
        self.dependency_index = data.get("dependency_index", {}) or {}
        self.causal_ledger = data.get("causal_ledger", []) or []
        self.inheritance = data.get("inheritance", {}) or {}

        # Execution context can be stored in multiple places; we prefer a
        # dedicated field if present, otherwise we start empty.
        self.context = data.get("context", {}) or {}

        # Legacy-style results may be present; if not, leave empty.
        self.results = data.get("results", {}) or {}
        self.params = data.get("params", {}) or {}

    # ------------------------------------------------------------------ #
    # Convenience properties & core accessors
    # ------------------------------------------------------------------ #
    @property
    def id(self) -> str:
        """Canonical id property used by orchestrator."""
        return self.workflow_id

    def get_default_phases(self) -> List[str]:
        """
        Return the default ordered list of phase identifiers.

        For schema-based workflows:
        - If `phases` contains dicts with `id`/`phase_id`/`name` fields, use those.

        For legacy workflows:
        - Fall back to the original hard-coded phases.
        """
        if self.phases:
            ids: List[str] = []
            for ph in self.phases:
                pid = ph.get("id") or ph.get("phase_id") or ph.get("name")
                if pid:
                    ids.append(str(pid))
            if ids:
                return ids

        # Legacy fallback
        return [
            "Phase 1 — Initialization",
            "Phase 2 — How-To Generation",
            "Phase 3 — Modularization",
        ]

    def get_modules_for_phase(self, phase_id: str) -> List[Dict[str, Any]]:
        """
        Return all module definitions that belong to the given phase.

        Modules are expected to be dicts with at least:
            - module_id: str
            - phase_id: str
        """
        return [
            m for m in self.modules
            if str(m.get("phase_id")) == str(phase_id)
        ]

    def get_context(self) -> Dict[str, Any]:
        """
        Return the mutable execution context for this workflow.
        """
        return self.context

    def update_context(self, updates: Dict[str, Any]) -> None:
        """
        Merge updates into the execution context.
        """
        self.context.update(updates)

    # ------------------------------------------------------------------ #
    # Legacy phase execution (kept for generator/main compatibility)
    # ------------------------------------------------------------------ #
    def run_all_phases(self) -> None:
        """
        Run all phases of the workflow (legacy behavior).

        This preserves the original simple phase loop so that existing
        generator/main.py code using `wf.run_all_phases()` still works.
        """
        phases = [
            "Phase 1 — Initialization",
            "Phase 2 — How-To Generation",
            "Phase 3 — Modularization",
        ]
        for phase in phases:
            self.results[phase] = self.execute_phase(phase)

    def execute_phase(self, phase_name: str) -> Dict[str, Any]:
        """
        Placeholder phase execution logic (legacy).

        For now, this just returns a stubbed structure. In the future,
        this could be wired into the same module/phase machinery used
        by the orchestrator.
        """
        print(f"[Workflow] Executing {phase_name}")
        return {
            "objective": f"Objective for {phase_name}",
            "details": {},
        }

    # ------------------------------------------------------------------ #
    # Serialization
    # ------------------------------------------------------------------ #
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize this workflow to a schema-aligned dict as much as possible.

        This is what exporters / validators should consume.
        """
        payload: Dict[str, Any] = {
            "workflow_id": self.workflow_id,
            "version": self.version,
            "schema_version": self.schema_version,
            "metadata": self.metadata,
            "phases": self.phases,
        }
        if self.modules:
            payload["modules"] = self.modules
        if self.outputs:
            payload["outputs"] = self.outputs
        if self.evaluation:
            payload["evaluation"] = self.evaluation
        if self.recursion:
            payload["recursion"] = self.recursion
        if self.dependency_graph:
            payload["dependency_graph"] = self.dependency_graph
        if self.dependency_index:
            payload["dependency_index"] = self.dependency_index
        if self.causal_ledger:
            payload["causal_ledger"] = self.causal_ledger
        if self.inheritance:
            payload["inheritance"] = self.inheritance
        if self.context:
            payload["context"] = self.context
        if self.results:
            payload["results"] = self.results
        if self.params:
            payload["params"] = self.params
        return payload
# ---------------------------------------------------------------------- #
