# 🧱 Template Structure Specification

All templates follow a strict JSON structure which MVM then validates and expands.

---

# 🧩 Required Fields

### **Top Level**
```json
{
  "template_id": "string",
  "title": "string",
  "description": "string",
  "phases": [...],
  "metadata": {...}
}
```

### **Phase Object**
Each phase in `phases` must include at minimum:

```json
{
  "id": "P1",
  "title": "Phase Title",
  "tasks": [
    "Task A",
    "Task B"
  ]
}
```

During MVM processing, missing fields are auto-inserted:

- `ai_task_logic`
- `human_actionable`
- fully structured `task` objects if needed

---

# 🧠 Schema Differences: Template vs Workflow

Templates = **lightweight**, minimal, human-designed  
Workflows = **fully expanded**, machine-rich, schema-complete  

| Feature | Template | Workflow |
|---------|----------|-----------|
| tasks | strings | structured objects |
| ai_task_logic | optional | required |
| human_actionable | optional | required |
| dependency_graph | optional | auto-generated |
| version | optional | required (v.09.mvm.25) |
| metadata completeness | minimal | full |

---

# 🔧 Template Expansion Example

Template task:
```
"Identify system constraints"
```

Expanded workflow (auto-fill):

```json
{
  "text": "Identify system constraints",
  "ai_task_logic": "Analyze and list external and internal constraints that affect execution.",
  "human_actionable": "Provide environmental or operational constraints relevant to the system."
}
```

---

# ✔ Template Loading

Templates are loaded via:

```python
from data.data_parsing import load_template
wf = load_template("creative")
```

Automatically normalizing everything into full workflow format.

---

# 🧩 Optimization Template Reference

The optimization subsystem uses a dedicated ontology template:

```
data/templates/system_optimization_template.json
```

Use this template when defining optimization telemetry or bounded cognition parameters.
