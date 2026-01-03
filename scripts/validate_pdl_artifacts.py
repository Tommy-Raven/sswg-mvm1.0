from __future__ import annotations

import argparse
from pathlib import Path

from cli.cli_arg_parser_core import build_parser, parse_args
from generator.pdl_validator import PDLValidationError, validate_pdl_file_with_report


def _parse_args() -> argparse.Namespace:
    parser = build_parser("Validate all PDL artifacts.")
    parser.add_argument(
        "--pdl-dir",
        type=Path,
        default=Path("pdl"),
        help="Directory containing PDL YAML files.",
    )
    parser.add_argument(
        "--schema-dir",
        type=Path,
        default=Path("schemas"),
        help="Directory containing schema files.",
    )
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=Path("artifacts/validation"),
        help="Directory to emit validation reports.",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default="local-run",
        help="Run identifier for report output.",
    )
    return parse_args(parser)


def main() -> int:
    args = _parse_args()
    pdl_files = sorted(args.pdl_dir.glob("*.yaml"))
    if not pdl_files:
        print(f"No PDL files found in {args.pdl_dir}")
        return 1
    for pdl_path in pdl_files:
        try:
            validate_pdl_file_with_report(
                pdl_path=pdl_path,
                schema_dir=args.schema_dir,
                report_dir=args.report_dir,
                run_id=args.run_id,
            )
        except PDLValidationError as exc:
            print(f"PDL validation failed for {pdl_path}: {exc.label.as_dict()}")
            return 1
    print("PDL validation passed for all artifacts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
