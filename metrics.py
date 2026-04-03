"""
EvalForge — Metrics Calculator
================================
Computes evaluation statistics from Result rows stored in the database.

Metrics returned
----------------
  pass_rate           overall fraction of passed results
  pass_at_1           Pass@1 — fraction of questions solved on first attempt
  avg_execution_time  mean execution time of passed results (seconds)
  error_distribution  count + ratio breakdown by error kind
  total / passed / failed counts
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from sqlalchemy.orm import Session

from evaluator import ErrorKind
from models import Result, Task


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class ErrorBucket:
    label: str
    count: int
    ratio: float          # 0.0 – 1.0


@dataclass
class TaskReport:
    task_id: int
    model_name: str
    dataset_name: str
    status: str

    total_results: int
    passed_count: int
    failed_count: int

    pass_rate: float                        # passed / total
    pass_at_1: float                        # unique questions solved / total unique questions

    avg_execution_time: Optional[float]     # mean time of passed results (None if no pass)

    error_distribution: list[ErrorBucket]  # pie-chart data

    # Raw counts per error kind (convenient for tables / tooltips)
    syntax_errors: int = 0
    runtime_errors: int = 0
    assertion_errors: int = 0
    timeout_errors: int = 0
    other_errors: int = 0


# ---------------------------------------------------------------------------
# Error kind inference
# (Results don't store ErrorKind directly; we infer from error_log text)
# ---------------------------------------------------------------------------

_TIMEOUT_PAT  = re.compile(r"timeoutexpired|dockertimeout", re.I)
_ASSERT_PAT   = re.compile(r"assertionerror", re.I)
_SYNTAX_PAT   = re.compile(r"syntaxerror|indentationerror|taberror", re.I)


def _infer_error_kind(result: Result) -> ErrorKind:
    """Infer the ErrorKind from a failed Result's error_log."""
    if result.passed:
        return ErrorKind.none

    log = result.error_log or ""
    if _TIMEOUT_PAT.search(log):
        return ErrorKind.timeout
    if _ASSERT_PAT.search(log):
        return ErrorKind.assertion_error
    if _SYNTAX_PAT.search(log):
        return ErrorKind.syntax_error
    if log.strip():
        return ErrorKind.runtime_error
    return ErrorKind.sandbox_error


# ---------------------------------------------------------------------------
# Calculator
# ---------------------------------------------------------------------------


class MetricsCalculator:
    """
    Computes all metrics for a given task from its Result rows.

    Usage
    -----
        calc = MetricsCalculator(db)
        report = calc.compute(task_id=42)
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def compute(self, task_id: int) -> TaskReport:
        task: Optional[Task] = self._db.query(Task).filter(Task.id == task_id).first()
        if task is None:
            raise ValueError(f"Task {task_id} not found")

        results: list[Result] = (
            self._db.query(Result).filter(Result.task_id == task_id).all()
        )

        total = len(results)
        if total == 0:
            return self._empty_report(task)

        # ── pass / fail counts ────────────────────────────────────────
        passed_results  = [r for r in results if r.passed is True]
        failed_results  = [r for r in results if r.passed is not True]
        passed_count    = len(passed_results)
        failed_count    = len(failed_results)

        # ── Pass@1 ────────────────────────────────────────────────────
        # Each (question_id) has exactly one result in Pass@1 setup.
        # Fraction of unique questions for which the first (and only) attempt passed.
        unique_questions:  set[int] = {r.question_id for r in results}
        solved_questions:  set[int] = {r.question_id for r in passed_results}
        pass_at_1 = len(solved_questions) / len(unique_questions) if unique_questions else 0.0

        # ── Average execution time (passed only) ──────────────────────
        exec_times = [
            r.execution_time
            for r in passed_results
            if r.execution_time is not None
        ]
        avg_exec_time = (sum(exec_times) / len(exec_times)) if exec_times else None

        # ── Error distribution ────────────────────────────────────────
        kind_counts: dict[ErrorKind, int] = {k: 0 for k in ErrorKind}
        for r in failed_results:
            kind_counts[_infer_error_kind(r)] += 1

        error_distribution = self._build_distribution(kind_counts, failed_count)

        return TaskReport(
            task_id=task.id,
            model_name=task.model_name,
            dataset_name=task.dataset_name,
            status=task.status,
            total_results=total,
            passed_count=passed_count,
            failed_count=failed_count,
            pass_rate=round(passed_count / total, 4),
            pass_at_1=round(pass_at_1, 4),
            avg_execution_time=round(avg_exec_time, 4) if avg_exec_time is not None else None,
            error_distribution=error_distribution,
            syntax_errors=kind_counts[ErrorKind.syntax_error],
            runtime_errors=kind_counts[ErrorKind.runtime_error],
            assertion_errors=kind_counts[ErrorKind.assertion_error],
            timeout_errors=kind_counts[ErrorKind.timeout],
            other_errors=kind_counts[ErrorKind.sandbox_error],
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_distribution(
        kind_counts: dict[ErrorKind, int],
        failed_total: int,
    ) -> list[ErrorBucket]:
        """
        Returns a list of ErrorBucket for the pie chart.
        Only includes error kinds that actually occurred.
        Denominator is the total failed count (not total results).
        """
        buckets: list[ErrorBucket] = []
        labels = {
            ErrorKind.syntax_error:    "语法错误",
            ErrorKind.runtime_error:   "运行时错误",
            ErrorKind.assertion_error: "答案错误（断言失败）",
            ErrorKind.timeout:         "执行超时",
            ErrorKind.sandbox_error:   "沙盒异常",
        }
        for kind, label in labels.items():
            count = kind_counts.get(kind, 0)
            if count == 0:
                continue
            ratio = round(count / failed_total, 4) if failed_total else 0.0
            buckets.append(ErrorBucket(label=label, count=count, ratio=ratio))
        return buckets

    @staticmethod
    def _empty_report(task: Task) -> TaskReport:
        return TaskReport(
            task_id=task.id,
            model_name=task.model_name,
            dataset_name=task.dataset_name,
            status=task.status,
            total_results=0,
            passed_count=0,
            failed_count=0,
            pass_rate=0.0,
            pass_at_1=0.0,
            avg_execution_time=None,
            error_distribution=[],
        )
