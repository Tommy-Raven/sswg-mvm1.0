# 🎨 Visualization API (ai_visualization/)  
### Mermaid · Graphviz · Markdown

---

# 📄 Markdown Export

## `export_markdown(workflow, out_dir)`
Outputs a full Markdown workflow document:

Sections:
- Metadata  
- Phase breakdown  
- Tasks  
- Mermaid graph  

---

# 🔗 Graphviz Export

## `export_graphviz(workflow, out_dir)`
Creates `.dot` files for graph rendering.

---

# 🧭 Mermaid Generator

## `mermaid_from_workflow(workflow)`
Produces:

```
flowchart TD
    P1 --> P2
    P2 --> P3
```

Used for docs + dashboards.
