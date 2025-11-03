ai-instructional-workflow-generator/
│
├── generator/                      # Legacy interface layer (CLI entry point)
│   ├── main.py
│   ├── exporters.py
│   ├── workflow.py             # Workflow class; manages phases 1–5
│   ├── modules.py              # Modular AI subroutines (ObjectiveRefinement, StageWriter, etc.)
│   ├── evaluation.py           # Evaluates clarity, expandability, and AI readability
│   ├── recursive_expansion.py  # Variant generation + recursive merging logic
│   └── utils.py                # UUID, timestamps, and logging tools
│
├── data/
│   ├── templates/              # (optional) Prebuilt workflow blueprints for reference
│   └── outputs/                # Export destination for .json / .md workflows
│
├── README.md                   # Project documentation and usage guide
└── requirements.txt             # Python dependencies (if any)
|
├── ai_core/                        # Core workflow execution logic
│   ├── __init__.py
│   ├── workflow.py                 # Orchestrator for phases
│   ├── phases/
│   │   ├── __init__.py
│   │   ├── initialization.py
│   │   ├── refinement.py
│   │   ├── human_readable.py
│   │   ├── modularization.py
│   │   ├── evaluation.py
│   │   └── regeneration.py
│   └── registry.py                 # Dynamically discovers and runs phases
│
├── ai_recursive/                   # Self-evolving recursion engine
│   ├── __init__.py
│   ├── expansion.py
│   ├── merging.py
│   ├── evaluator.py
│   ├── registry.py
│   └── memory.py
│
├── ai_memory/                      # Long-term storage of evolution logs
│   ├── __init__.py
│   ├── store.py
│   ├── lineage.py
│   ├── metrics.py
│   └── analytics.py
│
├── ai_evaluation/                  # Metric-based evaluation engine
│   ├── __init__.py
│   ├── base.py
│   ├── clarity.py
│   ├── expandability.py
│   ├── translatability.py
│   └── registry.py
│
├── data/
│   ├── templates/
│   └── outputs/
│
├── schemas/                        # JSON Schemas for validation
│   ├── workflow_schema.json
│   ├── module_schema.json
│   └── evaluation_schema.json
│
├── tests/
│   ├── test_ai_core.py
│   ├── test_recursive.py
│   ├── test_memory.py
│   ├── test_exporters.py
│   └── test_evaluation.py
│
└── docs/
    ├── ARCHITECTURE.md
    ├── API_REFERENCE.md
    ├── AI_RECURSION.md
    ├── METRICS_SYSTEM.md
    ├── EVOLUTION_LOGGING.md
    └── CONTRIBUTOR_GUIDE.md
