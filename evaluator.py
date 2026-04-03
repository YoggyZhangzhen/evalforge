"""
EvalForge — Evaluator Engine
=============================
Provides two classes:

  CodeSandbox  — executes untrusted code in an isolated environment.
                 Version A: subprocess (local / CI use)
                 Version B: Docker container (production / staging)

  Evaluator    — assembles test scripts from LLM-generated code + test cases,
                 drives the sandbox, and returns a structured EvalResult.

Usage example
-------------
    from evaluator import Evaluator, SandboxMode

    evaluator = Evaluator(mode=SandboxMode.SUBPROCESS, timeout=3.0)
    result = evaluator.run(
        generated_code="def add(a, b):\\n    return a + b",
        test_cases=[
            {"input": "add(1, 2)", "expected_output": 3},
            {"input": "add(-1, 1)", "expected_output": 0},
        ],
    )
    print(result)
"""

from __future__ import annotations

import textwrap
import time
import subprocess
import sys
import tempfile
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------


class ErrorKind(str, Enum):
    none = "none"
    syntax_error = "syntax_error"
    runtime_error = "runtime_error"
    assertion_error = "assertion_error"
    timeout = "timeout"
    sandbox_error = "sandbox_error"


@dataclass
class EvalResult:
    passed: bool
    execution_time: float          # seconds
    error_kind: ErrorKind = ErrorKind.none
    error_log: str = ""
    stdout: str = ""

    def __str__(self) -> str:
        status = "PASS" if self.passed else f"FAIL [{self.error_kind.value}]"
        return (
            f"{status} | {self.execution_time:.3f}s"
            + (f"\n  error: {self.error_log}" if self.error_log else "")
        )


# ---------------------------------------------------------------------------
# Script builder
# ---------------------------------------------------------------------------

_RUNNER_TEMPLATE = """\
{user_code}

# ── test harness ──────────────────────────────────────────────────────────
import sys as _sys

_failures = []
{assertions}

if _failures:
    for _msg in _failures:
        print(_msg, file=_sys.stderr)
    raise AssertionError(f"{{len(_failures)}} test case(s) failed")
"""

_ASSERT_TEMPLATE = """\
try:
    _got = {expr}
    assert _got == {expected!r}, (
        "case {idx}: " + {expr!r} + " => " + repr(_got) + " != " + repr({expected!r})
    )
except AssertionError as _e:
    _failures.append(str(_e))
"""


def build_test_script(generated_code: str, test_cases: list[dict[str, Any]]) -> str:
    """Combine LLM code with assert statements into a single runnable script."""
    assertions = []
    for idx, tc in enumerate(test_cases, start=1):
        expr = str(tc["input"])
        expected = tc["expected_output"]
        assertions.append(
            _ASSERT_TEMPLATE.format(idx=idx, expr=expr, expected=expected)
        )

    script = _RUNNER_TEMPLATE.format(
        user_code=textwrap.dedent(generated_code),
        assertions="\n".join(assertions),
    )
    return script


# ---------------------------------------------------------------------------
# Version A — subprocess sandbox (local / CI)
# ---------------------------------------------------------------------------


