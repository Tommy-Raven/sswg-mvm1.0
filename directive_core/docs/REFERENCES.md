# === CANONIC LEDGER (TOML) ===
```toml
[anchor]
anchor_id = "sswg_references"
anchor_model = "sswg+mvm+version"
anchor_version = "1.0.0"
scope = "directive_core/docs"
status = "invariant"
output_mode = "non_operational_output"

owner = [
  "2025© Raven Recordings",
  "Tommy Raven (Thomas Byers)"
]

init_purpose = "Define canonical references for directive_core."
init_authors = ["Tommy Raven"]
```
## Executive Summary

This document establishes the **canonical ledger versioning rules** for the SSWG/MVM governance system. It defines, in normative and enforceable terms, how governance documents identify themselves, how version authority is encoded, and where the boundary between *draft history* and *enforced governance* is drawn.

The core outcome of this document is the formal declaration of **`anchor_version: 1.0.0`** as the **first validator-enforced governance baseline**, with a mandatory separation between governance model identity and semantic version numbering. From this baseline forward, all governance is machine-validated, fail-closed, and auditable. Prior identifiers are explicitly preserved as historical drafts without authority.

This document is authoritative for all governance materials under `directive_core/docs/` and is intended to eliminate ambiguity, prevent silent drift, and provide a stable reference point for future evolution.

---

## Canonical Ledger Version Encoding (Normative)

### Rule

All canonical governance documents **MUST** encode versioning using a **two-field split** that cleanly separates *governance model identity* from *semantic version numbering*. This requirement is absolute and applies uniformly across all canonical documents without exception.

```toml
anchor_model = "sswg+mvm+version"
anchor_version = "1.0.0"
```

This split is **mandatory**, **non-optional**, and **structurally enforced**. Any deviation from this encoding is considered a governance violation and is subject to fail-closed validation behavior.

---

### Prohibited Forms

The following forms are **explicitly forbidden** inside any anchor block, regardless of document type or lifecycle stage:

* Embedding the version number directly into `anchor_model`
* Prefixing semantic versions with `v`
* Encoding combined or overloaded identifiers such as:

  * `sswg+mvm+v1.0.0`
  * `sswg+mvm@1.0.0`
  * `sswg+mvm-1.0.0`

Any document containing a prohibited form **SHALL be rejected** by validators and **SHALL NOT** be considered authoritative under any circumstances.

---

### Semantics

The anchor fields have fixed and non-overlapping meanings:

* `anchor_model` identifies the **governance system and versioning scheme** in use. It establishes the interpretive framework under which the document is evaluated.
* `anchor_version` identifies the **semantic baseline number only**, expressed strictly as `X.Y.Z`.

The combined string `sswg+mvm+v1.0.0` is **reserved exclusively** for:

* git tags,
* release names,
* human-readable prose references.

It **MUST NOT** appear inside anchor metadata, headers, or any machine-ingested governance fields.

---

### Stability Guarantee

To preserve long-term auditability and deterministic evolution:

* `anchor_model` **SHALL remain stable** across future releases and governance phases.
* `anchor_version` **SHALL advance monotonically** according to semantic versioning rules.

Silent redefinition, recombination, or reinterpretation of these fields is forbidden and constitutes a breaking governance violation.

---

## Canonical Version Baseline

### Canonical Anchor Encoding

All canonical governance documents under `directive_core/docs/` **MUST** encode versioning using the following anchor fields, without alteration:

```toml
anchor_model = "sswg+mvm+version"
anchor_version = "1.0.0"
```

This encoding defines the **first enforced governance baseline** and establishes the reference point against which all future governance evolution is measured.

---

### Meaning of `anchor_version: 1.0.0`

The value `1.0.0` denotes:

* the first validator-enforced governance baseline,
* the formal completion of Phase 2 (governance enforcement),
* the transition point at which governance moves from documented intent to enforced authority.

This version **DOES NOT** imply:

* feature completeness,
* API stability,
* production or end-user readiness.

It is strictly a **governance milestone**, not a software release signal.

---

### Relationship to Tags and Releases

The string **`sswg+mvm+v1.0.0`** is reserved exclusively for:

* git tags used to mark baseline commits,
* GitHub Releases serving as milestone markers,
* explanatory or historical prose.

It **MUST NOT** appear inside anchor metadata or any other machine-validated field. Anchors **MUST** use the split-field form exclusively to ensure deterministic parsing and validation.

---

### Pre-Baseline Drafts

Any identifiers prior to `anchor_version: 1.0.0` (including `1.2.0`, `v1.2.x`, or similar) are classified as:

> **Pre-baseline drafts**

These drafts:

* are retained for historical and design traceability,
* MAY be referenced in prose when explicitly labeled as non-canonical,
* MUST NOT be treated as authoritative, enforced, or released baselines.

No pre-baseline identifier carries governance authority.

---

### Authority Boundary

The governance authority boundary is defined precisely as follows:

* **At or after `anchor_version: 1.0.0`**

  * governance rules are authoritative,
  * ingestion order is enforced,
  * validators operate in fail-closed mode.

* **Before `anchor_version: 1.0.0`**

  * governance documents are treated as non-authoritative drafts,
  * enforcement guarantees do not apply.

---

### Forward Evolution Rule

All future governance evolution **MUST**:

* retain explicit traceability to this baseline,
* declare clear version deltas, overlays, or amendments,
* preserve the anchor field split invariant defined above.

Silent recombination, implicit reinterpretation, or retroactive alteration of baseline semantics is strictly forbidden.

---

## End-of-Document Summary (Normative)

This document defines the **non-negotiable rules** for canonical ledger versioning within the SSWG/MVM governance system. It establishes a single, enforceable baseline (`anchor_version: 1.0.0`), mandates a strict separation between governance model identity and semantic version numbers, and clearly delineates the authority boundary between pre-baseline drafts and enforced governance.

All future governance documents, updates, and amendments **MUST** comply with the rules defined herein. Any document that violates these requirements is non-canonical by definition and **SHALL** be rejected by governance validators.

This end-of-document summary pattern **SHALL be replicated** (with document-specific content) in all future canonical governance documentation to provide a clear, auditable closure and prevent interpretive ambiguity.
