> ⚠️ DEPRECATED — NON-AUTHORITATIVE
>
> This document is NOT canonical.
> It SHALL NEVER be used as a source of governance.
> Canonical governance will reside exclusively in `directive_core/docs/`.
> This file exists only for historical or migration reference.

--- 
anchor:
  anchor_id: cli_reference
  anchor_version: "1.3.0+mvm"
  scope: docs
  owner: sswg-core
  status: canonical
  output_mode: non_operational_output
---

# sswg cli reference (non_operational_output)

## Scope and terminology alignment

This document is a non_operational_output. Terminology follows `TERMINOLOGY.md` and uses glossary-defined terms such as `evidence_bundle`, `decision_trace`, `evaluation_gate`, and `bounded_recursion`.

## CLI reference summary

The cli definition describes command names, arguments, and artifact-oriented outputs. The reference is declarative and avoids operational instructions.

### Commands

| Command | Description | Primary artifacts |
| --- | --- | --- |
| `phase` | Declares a phase selection against the canonical phase set. | `decision_trace` |
| `init` | Declares deterministic prerequisites and output directories as artifacts. | `evidence_bundle` |
| `run` | Declares bounded_recursion scope for the canonical phase set. | `evidence_bundle` |
| `validate` | Declares schema validation of the canonical PDL phase set. | `decision_trace` |
| `bundle` | Declares audit artifact aggregation into an `evidence_bundle`. | `evidence_bundle` |
| `add-artifact` | Declares additive artifact creation. | `artifact` |
| `fork` | Declares branch creation metadata. | `decision_trace` |
| `merge-request` | Declares a merge request intent into canonical state. | `decision_trace` |

### Common argument fields

| Field | Description |
| --- | --- |
| `pdl_path` | Path reference to a PDL document aligned to `full_9_phase`. |
| `schema_dir` | Path reference to schema definitions used for validation. |
| `audit_dir` | Path reference for audit `evidence_bundle` outputs. |
| `run_id` | Identifier used for audit correlation in `decision_trace` outputs. |

## Canonical 9-phase model

The canonical phase order is fixed and declarative:

`ingest → normalize → parse → analyze → generate → validate → compare → interpret → log`

### Phase determinism

Determinism is phase-scoped. The phases `normalize`, `analyze`, `validate`, and `compare` are deterministic. The phase `interpret` is nondeterministic and is labeled accordingly; determinism claims exclude `interpret`.

### Phase constraints (schema-aligned)

| Phase | Determinism | Required constraints |
| --- | --- | --- |
| ingest | not deterministic_required | `no_interpretation: true`, `no_mutation_of_canonical: true` |
| normalize | deterministic_required | `deterministic_required: true`, `alignment_rules_required: true` |
| parse | not deterministic_required | `schema_binding_required: true`, `no_generation: true` |
| analyze | deterministic_required | `deterministic_required: true`, `no_generative_tools_for_measurement: true` |
| generate | not deterministic_required | `outputs_must_be_declarative: true`, `no_measurement_keys_generated_stochastically: true` |
| validate | deterministic_required | `schema_validation_required: true`, `invariants_required: true` |
| compare | deterministic_required | `deterministic_required: true`, `overlap_metrics_allowed: [iou, jaccard]` |
| interpret | nondeterministic | `must_reference_measured_artifacts: true`, `output_must_be_labeled_nondeterministic: true` |
| log | not deterministic_required | `run_id_required: true`, `inputs_hash_required: true`, `phase_status_required: true` |

## Deterministic evidence_bundle note

Deterministic phases produce reproducible `evidence_bundle` outputs under fixed schema conditions and validated inputs.

## PDL validation outputs (non_operational_output)

The `validate` command emits a `decision_trace` and a `pdl_validation_report` artifact. A syntactically valid PDL aligned to `full_9_phase` yields `result: pass` in the report with no schema errors. Schema-alignment failures yield `result: fail` with `Type: schema_failure` in the associated failure label.
