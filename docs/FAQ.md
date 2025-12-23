sswg-mvm; version 1.0+ (living document)
Date: 05-03-2025
Document title: Frequently Asked Questions (FAQ)
Author: Tommy Raven
Licensing: Raven Recordings ©️ see: *LICENSE.md*
(Document) Purpose: Provide quick answers about the SSWG-MVM, including installation, workflow execution, recursion controls, memory, evaluation, and contribution pathways. Connect new readers to the root [README](../README.md) and [docs/README.md](./README.md) so they can navigate to deeper architecture and API guides. Emphasize SSWG as the topic base multiplier that keeps refinements anchored during iterative runs.

# Frequently Asked Questions (FAQ) — SSWG-MVM

## General

**Q:** What is the SSWG-MVM?
**A:** The SSWG-MVM is a modular AI system for generating, evaluating, and recursively improving instructional workflows. It produces human- and machine-readable outputs, with persistent memory and deterministic execution while keeping the SSWG topic focus anchored as iterations progress.

**Q:** Who is this system intended for?
**A:** Developers, AI researchers, and instructional designers looking for automated workflow generation with self-improving recursive capabilities.

---

## Installation & Setup

**Q:** What are the prerequisites?
**A:** Python 3.10+ (or compatible), and dependencies listed in `requirements.txt`. Optional: Docker for containerized deployment.

**Q:** How do I install dependencies?
**A:** Run `pip install -r requirements.txt` from the project root.

**Q:** Can I run the system without the CLI?
**A:** Yes. The system can be invoked programmatically using FastAPI endpoints or by importing core modules directly in Python.

---

## Workflow Execution

**Q:** How do I start a new workflow?
**A:** Use `generator.main.create_workflow(user_params)` to initiate a workflow, or trigger a recursive cycle via `ai_recursive.expansion.generate()` when you need the SSWG-guided refinement pass.

**Q:** How does recursion work?
**A:** Recursive workflows feed previous outputs into new iterations, applying semantic scoring, merging, and evaluation to improve clarity and coverage continuously.

**Q:** Can I stop a recursive workflow?
**A:** Yes. Recursion halts automatically when semantic stability thresholds are reached, or manually via the RecursionManager interface.

---

## Memory & Evaluation

**Q:** Where are workflows stored?
**A:** All workflow iterations are archived in `ai_memory/`, including versioned identifiers, metrics, and lineage data.

**Q:** How are workflows evaluated?
**A:** The `ai_evaluation` engine scores workflows on clarity, expandability, and translatability. Evaluations inform recursive improvement cycles.

**Q:** Can I access historical iterations?
**A:** Yes. Historical workflows are accessible via `ai_memory.lineage` and `ai_memory.store` for reconstruction or analysis.

---

## Troubleshooting

**Q:** I get inconsistent outputs across runs. Why?
**A:** Ensure deterministic execution by using consistent input parameters and environment settings. Check that caching and memory persistence are functioning correctly.

**Q:** Workflow modules fail to load. What should I do?
**A:** Confirm that `ai_core/phases/` and `generator/modules.py` exist and are on the Python path. Use `registry.py` for dynamic discovery if necessary.

**Q:** How do I debug recursion loops?
**A:** Use telemetry logs in `ai_monitoring.telemetry` and benchmark metrics in `ai_memory/benchmark_tracker.py`. RecursionManager exceptions also provide traceable information.

---

## Contribution & Support

**Q:** How can I contribute?
**A:** See `CONTRIBUTOR_GUIDE.md` for contribution workflows, coding standards, and phase-based module ownership.

**Q:** Where can I report bugs or request features?
**A:** Open issues on the GitHub repository: [https://github.com/Tommy-Raven/AI_instructions_workflow](https://github.com/Tommy-Raven/AI_instructions_workflow).

**Q:** Are there any learning resources?
**A:** Documentation includes onboarding guides, API reference, and architecture overviews. Demo notebooks provide practical examples.
