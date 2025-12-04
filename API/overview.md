# 🧩 SSWG-MVM API Overview  
### Developer Reference · v.09.mvm.25

The **SSWG Minimum Viable Model (MVM)** is a modular architecture composed of interoperable subsystems.  
Each module can run independently or as part of the full recursion pipeline.

This document provides a **high-level map** of all public interfaces.

---

# 🏗 Core Architectural Layers

```
generator/       → Main entrypoints, refinement loop, export pipeline  
ai_core/         → Orchestrator + workflow lifecycle  
ai_validation/   → Schema/structure validation  
ai_recursive/    → Diff-based regeneration + variant synthesis  
ai_graph/        → Dependency graph engine  
ai_memory/       → Persistence + feedback systems  
ai_evaluation/   → Clarity & quality metrics  
ai_visualization/→ Mermaid/Graphviz/document exporters  
ai_monitoring/   → Telemetry, logging, diagnostics  
```

All subsystems follow the SSWG-MVM principles:

- **Schema-aligned internal models**  
- **Deterministic execution**  
- **Recursion-first architecture**  
- **Human-readable + machine-readable parity**  
- **Explicit metadata tracking**  

---

# 📚 What You’ll Find in This Section

This API reference includes:

- Public classes and functions  
- Expected inputs/outputs  
- Execution flow diagrams  
- Module interactions  
- Notes on recursion or refinement behaviors
