# Getting Started with SSWG-MVM

This section introduces the Minimum Viable Model for the Synthetic Synthesist of Workflow Generation (SSWG-MVM).  

## What is SSWG-MVM?

A modular, schema-enforced AI system that:

- converts abstract intent → structured workflow  
- enforces required metadata and dependency rules  
- recursively improves outputs  
- exports JSON + Markdown versions  
- logs lineage and metrics  

---

# Workflow Lifecycle

SSWG-MVM runs through:

1. **Loading**  
2. **Schema validation**  
3. **Dependency graph correction**  
4. **Evaluation**  
5. **Optional refinement**  
6. **Export**  
7. **History recording**

---

# Templates Overview

MVM ships with several templates in `data/templates/`:

- **creative_writing**
- **technical_procedure**
- **meta_reflection**
- **training_curriculum**

Each can be invoked using:

```bash
python3 -m generator.main --template creative
```

---

# Requirements

- Python 3.10+
- pip
- Linux/WSL/ChromeOS Debian (supported)

Recommended:

- VS Code  
- GitHub Desktop or terminal Git  
- Graphviz (optional)
