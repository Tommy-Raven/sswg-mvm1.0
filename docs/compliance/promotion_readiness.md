# Promotion Readiness Rule

Promotion is blocked on any PDL schema validation failure. Any PDL document that fails validation against `schemas/pdl.json` must hard-fail with `Type: schema_failure` and `phase_id: validate`, and the run must not be promoted.
