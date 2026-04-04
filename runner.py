"""
EvalForge — 评测调度器
========================
EvaluationRunner 是整个平台的核心，把所有零件串联起来：

  Task（题库 + 模型）
      ↓
  从 DB 取该 dataset 的 Questions
      ↓
  逐题调 LLMClient.generate_code()   ← 若无 API Key，自动降级为 MockLLMClient
      ↓
  Evaluator.run()  →  沙盒执行 + 错误分类
      ↓
  Result 写入 DB，实时更新 Task.status
      ↓
  Task.status = completed / failed

用法：
    runner = EvaluationRunner(config)
    runner.run(task_id=1)          # 同步，可在 BackgroundTasks 里调用
"""

from __future__ import annotations

import logging
from typing import Optional

from config import AppConfig, config as global_config
from evaluator import EvalResult, ErrorKind, Evaluator, SandboxMode
from llm_client import LLMClient, LLMConfig, LLMError
from models import Question, Result, SessionLocal, Task, TaskStatus

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Mock LLM（无 API Key 时使用）
# ---------------------------------------------------------------------------

class MockLLMClient:
    """
    不调用任何外部接口，根据函数签名生成一个占位实现。
    生成的代码大多会通过/失败测试，用于验证完整评测流程。
    """

    # 简单规则：能匹配的签名返回正确实现，其余返回 pass
    _KNOWN: dict[str, str] = {
        "add":         "def add(a, b):\n    return a + b",
        "is_even":     "def is_even(n):\n    return n % 2 == 0",
        "reverse_str": "def reverse_str(s):\n    return s[::-1]",
        "factorial":   "def factorial(n):\n    if n == 0: return 1\n    return n * factorial(n - 1)",
        "list_max":    "def list_max(lst):\n    return max(lst)",
    }

    def generate_code(self, function_signature: str, description: str) -> str:
        for name, impl in self._KNOWN.items():
            if name in function_signature:
                logger.debug("MockLLM: 命中已知函数 %s", name)
                return impl
        # 默认：返回 pass 占位（会触发断言失败，但流程完整）
        first_line = function_signature.strip().splitlines()[0]
        logger.debug("MockLLM: 未知函数，返回 pass 占位")
        return f"{first_line}\n    pass  # MockLLM: 未配置 LLM_API_KEY"


# ---------------------------------------------------------------------------
# 评测调度器
# ---------------------------------------------------------------------------