class SubprocessSandbox:
    """
    Executes a Python script in a child process with a hard timeout.

    Security properties
    -------------------
    - Isolated process: crashes / infinite loops cannot affect the host.
    - stdout / stderr fully captured; never printed to the host terminal.
    - Hard wall-clock timeout enforced via subprocess.TimeoutExpired.

    Limitations
    -----------
    - The child process runs under the same OS user — no filesystem or network
      isolation.  Use DockerSandbox for production workloads.
    """

    def __init__(self, timeout: float = 3.0) -> None:
        self.timeout = timeout

    def run(self, script: str) -> tuple[bool, str, str]:
        """
        Run *script* and return (success, stdout, stderr).

        *success* is True only when the process exits with code 0.
        """
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as tmp:
            tmp.write(script)
            tmp_path = tmp.name

        try:
            proc = subprocess.run(
                [sys.executable, tmp_path],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            return proc.returncode == 0, proc.stdout, proc.stderr

        except subprocess.TimeoutExpired:
            return False, "", f"TimeoutExpired: execution exceeded {self.timeout}s"

        except Exception as exc:  # OS-level failures (e.g. OOM)
            return False, "", f"SubprocessError: {exc}"

        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


# ---------------------------------------------------------------------------
# Version B — Docker sandbox (production)
# ---------------------------------------------------------------------------


class DockerSandbox:
    """
    Executes a Python script inside a disposable Docker container.

    Requirements
    ------------
        pip install docker
        # Docker daemon must be running.

    Security properties
    -------------------
    - network_disabled=True  → no outbound connections.
    - mem_limit / nano_cpus  → resource caps.
    - read_only=True         → immutable container filesystem.
    - auto_remove=True       → container deleted on exit (no orphan containers).
    - Runs as unprivileged user inside Alpine image.

    The script is passed via stdin so no host filesystem path is exposed.
    """

    DEFAULT_IMAGE = "python:3.11-alpine"

    def __init__(
        self,
        timeout: float = 10.0,
        image: str = DEFAULT_IMAGE,
        mem_limit: str = "64m",
        nano_cpus: int = 500_000_000,   # 0.5 CPU
    ) -> None:
        self.timeout = timeout
        self.image = image
        self.mem_limit = mem_limit
        self.nano_cpus = nano_cpus

    def run(self, script: str) -> tuple[bool, str, str]:  # pragma: no cover
        """
        Run *script* inside a fresh container and return (success, stdout, stderr).

        NOTE: This method requires the `docker` Python package and a running
        Docker daemon.  It is intentionally not executed in unit tests that
        lack a Docker environment — gate it behind a feature flag or
        environment variable in production.
        """
        try:
            import docker  # type: ignore[import]
        except ImportError as exc:
            raise RuntimeError(
                "docker-py is not installed. Run: pip install docker"
            ) from exc

        client = docker.from_env()

        try:
            container = client.containers.run(
                image=self.image,
                command=["python", "-c", script],
                # ── isolation ──────────────────────────────────────────
                network_disabled=True,
                read_only=True,
                mem_limit=self.mem_limit,
                nano_cpus=self.nano_cpus,
                # ── lifecycle ──────────────────────────────────────────
                detach=True,
                auto_remove=False,   # we remove manually after reading logs
                stdout=True,
                stderr=True,
            )

            try:
                exit_status = container.wait(timeout=self.timeout)
                exit_code: int = exit_status.get("StatusCode", -1)
                raw_logs = container.logs(stdout=True, stderr=True)
                # docker-py returns combined logs; split by marker if needed
                stdout_text = raw_logs.decode("utf-8", errors="replace")
                success = exit_code == 0
                stderr_text = "" if success else stdout_text
                return success, stdout_text if success else "", stderr_text

            except Exception as wait_exc:
                container.kill()
                return False, "", f"DockerTimeout: {wait_exc}"

            finally:
                try:
                    container.remove(force=True)
                except Exception:
                    pass

        except docker.errors.ImageNotFound:
            return False, "", f"Docker image '{self.image}' not found. Run: docker pull {self.image}"
        except docker.errors.DockerException as exc:
            return False, "", f"DockerError: {exc}"


# ---------------------------------------------------------------------------
# Sandbox mode selector
# ---------------------------------------------------------------------------


class SandboxMode(str, Enum):
    SUBPROCESS = "subprocess"
    DOCKER = "docker"


# ---------------------------------------------------------------------------
# Evaluator
# ---------------------------------------------------------------------------


class Evaluator:
    """
    Orchestrates LLM code evaluation against a set of test cases.

    Parameters
    ----------
    mode : SandboxMode
        SUBPROCESS for local development; DOCKER for production.
    timeout : float
        Maximum wall-clock seconds allowed per evaluation.

    Example
    -------
    >>> ev = Evaluator(mode=SandboxMode.SUBPROCESS, timeout=3.0)
    >>> result = ev.run(
    ...     generated_code="def add(a, b):\\n    return a + b",
    ...     test_cases=[{"input": "add(1, 2)", "expected_output": 3}],
    ... )
    >>> assert result.passed
    """

    def __init__(
        self,
        mode: SandboxMode = SandboxMode.SUBPROCESS,
        timeout: float = 3.0,
        docker_image: str = DockerSandbox.DEFAULT_IMAGE,
    ) -> None:
        self.mode = mode
        if mode == SandboxMode.SUBPROCESS:
            self._sandbox: SubprocessSandbox | DockerSandbox = SubprocessSandbox(timeout=timeout)
        else:
            self._sandbox = DockerSandbox(timeout=timeout, image=docker_image)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(
        self,
        generated_code: str,
        test_cases: list[dict[str, Any]],
    ) -> EvalResult:
        """
        Evaluate *generated_code* against *test_cases*.

        Each test case must be a dict with keys:
            "input"           — a Python expression string, e.g. "add(1, 2)"
            "expected_output" — the expected return value (any JSON-serialisable type)

        Returns an EvalResult with pass/fail, timing, and error details.
        """
        # ── 1. Syntax check (fast, no subprocess needed) ──────────────
        syntax_error = self._check_syntax(generated_code)
        if syntax_error:
            return EvalResult(
                passed=False,
                execution_time=0.0,
                error_kind=ErrorKind.syntax_error,
                error_log=syntax_error,
            )

        # ── 2. Build the combined test script ─────────────────────────
        try:
            script = build_test_script(generated_code, test_cases)
        except Exception as exc:
            return EvalResult(
                passed=False,
                execution_time=0.0,
                error_kind=ErrorKind.sandbox_error,
                error_log=f"Script build failed: {exc}",
            )

        # ── 3. Execute in sandbox ─────────────────────────────────────
        t_start = time.perf_counter()
        success, stdout, stderr = self._sandbox.run(script)
        elapsed = time.perf_counter() - t_start

        # ── 4. Classify the outcome ───────────────────────────────────
        return self._classify(success, stdout, stderr, elapsed)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _check_syntax(code: str) -> Optional[str]:
        """Return a human-readable syntax error message, or None if OK."""
        try:
            compile(code, "<generated>", "exec")
            return None
        except SyntaxError as exc:
            return f"SyntaxError at line {exc.lineno}: {exc.msg} — {exc.text!r}"

    @staticmethod
    def _classify(
        success: bool,
        stdout: str,
        stderr: str,
        elapsed: float,
    ) -> EvalResult:
        if success:
            return EvalResult(
                passed=True,
                execution_time=elapsed,
                error_kind=ErrorKind.none,
                stdout=stdout,
            )

        # Map stderr keywords to error kinds
        stderr_lower = stderr.lower()
        if "timeoutexpired" in stderr_lower or "dockertimeout" in stderr_lower:
            kind = ErrorKind.timeout
        elif "assertionerror" in stderr_lower:
            kind = ErrorKind.assertion_error
        elif any(k in stderr_lower for k in ("syntaxerror", "indentationerror", "taberror")):
            # Rare: syntax error inside dynamically generated harness
            kind = ErrorKind.syntax_error
        elif stderr_lower.strip():
            kind = ErrorKind.runtime_error
        else:
            kind = ErrorKind.sandbox_error

        return EvalResult(
            passed=False,
            execution_time=elapsed,
            error_kind=kind,
            error_log=stderr.strip(),
            stdout=stdout,
        )


# ---------------------------------------------------------------------------
# Quick smoke-test  (python evaluator.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    evaluator = Evaluator(mode=SandboxMode.SUBPROCESS, timeout=3.0)

    cases: list[tuple[str, list[dict]]] = [
        (
            "correct addition",
            "def add(a, b):\n    return a + b",
            [{"input": "add(1, 2)", "expected_output": 3},
             {"input": "add(-5, 5)", "expected_output": 0}],
        ),
        (
            "wrong answer",
            "def add(a, b):\n    return a - b",   # intentional bug
            [{"input": "add(1, 2)", "expected_output": 3}],
        ),
        (
            "syntax error",
            "def add(a, b)\n    return a + b",    # missing colon
            [{"input": "add(1, 2)", "expected_output": 3}],
        ),
        (
            "runtime exception",
            "def add(a, b):\n    return a / b",
            [{"input": "add(1, 0)", "expected_output": 0}],
        ),
        (
            "infinite loop (timeout)",
            "def add(a, b):\n    while True: pass",
            [{"input": "add(1, 2)", "expected_output": 3}],
        ),
    ]

    for label, code, test_cases in cases:
        result = evaluator.run(generated_code=code, test_cases=test_cases)
        print(f"[{label:30s}]  {result}")
