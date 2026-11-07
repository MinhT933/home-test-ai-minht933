"""Command-line entry point for safe knowledge-base synchronization."""

import argparse
import os
from pathlib import Path

from app.gemini_store import configured_store_name, create_client
from app.scraper import fetch_articles
from app.sync import (
    GeminiDocumentGateway,
    JsonManifestStateStore,
    build_bootstrap_report,
    confirm_bootstrap,
    synchronize,
    write_bootstrap_report,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fetch Zendesk articles and compute or apply Gemini deltas."
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--dry-run", action="store_true", help="Report deltas without remote writes."
    )
    mode.add_argument(
        "--sync", action="store_true", help="Apply deltas to the configured existing store."
    )
    mode.add_argument(
        "--bootstrap-report",
        type=Path,
        metavar="REPORT",
        help="Create a read-only legacy reconciliation report.",
    )
    mode.add_argument(
        "--bootstrap-confirm",
        type=Path,
        metavar="REPORT",
        help="Commit checkpoints from an explicitly verified report.",
    )
    parser.add_argument(
        "--articles-dir", type=Path, default=Path("data/articles")
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Limit Zendesk pages for a deliberately scoped take-home sync.",
    )
    parser.add_argument(
        "--state-file",
        type=Path,
        default=None,
        help=(
            "Development checkpoint manifest. Production must point this at durable "
            "mounted/cloud-backed storage or replace the StateStore adapter."
        ),
    )
    parser.add_argument(
        "--acknowledge-verified-content",
        action="store_true",
        help="Confirm that report mappings were verified beyond article-ID matching.",
    )
    parser.add_argument(
        "--verification-evidence",
        default="",
        help="Trusted upload record or independent verification reference.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not any(
        [args.dry_run, args.sync, args.bootstrap_report, args.bootstrap_confirm]
    ):
        parser.print_help()
        return 0

    state_path = args.state_file or (
        Path(os.environ["SYNC_STATE_PATH"])
        if os.getenv("SYNC_STATE_PATH")
        else None
    )
    if state_path is None and not args.bootstrap_report:
        parser.error(
            "--state-file or SYNC_STATE_PATH is required; use durable storage for live sync"
        )
    if (args.dry_run or args.sync) and not state_path.is_file():
        print(f"Checkpoint manifest is missing: {state_path}. Refusing empty-state sync.")
        return 2

    gateway = GeminiDocumentGateway(create_client(), configured_store_name())
    if args.bootstrap_report:
        paths = sorted(args.articles_dir.glob("*.md"))
        report = build_bootstrap_report(paths, gateway.list_documents())
        write_bootstrap_report(report, args.bootstrap_report)
        print(
            f"Bootstrap report: {len(report.entries)} mappings, "
            f"{len(report.issues)} issues. No checkpoints committed."
        )
        return 1 if report.issues else 0

    if args.bootstrap_confirm:
        paths = sorted(args.articles_dir.glob("*.md"))
        try:
            count = confirm_bootstrap(
                args.bootstrap_confirm,
                paths,
                gateway,
                JsonManifestStateStore(state_path),
                args.acknowledge_verified_content,
                args.verification_evidence,
            )
        except (ValueError, RuntimeError) as exc:
            print(f"Bootstrap confirmation failed: {exc}")
            return 1
        print(f"Bootstrap checkpoints committed: {count}")
        return 0

    paths = fetch_articles(max_pages=args.max_pages)
    summary = synchronize(
        paths,
        gateway,
        JsonManifestStateStore(state_path),
        dry_run=args.dry_run,
    )
    return 1 if summary.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
