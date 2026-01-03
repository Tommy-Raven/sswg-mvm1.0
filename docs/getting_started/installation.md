---
anchor:
  anchor_id: docs_getting_started_installation
  anchor_version: "1.0.0"
  scope: docs
  owner: sswg
  status: draft
---

# Installation

## Clone the Repository

```bash
git clone https://github.com/Tommy-Raven/sswg-mvm1.0
cd sswg-mvm1.0
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

If using editable mode for dev:

```bash
pip install -e .
```

---

# Optional: Install Graphviz

```bash
sudo apt install graphviz
```

---

# Verify Installation

```bash
python3 -m generator.main --version
```

Expected:

```
SSWG Workflow Generator — MVM v1.2.0
```
