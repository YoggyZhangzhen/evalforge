"""
往 evalforge.db 注入一批演示数据，让前端首次打开就有内容可看。
运行一次即可：python seed_demo.py
"""
from models import Base, Task, Question, Result, TaskStatus, engine, SessionLocal
from evaluator import Evaluator, SandboxMode

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# ── 清空旧数据 ────────────────────────────────────────────────────────────────
db.query(Result).delete()
db.query(Question).delete()
db.query(Task).delete()
db.commit()

# ── 题目 ──────────────────────────────────────────────────────────────────────
questions_data = [
    {
        "dataset_name": "HumanEval",
        "description": "Return the sum of two integers.",
        "function_signature": "def add(a: int, b: int) -> int:",
        "test_cases": [
            {"input": "add(1, 2)",   "expected_output": 3},
            {"input": "add(-1, 1)",  "expected_output": 0},
            {"input": "add(0, 0)",   "expected_output": 0},
        ],
    },
    {
        "dataset_name": "HumanEval",
        "description": "Return True if n is even, False otherwise.",
        "function_signature": "def is_even(n: int) -> bool:",
        "test_cases": [
            {"input": "is_even(4)",  "expected_output": True},
            {"input": "is_even(7)",  "expected_output": False},
        ],
    },
    {
        "dataset_name": "HumanEval",
        "description": "Reverse a string.",
        "function_signature": "def reverse_str(s: str) -> str:",
        "test_cases": [
            {"input": "reverse_str('hello')", "expected_output": "olleh"},
            {"input": "reverse_str('ab')",    "expected_output": "ba"},
        ],
    },
    {
        "dataset_name": "HumanEval",
        "description": "Return the factorial of n (n >= 0).",
        "function_signature": "def factorial(n: int) -> int:",
        "test_cases": [
            {"input": "factorial(0)", "expected_output": 1},
            {"input": "factorial(5)", "expected_output": 120},
        ],
    },
    {
        "dataset_name": "HumanEval",
        "description": "Return the maximum element in a list.",
        "function_signature": "def list_max(lst: list) -> int:",
        "test_cases": [
            {"input": "list_max([3, 1, 4, 1, 5])", "expected_output": 5},
            {"input": "list_max([-1, -3, -2])",     "expected_output": -1},
        ],
    },
]

qs = []
for qd in questions_data:
    q = Question(**qd)
    db.add(q)
db.commit()
qs = db.query(Question).all()
print(f"✓ Inserted {len(qs)} questions")

# ── 模拟代码（有好有坏，覆盖全部错误类型）────────────────────────────────────
CODES = {
    # (question_idx, task_idx): generated_code
    # Task 0: GPT-4o on HumanEval — mostly correct
    (0, 0): "def add(a, b):\n    return a + b",
    (1, 0): "def is_even(n):\n    return n % 2 == 0",
    (2, 0): "def reverse_str(s):\n    return s[::-1]",
    (3, 0): "def factorial(n):\n    if n == 0: return 1\n    return n * factorial(n-1)",
    (4, 0): "def list_max(lst):\n    return max(lst)",

    # Task 1: DeepSeek-Coder — mixed quality
    (0, 1): "def add(a, b):\n    return a + b",
    (1, 1): "def is_even(n):\n    return n % 2",            # 逻辑错：返回余数而非 bool
    (2, 1): "def reverse_str(s):\n    return s[::-1]",
    (3, 1): "def factorial(n):\n    return a / 0",           # 运行时错误
    (4, 1): "def list_max(lst):\n    return lst[0]",        # 答案错误（只取第一个）

    # Task 2: Qwen2.5 — poor quality, lots of errors
    (0, 2): "def add(a, b): return a +",                    # 语法错误
    (1, 2): "def is_even(n):\n    while True: pass",        # 超时
    (2, 2): "def reverse_str(s):\n    return s",            # 答案错
    (3, 2): "def factorial(n):\n    return n / 0",          # 运行时错误
    (4, 2): "def list_max(lst):\n    return max(lst)",
}

TASKS_META = [
    ("gpt-4o",           "HumanEval"),
    ("deepseek-coder",   "HumanEval"),
    ("qwen2.5-coder-7b", "HumanEval"),
]

evaluator = Evaluator(mode=SandboxMode.SUBPROCESS, timeout=3.0)

for task_idx, (model, dataset) in enumerate(TASKS_META):
    task = Task(model_name=model, dataset_name=dataset, status=TaskStatus.running)
    db.add(task)
    db.commit()
    db.refresh(task)
    print(f"\n▶ Task #{task.id}  {model} / {dataset}")

    for q_idx, q in enumerate(qs):
        code = CODES.get((q_idx, task_idx), "def placeholder(): pass")
        result = evaluator.run(generated_code=code, test_cases=q.test_cases)

        row = Result(
            task_id=task.id,
            question_id=q.id,
            generated_code=code,
            execution_time=result.execution_time,
            passed=result.passed,
            error_log=result.error_log,
        )
        db.add(row)
        db.commit()

        icon = "✓" if result.passed else "✗"
        print(f"  {icon} Q#{q.id}  {result.error_kind.value:<18}  {result.execution_time:.3f}s")

    task.status = TaskStatus.completed
    db.commit()

db.close()
print("\n✓ Seed complete — evalforge.db is ready")
