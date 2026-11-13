"""Finalize a worker report only after the orchestrator persisted its checkpoint."""

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.pipeline import PartialPolicy, evaluate, next_streaks
from app.sync import SyncSummary


def atomic_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent,
                                 prefix="report-", suffix=".tmp", delete=False) as handle:
        temporary = Path(handle.name)
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(temporary, path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--prior-streaks", type=Path)
    parser.add_argument("--checkpoint-persisted", action="store_true")
    parser.add_argument("--summary-file", type=Path,
                        help="Write Markdown for a CI step summary")
    parser.add_argument("--prepare-history", action="store_true",
                        help="Write next failure streaks before checkpoint commit, without a status claim")
    args = parser.parse_args()
    policy = PartialPolicy(
        enabled=os.getenv("ALLOW_PARTIAL_SUCCESS", "false").lower() == "true",
        max_failed_articles=int(os.getenv("MAX_FAILED_ARTICLES", "1")),
        max_failed_percent=float(os.getenv("MAX_FAILED_PERCENT", "1")),
        max_consecutive_failures=int(os.getenv("MAX_CONSECUTIVE_FAILURES", "2")),
    )
    if policy.enabled and not args.prior_streaks:
        raise ValueError("partial success requires durable failure streak history")
    raw = json.loads(args.worker_report.read_text(encoding="utf-8"))
    summary = SyncSummary(**raw)
    prior = json.loads(args.prior_streaks.read_text(encoding="utf-8")) if args.prior_streaks else {}
    if not isinstance(prior, dict) or any(not isinstance(v, int) or v < 0 for v in prior.values()):
        raise ValueError("invalid failure streak history")
    if args.prepare_history:
        if not args.prior_streaks:
            raise ValueError("preparing history requires prior streaks")
        atomic_json(args.output, next_streaks(summary, prior))
        return 0
    report, _ = evaluate(summary, policy, args.checkpoint_persisted, prior)
    atomic_json(args.output, report)
    lines = [f"## Daily sync: {report['status']}", "",
             f"Processed: {report['total_processed']}; added: {report['added']}; "
             f"updated: {report['updated']}; skipped: {report['skipped']}; "
             f"failed: {report['failed']}.", "", report["reason"]]
    for failure in report["failed_articles"]:
        article_id = failure.get("article_id", "unknown")
        lines.append(f"- Article {article_id}: {failure.get('error_type', 'Error')}, "
                     f"retries {failure.get('retry_count', 0)}")
        if str(article_id).isdigit():
            print(f"::warning title=Daily sync article failed::Article {article_id} failed")
    if os.getenv("GITHUB_STEP_SUMMARY"):
        with Path(os.environ["GITHUB_STEP_SUMMARY"]).open("a", encoding="utf-8") as output:
            output.write("\n".join(lines) + "\n")
    if args.summary_file:
        args.summary_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    return 0 if report["status"] in {"SUCCESS", "PARTIAL_SUCCESS"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
