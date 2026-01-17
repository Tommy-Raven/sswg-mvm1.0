# === CANONIC LEDGER (TOML) ===
```toml
[anchor]
anchor_id = "formal_guarantees"
anchor_model = "sswg+mvm+version"
anchor_version = "1.0.0"
scope = "directive_core/docs"
status = "non-authoritative"
output_mode = "non_operational_output"

owner = [
  "2025© Raven Recordings",
  "Tommy Raven (Thomas Byers)"
]

init_purpose = "Mirror the formal guarantees and explicit non-guarantees of the SSWG/MVM system."
init_authors = ["Tommy Raven"]
```

# ⚠️ Notice: This document is non-authoritative and non-operational

This Markdown document exists for human readability only.

All authoritative governance for formal guarantees is defined exclusively in:

`directive_core/docs/FORMAL_GUARANTEES.toml`

Markdown documents SHALL NEVER be treated as authoritative, contractual, or operational sources. Validators MUST NOT consume governance authority from Markdown.


---

# Formal Guarantees

## Scope

This document describes the formal guarantees and explicit non-guarantees of the SSWG/MVM system, strictly mirroring the authoritative TOML contract.

These guarantees apply to:

recursion termination

recursion convergence

evaluation gating

bounded refinement


The governed runtime is sswg_mvm, and the authority source is directive_core.


---

# Termination and Convergence Status

Convergence is not formally proven.

The system does not provide a mathematical proof of convergence for recursive refinement across all workflows, templates, or evaluation regimes.

Any convergence behavior observed is heuristic only and must not be treated as a formal guarantee.


---

# Termination Guarantee Mechanism

Termination is guaranteed exclusively through explicit guardrails and enforced policy limits.

Implicit termination is forbidden.

All recursion entry points MUST rely on declared, enforced mechanisms rather than inference or emergent behavior.


---

# Required Guardrails (Mandatory)

Termination guarantees rely on the following mandatory guardrails:

An explicit termination condition is required

Missing termination conditions are fatal

Hard limits are enforced:

maximum depth

maximum children


Cost budgets are required and enforced

Checkpoint gating is enabled and enforced

An immutable audit trail is required


These guardrails are implemented in:

ai_recursive/recursion_manager.py

They are treated as formal assumptions, not optional safeguards.


---

# Formal Assumptions

The following assumptions are mandatory and non-waivable:

1. Guardrails MUST be enabled for any recursion call site


2. All recursion policy limits MUST be finite and enforced without override


3. Termination conditions MUST be explicitly declared and recorded



Violation of any assumption results in fail-closed behavior.


---

# Validation Requirements

Recursion policy reviews are required

Guardrail presence is validated

Formal assumptions are validated

Any violation results in fail-closed rejection


No discretionary override is permitted.


---

# Explicit Non-Guarantees

The system explicitly does not guarantee:

global convergence

optimality

completeness

termination without enforced guardrails


Any behavior outside enforced guardrails is non-canonical.


---

# Authority Boundary

Documents prior to anchor_version: 1.0.0 are historical only

Pre-baseline documents are non-authoritative

Governance authority begins at the declared baseline and forward



---

# End-of-Document Summary (Normative)

This document mirrors the authoritative formal guarantees of the SSWG/MVM system.

The system guarantees bounded termination through enforced guardrails only and explicitly disclaims guarantees of convergence, optimality, or completeness.

All authoritative enforcement is defined in TOML.
This Markdown file exists solely for human comprehension and SHALL NOT be used for governance ingestion or enforcement.