class EvaluationRunner:
    """
    Parameters
    ----------
    cfg : AppConfig
        全局配置，包含 LLM key、沙盒超时等。
        默认使用全局 config 单例。
    """

    def __init__(self, cfg: AppConfig = global_config) -> None:
        self.cfg = cfg

    # ------------------------------------------------------------------
    # 公开接口
    # ------------------------------------------------------------------

    def run(self, task_id: int) -> None:
        """
        执行一次完整评测，在独立 DB Session 中运行。
        设计用于在 FastAPI BackgroundTasks / 线程池中调用。
        """
        db = SessionLocal()
        try:
            self._execute(task_id, db)
        except Exception as exc:
            logger.error("Task %d 异常终止: %s", task_id, exc, exc_info=True)
            self._mark_failed(task_id, db)
        finally:
            db.close()

    # ------------------------------------------------------------------
    # 内部逻辑
    # ------------------------------------------------------------------

    def _execute(self, task_id: int, db) -> None:
        task: Optional[Task] = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise ValueError(f"Task {task_id} 不存在")

        # ── 标记运行中 ────────────────────────────────────────────────
        task.status = TaskStatus.running
        db.commit()
        logger.info("Task %d 开始 | 模型=%s | 题库=%s", task.id, task.model_name, task.dataset_name)

        # ── 取题目 ────────────────────────────────────────────────────
        questions = (
            db.query(Question)
            .filter(Question.dataset_name == task.dataset_name)
            .all()
        )
        if not questions:
            logger.warning(
                "题库 '%s' 没有题目，回退到全部题目", task.dataset_name
            )
            questions = db.query(Question).all()
        if not questions:
            raise ValueError("数据库中没有任何题目，请先运行 seed_demo.py")

        logger.info("Task %d | 共 %d 道题目", task.id, len(questions))

        # ── 构建 LLM 客户端 ──────────────────────────────────────────
        llm = self._build_llm_client()
        evaluator = Evaluator(
            mode=SandboxMode.DOCKER if self.cfg.use_docker else SandboxMode.SUBPROCESS,
            timeout=self.cfg.sandbox_timeout,
        )

        # ── 断点续传：跳过已有结果的题目 ────────────────────────────
        done_ids = {
            r.question_id
            for r in db.query(Result).filter(Result.task_id == task.id).all()
        }
        remaining = [q for q in questions if q.id not in done_ids]
        if done_ids:
            logger.info("Task %d | 断点续传，跳过已完成 %d 题，剩余 %d 题",
                        task.id, len(done_ids), len(remaining))

        # ── 逐题评测 ─────────────────────────────────────────────────
        for idx, q in enumerate(remaining, start=1):
            # 每题前检查是否已被取消
            db.refresh(task)
            if task.status == TaskStatus.cancelled:
                logger.info("Task %d 已被用户取消，停止评测", task.id)
                return

            logger.info("Task %d | 题目 %d/%d (Q#%d) ...", task.id, idx, len(remaining), q.id)
            result = self._eval_one(llm, evaluator, q)

            row = Result(
                task_id=task.id,
                question_id=q.id,
                generated_code=result.generated_code,
                execution_time=result.execution_time,
                passed=result.passed,
                error_log=result.error_log,
            )
            db.add(row)
            db.commit()

            status_str = "✓ 通过" if result.passed else f"✗ {result.error_kind.value}"
            logger.info(
                "Task %d | Q#%d %s | %.3fs",
                task.id, q.id, status_str, result.execution_time,
            )

        # ── 完成 ─────────────────────────────────────────────────────
        task.status = TaskStatus.completed
        db.commit()
        logger.info("Task %d 评测完成 ✓", task.id)

    def _eval_one(self, llm, evaluator: Evaluator, q: Question) -> "_RichResult":
        """对单道题调 LLM + 沙盒，返回带 generated_code 的结果。"""
        generated_code: Optional[str] = None
        try:
            generated_code = llm.generate_code(
                function_signature=q.function_signature,
                description=q.description,
            )
        except LLMError as exc:
            logger.error("LLM 调用失败 Q#%d: %s", q.id, exc)
            return _RichResult(
                generated_code=None,
                passed=False,
                execution_time=0.0,
                error_kind=ErrorKind.sandbox_error,
                error_log=f"LLM 调用失败: {exc}",
            )

        eval_result: EvalResult = evaluator.run(
            generated_code=generated_code,
            test_cases=q.test_cases,
        )
        return _RichResult(
            generated_code=generated_code,
            passed=eval_result.passed,
            execution_time=eval_result.execution_time,
            error_kind=eval_result.error_kind,
            error_log=eval_result.error_log,
        )

    def _build_llm_client(self):
        if not self.cfg.has_llm_key:
            logger.warning(
                "LLM_API_KEY 未配置，使用 MockLLMClient（内置答案库）"
            )
            return MockLLMClient()
        return LLMClient(LLMConfig(
            api_key=self.cfg.llm_api_key,
            base_url=self.cfg.llm_base_url,
            model=self.cfg.llm_model,
            temperature=self.cfg.llm_temperature,
            timeout=self.cfg.llm_timeout,
        ))

    @staticmethod
    def _mark_failed(task_id: int, db) -> None:
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = TaskStatus.failed
            db.commit()


# ---------------------------------------------------------------------------
# 内部数据类（带 generated_code 字段）
# ---------------------------------------------------------------------------

class _RichResult:
    """EvalResult + generated_code，方便写入 DB。"""
    __slots__ = ("generated_code", "passed", "execution_time", "error_kind", "error_log")

    def __init__(
        self,
        generated_code: Optional[str],
        passed: bool,
        execution_time: float,
        error_kind: ErrorKind,
        error_log: str,
    ) -> None:
        self.generated_code  = generated_code
        self.passed          = passed
        self.execution_time  = execution_time
        self.error_kind      = error_kind
        self.error_log       = error_log
