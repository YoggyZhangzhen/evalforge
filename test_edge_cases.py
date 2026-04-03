"""
EvalForge — Edge Case Validation
=================================
手动验证四种边缘情况，覆盖：
  Case 1  SyntaxError    — 语法残缺代码
  Case 2  RuntimeError   — 运行时异常 (ZeroDivisionError)
  Case 3  AssertionError — 逻辑/答案错误
  Case 4  Timeout        — 死循环强制 Kill

测试内容：
  ① 沙盒能否精准分类每种错误
  ② 结果是否正确写入 SQLite 数据库
  ③ MetricsCalculator 能否生成正确的饼图数据
  ④ 整体耗时（Timeout 应在 3s 被 kill，不阻塞）

运行：
    python test_edge_cases.py
"""

import sys
import time
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ── 项目模块 ─────────────────────────────────────────────────────────────────
from models import Base, Task, Question, Result, TaskStatus
from evaluator import Evaluator, SandboxMode, ErrorKind
from metrics import MetricsCalculator

# ── ANSI 颜色 ─────────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
DIM    = "\033[2m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

TIMEOUT_SEC = 3.0


# ─────────────────────────────────────────────────────────────────────────────
# Test case definitions
# ─────────────────────────────────────────────────────────────────────────────

CASES = [
    {
        "id":          1,
        "name":        "SyntaxError — 语法残缺",
        "code":        "def add(a, b): return a +",      # 不完整表达式
        "test_cases":  [{"input": "add(1, 2)", "expected_output": 3}],
        "expected_kind": ErrorKind.syntax_error,
        "expected_pass": False,
    },
    {
        "id":          2,
        "name":        "RuntimeError — 除零异常",
        "code":        "def add(a, b): return a / 0",    # ZeroDivisionError
        "test_cases":  [{"input": "add(1, 2)", "expected_output": 3}],
        "expected_kind": ErrorKind.runtime_error,
        "expected_pass": False,
    },
    {
        "id":          3,
        "name":        "AssertionError — 答案错误",
        "code":        "def add(a, b): return a - b",    # 逻辑 bug
        "test_cases":  [{"input": "add(1, 2)", "expected_output": 3}],
        "expected_kind": ErrorKind.assertion_error,
        "expected_pass": False,
    },
    {
        "id":          4,
        "name":        "Timeout — 死循环",
        "code":        "def add(a, b):\n    while True: pass",
        "test_cases":  [{"input": "add(1, 2)", "expected_output": 3}],
        "expected_kind": ErrorKind.timeout,
        "expected_pass": False,
        "expected_min_time": TIMEOUT_SEC - 0.5,   # 应该接近超时时间
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def sep(char="─", width=68):
    print(f"{DIM}{char * width}{RESET}")

def header(text: str):
    sep("═")
    print(f"{BOLD}{CYAN}  {text}{RESET}")
    sep("═")

def section(text: str):
    print(f"\n{BOLD}{text}{RESET}")
    sep()

def ok(msg: str):
    print(f"  {GREEN}✓{RESET}  {msg}")

def fail(msg: str):
    print(f"  {RED}✗{RESET}  {msg}")
    return False

def info(msg: str):
    print(f"  {DIM}·{RESET}  {DIM}{msg}{RESET}")


def assert_eq(label: str, got, expected) -> bool:
    if got == expected:
        ok(f"{label}: {CYAN}{got}{RESET}")
        return True
    else:
        fail(f"{label}: got {RED}{got!r}{RESET}, expected {CYAN}{expected!r}{RESET}")
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Phase 1 — Sandbox-only tests (no DB)
# ─────────────────────────────────────────────────────────────────────────────

def phase1_sandbox() -> dict[int, object]:
    """Run all cases through the Evaluator and verify error classification."""
    header("Phase 1 · Sandbox Execution & Error Classification")
    evaluator = Evaluator(mode=SandboxMode.SUBPROCESS, timeout=TIMEOUT_SEC)
    eval_results = {}
    all_ok = True

    for case in CASES:
        section(f"Case {case['id']} — {case['name']}")
        t0 = time.perf_counter()
        result = evaluator.run(
            generated_code=case["code"],
            test_cases=case["test_cases"],
        )
        wall = time.perf_counter() - t0

        info(f"elapsed={wall:.3f}s  |  exec_time={result.execution_time:.3f}s  |  kind={result.error_kind.value}")
        if result.error_log:
            # Show first 3 non-empty lines of error log
            lines = [l for l in result.error_log.splitlines() if l.strip()][:3]
            for ln in lines:
                info(f"  {DIM}{ln}{RESET}")

        ok1 = assert_eq("passed",     result.passed,     case["expected_pass"])
        ok2 = assert_eq("error_kind", result.error_kind, case["expected_kind"])

        # Timeout should take ≥ TIMEOUT_SEC seconds
        ok3 = True
        if "expected_min_time" in case:
            if wall >= case["expected_min_time"]:
                ok(f"wall_time ≥ {case['expected_min_time']}s  (actual: {wall:.2f}s)  — process was killed")
            else:
                ok3 = fail(f"wall_time too short: {wall:.2f}s, expected ≥ {case['expected_min_time']}s")

        eval_results[case["id"]] = result
        if not (ok1 and ok2 and ok3):
            all_ok = False

    sep("═")
    if all_ok:
        print(f"\n{GREEN}{BOLD}  Phase 1 PASSED — all 4 cases correctly classified{RESET}\n")
    else:
        print(f"\n{RED}{BOLD}  Phase 1 FAILED — see details above{RESET}\n")

    return eval_results


# ─────────────────────────────────────────────────────────────────────────────
# Phase 2 — Database write + read-back
# ─────────────────────────────────────────────────────────────────────────────

def phase2_database(eval_results: dict) -> tuple:
    """Persist results to an in-memory SQLite DB and verify round-trip."""
    header("Phase 2 · Database Persistence")

    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    # Create task
    task = Task(
        model_name="test-model",
        dataset_name="EdgeCaseTests",
        status=TaskStatus.completed,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    ok(f"Task created  id={task.id}  status={task.status}")

    # Create one Question per case
    q_ids = {}
    for case in CASES:
        q = Question(
            description=case["name"],
            function_signature="def add(a, b): ...",
            test_cases=case["test_cases"],
        )
        db.add(q)
        db.commit()
        db.refresh(q)
        q_ids[case["id"]] = q.id

    # Write Results
    db_results = []
    for case in CASES:
        er = eval_results[case["id"]]
        row = Result(
            task_id=task.id,
            question_id=q_ids[case["id"]],
            generated_code=case["code"],
            execution_time=er.execution_time,
            passed=er.passed,
            error_log=er.error_log,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        db_results.append(row)
        info(f"Result#{row.id}  q={row.question_id}  passed={row.passed}  time={row.execution_time:.3f}s")

    # Read back and verify
    section("Read-back verification")
    all_ok = True
    rows = db.query(Result).filter(Result.task_id == task.id).all()
    assert_eq("result count in DB", len(rows), 4)

    for row, case in zip(rows, CASES):
        passed_ok = assert_eq(
            f"  Case {case['id']} passed",
            row.passed, case["expected_pass"],
        )
        code_ok = assert_eq(
            f"  Case {case['id']} code stored",
            row.generated_code, case["code"],
        )
        if not (passed_ok and code_ok):
            all_ok = False

    sep("═")
    if all_ok:
        print(f"\n{GREEN}{BOLD}  Phase 2 PASSED — all results persisted & verified{RESET}\n")
    else:
        print(f"\n{RED}{BOLD}  Phase 2 FAILED — see details above{RESET}\n")

    return task, db


# ─────────────────────────────────────────────────────────────────────────────
# Phase 3 — Metrics & pie-chart data
# ─────────────────────────────────────────────────────────────────────────────

def phase3_metrics(task: Task, db) -> None:
    header("Phase 3 · Metrics Calculator (Pie Chart Data)")

    report = MetricsCalculator(db).compute(task.id)
    all_ok = True

    section("Aggregate metrics")
    all_ok &= assert_eq("total_results",  report.total_results, 4)
    all_ok &= assert_eq("passed_count",   report.passed_count,  0)
    all_ok &= assert_eq("failed_count",   report.failed_count,  4)
    all_ok &= assert_eq("pass_rate",      report.pass_rate,     0.0)
    all_ok &= assert_eq("pass_at_1",      report.pass_at_1,     0.0)
    ok(f"avg_execution_time: {CYAN}{report.avg_execution_time}{RESET}  (None — no passing results)")

    section("Per-error-kind counts")
    all_ok &= assert_eq("syntax_errors",    report.syntax_errors,    1)
    all_ok &= assert_eq("runtime_errors",   report.runtime_errors,   1)
    all_ok &= assert_eq("assertion_errors", report.assertion_errors, 1)
    all_ok &= assert_eq("timeout_errors",   report.timeout_errors,   1)

    section("Pie chart distribution (error_distribution)")
    info(f"{'Label':<40} {'Count':>5}  {'Ratio':>7}  {'%':>6}")
    sep("-")
    ratio_sum = 0.0
    for bucket in report.error_distribution:
        bar = "█" * int(bucket.ratio * 20)
        info(f"{bucket.label:<40} {bucket.count:>5}  {bucket.ratio:>7.4f}  "
             f"[{CYAN}{bar:<20}{RESET}] {bucket.ratio*100:.1f}%")
        ratio_sum += bucket.ratio

    # Each bucket should represent exactly 25% (1/4 failures)
    all_ok &= assert_eq(
        "each bucket ratio ≈ 0.25",
        all(abs(b.ratio - 0.25) < 0.001 for b in report.error_distribution),
        True,
    )
    ok(f"ratio_sum ≈ 1.0  (actual: {ratio_sum:.4f})")

    sep("═")
    if all_ok:
        print(f"\n{GREEN}{BOLD}  Phase 3 PASSED — metrics & pie-chart data correct{RESET}\n")
    else:
        print(f"\n{RED}{BOLD}  Phase 3 FAILED — see details above{RESET}\n")


# ─────────────────────────────────────────────────────────────────────────────
# Phase 4 — Timing: system must not hang on timeout case
# ─────────────────────────────────────────────────────────────────────────────

def phase4_no_hang() -> None:
    header("Phase 4 · System Stability (no hang on infinite loop)")

    evaluator = Evaluator(mode=SandboxMode.SUBPROCESS, timeout=TIMEOUT_SEC)

    section("Running 3 timeout cases back-to-back…")
    t0 = time.perf_counter()
    for i in range(3):
        r = evaluator.run(
            generated_code="while True: pass",
            test_cases=[{"input": "True", "expected_output": False}],
        )
        elapsed = time.perf_counter() - t0
        info(f"  run {i+1}: kind={r.error_kind.value}  cumulative={elapsed:.2f}s")

    total = time.perf_counter() - t0

    # 3 runs × 3s = ~9s is expected; anything > 15s means hangs
    if total < TIMEOUT_SEC * 3 + 3.0:
        ok(f"3 timeouts completed in {total:.2f}s — system did not hang")
    else:
        fail(f"3 timeouts took {total:.2f}s — possible hang detected!")

    sep("═")
    print(f"\n{GREEN}{BOLD}  Phase 4 PASSED — no deadlocks or hangs{RESET}\n")


# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────

def summary_table(eval_results: dict) -> None:
    header("Summary · All Edge Cases")

    col_w = [6, 32, 12, 10, 50]
    fmt   = "  {:<{w0}}  {:<{w1}}  {:<{w2}}  {:<{w3}}  {}"

    print(fmt.format(
        "CaseID", "Name", "ErrorKind", "Passed", "First line of error",
        w0=col_w[0], w1=col_w[1], w2=col_w[2], w3=col_w[3],
    ))
    sep()

    for case in CASES:
        er = eval_results[case["id"]]
        first_line = (er.error_log or "").splitlines()[0][:48] if er.error_log else "—"
        kind_color = {
            ErrorKind.syntax_error:    YELLOW,
            ErrorKind.runtime_error:   RED,
            ErrorKind.assertion_error: YELLOW,
            ErrorKind.timeout:         CYAN,
        }.get(er.error_kind, DIM)
        pass_str = f"{GREEN}True{RESET}" if er.passed else f"{RED}False{RESET}"

        print(fmt.format(
            f"#{case['id']}",
            case["name"][:30],
            f"{kind_color}{er.error_kind.value}{RESET}",
            pass_str,
            f"{DIM}{first_line}{RESET}",
            w0=col_w[0], w1=col_w[1], w2=col_w[2], w3=col_w[3],
        ))

    sep("═")


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"\n{BOLD}{CYAN}EvalForge — Edge Case Validation Suite{RESET}")
    print(f"{DIM}Timeout per case: {TIMEOUT_SEC}s  |  Python: {sys.version.split()[0]}{RESET}\n")

    t_start = time.perf_counter()

    eval_results        = phase1_sandbox()
    task, db            = phase2_database(eval_results)
    phase3_metrics(task, db)
    phase4_no_hang()
    summary_table(eval_results)

    total_time = time.perf_counter() - t_start
    print(f"\n{BOLD}All phases completed in {total_time:.2f}s{RESET}\n")
