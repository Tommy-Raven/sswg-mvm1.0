# 🔁 Recursion Engine (MVM Refinement)

The recursion subsystem is a lightweight but powerful refinement system that:

- analyzes workflow structure  
- rewrites inconsistent phases  
- suggests expansions  
- unifies metadata  
- adjusts dependencies  

This is implemented in:

```
generator/recursion_manager.py
```

---

# 🧠 How Recursion Works (Abstract)

The refinement pass performs:

1. **Structural audit**  
   - missing fields?  
   - duplicate IDs?  
   - weak task descriptions?  

2. **Semantic strengthening**  
   - adds detail to vague phases  
   - rewrites weak task verbs (“do stuff”) → (“perform analysis”)  

3. **Dependency tightening**  
   - insert implied prerequisites  
   - align DAG direction  

4. **Metadata normalization**  
   - canonical names  
   - enforce version format  

5. **Evaluation-based adjustments**  
   - clarity_score < threshold?  
   - add corrective notes  

---

# 🔁 Recursion Depth

The MVM includes:

```
simple_refiner(workflow)
```

Future versions will allow:

- N-depth recursion  
- tree-branching  
- cross-template hybridization  

---

# 🧪 Regeneration Triggers

Triggered by:

- high diff_size  
- low clarity_score  
- missing dependency links  
- schema failure → autocorrect  

Every run logs:

```
mvm.process.refined
```

into the structured logger.
