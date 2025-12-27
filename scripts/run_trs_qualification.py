from __future__ import annotations

import argparse
import json
from pathlib import Path

from generator.determinism import replay_determinism_check
from generator.environment import check_environment_drift, environment_fingerprint
from generator.failure_emitter import FailureEmitter, FailureLabel
from generator.hashing import hash_data
from generator.pdl_validator import PDLValidationError, validate_pdl_object

from compatibility_checks import evaluate_compatibility
from overlay_ops import load_artifact, load_overlays, write_json


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run trs qualification gates.")
    parser.add_argument("--run-id", type=str, default="trs-run", help="Run identifier.")
    parser.add_argument(
        "--corpus-path",
        type=Path,
        default=Path("artifacts/trs/trs_corpus_pack.json"),
        help="TRS corpus pack path.",
    )
    parser.add_argument(
        "--schema-dir",
        type=Path,
        default=Path("schemas"),
        help="Schema directory.",
    )
    parser.add_argument(
        "--overlays-dir",
        type=Path,
        default=Path("overlays"),
        help="Overlay descriptor directory.",
    )
    parser.add_argument(
        "--lock-path",
        type=Path,
        default=Path("reproducibility/dependency_lock.json"),
        help="Dependency lock path.",
    )
    parser.add_argument(
        "--certificate-path",
        type=Path,
        default=Path("artifacts/trs/trs_certificate.json"),
        help="Output certificate path.",
    )
    return parser.parse_args()


def _emit_failure(emitter: FailureEmitter, run_id: str, failure: FailureLabel) -> int:
    emitter.emit(failure, run_id=run_id)
    print(f"TRS qualification failed: {failure.as_dict()}")
    return 1


def main() -> int:
    args = _parse_args()
    emitter = FailureEmitter(Path("artifacts/trs/failures"))

    if not args.corpus_path.exists():
        return _emit_failure(
            emitter,
            args.run_id,
            FailureLabel(
                Type="reproducibility_failure",
                message="TRS corpus pack missing",
                phase_id="validate",
                evidence={"path": str(args.corpus_path)},
            ),
        )

    corpus = json.loads(args.corpus_path.read_text(encoding="utf-8"))
    cases = corpus.get("cases", [])
    if not cases:
        return _emit_failure(
            emitter,
            args.run_id,
            FailureLabel(
                Type="schema_failure",
                message="TRS corpus pack has no cases",
                phase_id="validate",
                evidence={"path": str(args.corpus_path)},
            ),
        )

    overlays = load_overlays(args.overlays_dir)
    compatibility_baseline = Path(corpus.get("compatibility_baseline", cases[0]["pdl_path"]))
    compatibility_candidate = Path(corpus.get("compatibility_candidate", cases[0]["pdl_path"]))

    baseline_artifact = load_artifact(compatibility_baseline)
    candidate_artifact = load_artifact(compatibility_candidate)
    compatibility_errors, _, _ = evaluate_compatibility(
        baseline=baseline_artifact,
        candidate=candidate_artifact,
        overlays=overlays,
        schema_dir=args.schema_dir,
        phase_outputs_path=Path(corpus.get("compatibility_phase_outputs", "tests/fixtures/phase_outputs.json")),
        run_id=args.run_id,
    )
    if compatibility_errors:
        return _emit_failure(
            emitter,
            args.run_id,
            FailureLabel(
                Type="schema_failure",
                message="Compatibility matrix validation failed",
                phase_id="validate",
                evidence={"errors": compatibility_errors},
            ),
        )

    phase_hashes: dict[str, str] = {}
    inputs_hashes: list[str] = []
    for case in cases:
        pdl_path = Path(case["pdl_path"])
        phase_outputs_path = Path(case["phase_outputs_path"])
        compare_hash_expected = case.get("compare_output_hash")

        pdl_obj = load_artifact(pdl_path)
        try:
            validate_pdl_object(pdl_obj, schema_dir=args.schema_dir)
        except PDLValidationError as exc:
            return _emit_failure(
                emitter,
                args.run_id,
                FailureLabel(
                    Type="schema_failure",
                    message=exc.label.message,
                    phase_id="validate",
                    evidence=exc.label.evidence,
                ),
            )

        phase_outputs = json.loads(phase_outputs_path.read_text(encoding="utf-8"))
        failure, report = replay_determinism_check(
            run_id=args.run_id,
            phase_outputs=phase_outputs,
            required_phases=["normalize", "analyze", "validate", "compare"],
        )
        if failure:
            return _emit_failure(emitter, args.run_id, failure)

        compare_output = phase_outputs.get("compare")
        if compare_hash_expected and hash_data(compare_output) != compare_hash_expected:
            return _emit_failure(
                emitter,
                args.run_id,
                FailureLabel(
                    Type="deterministic_failure",
                    message="Compare output hash mismatch",
                    phase_id="compare",
                    evidence={
                        "expected": compare_hash_expected,
                        "observed": hash_data(compare_output),
                    },
                ),
            )

        phase_hashes.update(report.phase_hashes)
        inputs_hashes.append(report.inputs_hash)

    env_failure = check_environment_drift(args.lock_path)
    if env_failure:
        return _emit_failure(emitter, args.run_id, env_failure)

    certificate = {
        "anchor": {
            "anchor_id": "trs_certificate",
            "anchor_version": "1.0.0",
            "scope": "run",
            "owner": "scripts.run_trs_qualification",
            "status": "draft",
        },
        "trs_major": corpus.get("trs_major"),
        "run_id": args.run_id,
        "inputs_hashes": inputs_hashes,
        "phase_hashes": phase_hashes,
        "env_fingerprint": environment_fingerprint(args.lock_path),
        "overlay_chain": [
            {
                "overlay_id": overlay.get("overlay_id"),
                "overlay_version": overlay.get("overlay_version"),
            }
            for overlay in overlays
        ],
    }
    write_json(args.certificate_path, certificate)

    print(f"TRS qualification passed. Certificate at {args.certificate_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
