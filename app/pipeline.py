"""Pure policy for reporting article failures without hiding pipeline failures."""

from dataclasses import dataclass
from typing import Any

from app.sync import SyncSummary


@dataclass(frozen=True)
class PartialPolicy:
    enabled: bool = False
    max_failed_articles: int = 1
    max_failed_percent: float = 1.0
    max_consecutive_failures: int = 2

    def __post_init__(self) -> None:
        if self.max_failed_articles < 0 or not 0 <= self.max_failed_percent <= 100:
            raise ValueError("invalid partial success threshold")
        if self.max_consecutive_failures < 1:
            raise ValueError("max_consecutive_failures must be positive")


def next_streaks(summary: SyncSummary, prior_streaks: dict[str, int]) -> dict[str, int]:
    return {entry["article_id"]: prior_streaks.get(entry["article_id"], 0) + 1
            for entry in summary.failures if entry.get("article_id")}


def evaluate(summary: SyncSummary, policy: PartialPolicy,
             checkpoint_persisted: bool, prior_streaks: dict[str, int] | None = None
             ) -> tuple[dict[str, Any], dict[str, int]]:
    """Return a report and next failure streaks; never infer persistence from a local file."""
    if summary.total_processed == 0:
        status, reason = "FAILED", "no articles processed"
    elif not checkpoint_persisted:
        status, reason = "FAILED", "checkpoint not persisted"
    elif not summary.failed:
        status, reason = "SUCCESS", "all articles processed"
    else:
        fraction = summary.failed * 100 / summary.total_processed
        streaks = next_streaks(summary, prior_streaks or {})
        allowed = (policy.enabled and summary.failed <= policy.max_failed_articles
                   and fraction <= policy.max_failed_percent
                   and not any(entry.get("critical") for entry in summary.failures)
                   and all(value < policy.max_consecutive_failures for value in streaks.values()))
        status = "PARTIAL_SUCCESS" if allowed else "FAILED"
        reason = "article failures within policy" if allowed else "article failures exceed policy or policy disabled"
    streaks = next_streaks(summary, prior_streaks or {})
    report = {"status": status, "reason": reason,
              "checkpoint_persisted": checkpoint_persisted,
              "total_processed": summary.total_processed,
              "added": summary.added, "updated": summary.updated,
              "skipped": summary.skipped, "failed": summary.failed,
              "failed_articles": summary.failures,
              "article_results": summary.articles,
              "failure_streaks": streaks}
    return report, streaks
