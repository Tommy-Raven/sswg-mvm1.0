### repo map
%%----------------------------------------
%%  Recursive AI Instructional Workflow Generator
%%  Repository Structure Diagram
%%  Color Legend:
%%    🔵 Blue   = Root
%%    🟩 Green  = Package / Directory
%%    🟧 Orange = Module (.py)
%%    🟨 Yellow = Config / Metadata
%%    🟪 Purple = Tests
%%    🟥 Red    = Documentation / Diagrams
%%    🟦 Cyan   = CLI / Interface Layer
%%----------------------------------------

graph TD
    %% ROOT
    R[🔵 /AI_instructions_workflow]:::root

    %% PRIMARY DIRECTORIES
    R --> C1[🟩 ai_core/]:::package
    R --> C2[🟩 tests/]:::package
    R --> C3[🟩 docs/]:::package
    R --> F1[🟨 setup.py]:::config
    R --> F2[🟨 requirements.txt]:::config
    R --> F3[🟨 .gitignore]:::config
    R --> F4[🟦 cli.py]:::cli

    %% AI_CORE MODULES
    C1 --> M1[🟧 workflow_engine.py]:::module
    C1 --> M2[🟧 recursion_manager.py]:::module
    C1 --> M3[🟧 graph_engine.py]:::module
    C1 --> M4[🟧 evaluation_engine.py]:::module
    C1 --> M5[🟧 io_manager.py]:::module
    C1 --> M6[🟧 visualizer.py]:::module

    %% TESTS
    C2 --> T1[🟪 test_workflow_engine.py]:::test
    C2 --> T2[🟪 test_graph_engine.py]:::test
    C2 --> T3[🟪 conftest.py]:::test

    %% DOCS
    C3 --> D1[🟥 architecture.md]:::docs
    C3 --> D2[🟥 diagrams/]:::docs
    C3 --> D3[🟥 usage_guide.md]:::docs

    %% STYLING
    classDef root fill:#0096FF,stroke:#003366,color:white;
    classDef package fill:#00C957,stroke:#006400,color:white;
    classDef module fill:#FFB347,stroke:#CC7000,color:black;
    classDef config fill:#FFD700,stroke:#CCAC00,color:black;
    classDef test fill:#A020F0,stroke:#5D007A,color:white;
    classDef docs fill:#FF6B6B,stroke:#B22222,color:white;
    classDef cli fill:#00CED1,stroke:#007C80,color:black;

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

