---
anchor:
  anchor_id: docs_templates_overview
  anchor_version: "1.0.0"
  scope: docs
  owner: sswg
  status: draft
---

# 📚 Workflow Template Library  
### SSWG-MVM — Modular Instruction Blueprint System

The SSWG-MVM ships with a curated set of **base templates** that provide structured, domain-specific workflow blueprints. These templates serve as:

- **starting points** for generation  
- **training data** for schema alignment  
- **fallback structures** when user input is incomplete  
- **recursion anchors** for refinement loops  

Templates are stored in:

```
data/templates/
```

Each template follows the `workflow_schema.json` and passes:

- metadata validation  
- phase/task structure validation  
- DAG construction tests  

---

# 🎨 Why Templates Matter

Templates ensure:

### ✔ Deterministic minimum structure  
No matter what the user provides, workflows always meet baseline schema.

### ✔ Domain richness  
Each template injects specialized vocabulary and domain-specific logic.

### ✔ Cross-template hybridization  
Future recursion modes can merge templates (e.g., Creative + Meta-Reflection).

### ✔ Uniform refinement  
MVM recognizes template IDs and applies optimized refiner rules.

---

# 📦 Available Templates

| Template File | Domain | Purpose |
|---------------|--------|---------|
| `creative_writing_template.json` | Literary Arts | Generate structured narrative workflows |
| `meta_reflection_template.json` | Metacognition | Evaluate/refine cognitive frameworks |
| `technical_procedure_template.json` | Engineering | Document repeatable operational procedures |
| `training_curriculum_template.json` | Education | Scaffold full curriculum blueprints |

---

# 🔁 Template → Workflow Conversion

MVM transforms a template into a runnable workflow through:

1. **Normalization**  
   - ensures all phases include `ai_task_logic` + `human_actionable`

2. **DAG Generation**  
   - ordered P1 → Pn nodes  
   - edges based on domain heuristics  

3. **Refinement**  
   - adds missing tasks  
   - strengthens verbs and clarity  

4. **Evaluation**  
   - clarity scoring  
   - structural density analysis  

This produces a **fully schema-aligned JSON** ready for export to Markdown + Mermaid.
