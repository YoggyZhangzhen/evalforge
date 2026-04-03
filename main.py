"""
EvalForge — LLM Code Generation Evaluation Platform
FastAPI backend entry point.

Run:
    pip install fastapi uvicorn sqlalchemy pydantic
    uvicorn main:app --reload
"""

import logging
from typing import Optional

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from auth import create_token, get_current_user, hash_password, verify_password
from config import config
from metrics import MetricsCalculator
from models import (
    Base,
    Question,
    QuestionCreate,
    QuestionRead,
    Result,
    ResultCreate,
    ResultRead,
    Task,
    TaskCreate,
    TaskDetail,
    TaskRead,
    TaskReportSchema,
    TaskStatus,
    TaskStatusUpdate,
    TokenResponse,
    User,
    UserLogin,
    UserRead,
    UserRegister,
    engine,
    get_db,
)
from runner import EvaluationRunner

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(name)s — %(message)s",
)
_runner = EvaluationRunner(config)

# ---------------------------------------------------------------------------
# App init & table creation
# ---------------------------------------------------------------------------

app = FastAPI(
    title="EvalForge",
    description="LLM Code Generation Evaluation Platform API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    _auto_seed()


def _auto_seed():
    """首次启动时自动注入题库（幂等，已有题目则跳过）。"""
    from models import Question, SessionLocal as _SL
    from seed_questions import QUESTIONS
    from seed_hot100 import HOT100
    db = _SL()
    try:
        if db.query(Question).count() > 0:
            return
        for qd in QUESTIONS + HOT100:
            db.add(Question(**qd))
        db.commit()
        logging.getLogger(__name__).info("Auto-seeded %d questions", len(QUESTIONS) + len(HOT100))
    finally:
        db.close()


# ---------------------------------------------------------------------------
# 鉴权路由
# ---------------------------------------------------------------------------


@app.post("/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED, tags=["Auth"])
def register(payload: UserRegister, db: Session = Depends(get_db)):
    """注册新账号，自动登录返回 Token。第一个注册的用户自动成为管理员。"""
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=409, detail="用户名已被占用")
    is_first = db.query(User).count() == 0
    user = User(
        username=payload.username,
        hashed_pwd=hash_password(payload.password),
        is_admin=is_first,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_token(user.id, user.username)
    return TokenResponse(access_token=token, user=UserRead.model_validate(user))


@app.post("/auth/login", response_model=TokenResponse, tags=["Auth"])
def login(payload: UserLogin, db: Session = Depends(get_db)):
    """用户名密码登录，返回 JWT Token。"""
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.hashed_pwd):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = create_token(user.id, user.username)
    return TokenResponse(access_token=token, user=UserRead.model_validate(user))


@app.get("/auth/me", response_model=UserRead, tags=["Auth"])
def me(current_user: User = Depends(get_current_user)):
    """返回当前登录用户信息。"""
    return current_user


# ---------------------------------------------------------------------------
# Task routes
# ---------------------------------------------------------------------------


@app.post("/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED, tags=["Tasks"])
def create_task(
    payload: TaskCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """创建评测任务并在后台立即开始评测。需要登录。"""
    task = Task(model_name=payload.model_name, dataset_name=payload.dataset_name)
    db.add(task)
    db.commit()
    db.refresh(task)
    background_tasks.add_task(_runner.run, task.id)
    return task


@app.get("/tasks", response_model=list[TaskRead], tags=["Tasks"])
def list_tasks(
    status_filter: Optional[TaskStatus] = Query(default=None, alias="status"),
    limit: int = Query(default=20, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """Return a paginated list of tasks, optionally filtered by status."""
    q = db.query(Task)
    if status_filter:
        q = q.filter(Task.status == status_filter)
    return q.order_by(Task.created_at.desc()).offset(offset).limit(limit).all()


@app.get("/tasks/{task_id}", response_model=TaskDetail, tags=["Tasks"])
def get_task(task_id: int, db: Session = Depends(get_db)):
    """Return a single task with all its results."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task


@app.patch("/tasks/{task_id}/status", response_model=TaskRead, tags=["Tasks"])
def update_task_status(
    task_id: int,
    payload: TaskStatusUpdate,
    db: Session = Depends(get_db),
):
    """Update the status of a task (e.g. set to running / completed / failed)."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    task.status = payload.status
    db.commit()
    db.refresh(task)
    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Tasks"])
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a task and all its results (cascade)."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    db.delete(task)
    db.commit()


# ---------------------------------------------------------------------------
# Question routes
# ---------------------------------------------------------------------------


@app.get("/questions/datasets", response_model=list[str], tags=["Questions"])
def list_datasets(db: Session = Depends(get_db)):
    """返回数据库中所有不重复的题库名称。"""
    rows = db.query(Question.dataset_name).distinct().all()
    return [r[0] for r in rows]


@app.post("/questions", response_model=QuestionRead, status_code=status.HTTP_201_CREATED, tags=["Questions"])
def create_question(payload: QuestionCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """新增一道题目。需要登录。"""
    question = Question(
        dataset_name=payload.dataset_name,
        description=payload.description,
        function_signature=payload.function_signature,
        test_cases=[tc.model_dump() for tc in payload.test_cases],
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


@app.get("/questions", response_model=list[QuestionRead], tags=["Questions"])
def list_questions(
    dataset: Optional[str] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """返回题目列表，可按 dataset 过滤。"""
    q = db.query(Question)
    if dataset:
        q = q.filter(Question.dataset_name == dataset)
    return q.order_by(Question.id).offset(offset).limit(limit).all()


@app.get("/questions/{question_id}", response_model=QuestionRead, tags=["Questions"])
def get_question(question_id: int, db: Session = Depends(get_db)):
    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail=f"Question {question_id} not found")
    return q


@app.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Questions"])
def delete_question(question_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """删除一道题目。需要登录。"""
    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail=f"Question {question_id} not found")
    db.delete(q)
    db.commit()


# ---------------------------------------------------------------------------
# Result routes
# ---------------------------------------------------------------------------


@app.post("/results", response_model=ResultRead, status_code=status.HTTP_201_CREATED, tags=["Results"])
def create_result(payload: ResultCreate, db: Session = Depends(get_db)):
    """Record a single execution result (called by the evaluation runner)."""
    # Validate FK existence
    if not db.query(Task).filter(Task.id == payload.task_id).first():
        raise HTTPException(status_code=404, detail=f"Task {payload.task_id} not found")
    if not db.query(Question).filter(Question.id == payload.question_id).first():
        raise HTTPException(status_code=404, detail=f"Question {payload.question_id} not found")

    result = Result(**payload.model_dump())
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


@app.get("/tasks/{task_id}/results", response_model=list[ResultRead], tags=["Results"])
def list_results_for_task(
    task_id: int,
    passed: Optional[bool] = Query(default=None),
    db: Session = Depends(get_db),
):
    """Return all results for a given task, optionally filtered by pass/fail."""
    if not db.query(Task).filter(Task.id == task_id).first():
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    q = db.query(Result).filter(Result.task_id == task_id)
    if passed is not None:
        q = q.filter(Result.passed == passed)
    return q.all()


@app.get("/results/{result_id}", response_model=ResultRead, tags=["Results"])
def get_result(result_id: int, db: Session = Depends(get_db)):
    r = db.query(Result).filter(Result.id == result_id).first()
    if not r:
        raise HTTPException(status_code=404, detail=f"Result {result_id} not found")
    return r


# ---------------------------------------------------------------------------
# 进度查询（前端轮询用）
# ---------------------------------------------------------------------------


@app.get("/tasks/{task_id}/progress", tags=["Tasks"])
def get_task_progress(task_id: int, db: Session = Depends(get_db)):
    """
    返回当前评测进度，供前端轮询。
    { status, completed, total, percent }
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    completed = db.query(Result).filter(Result.task_id == task_id).count()

    total = db.query(Question).filter(
        Question.dataset_name == task.dataset_name
    ).count()
    if total == 0:
        total = db.query(Question).count()

    return {
        "task_id":   task_id,
        "status":    task.status,
        "completed": completed,
        "total":     total,
        "percent":   round(completed / total * 100) if total else 0,
    }


# ---------------------------------------------------------------------------
# 多模型对比接口
# ---------------------------------------------------------------------------


@app.get("/compare", tags=["Compare"])
def compare_tasks(
    dataset: Optional[str] = Query(default=None, description="按题库过滤，留空则取所有"),
    db: Session = Depends(get_db),
):
    """
    返回指定 dataset 下所有已完成任务的聚合报告，供对比视图使用。
    每个任务只取最新一条（按 id 降序），避免同一模型重复跑多次造成噪声。
    """
    q = db.query(Task).filter(Task.status == TaskStatus.completed)
    if dataset:
        q = q.filter(Task.dataset_name == dataset)
    tasks = q.order_by(Task.id.desc()).all()

    # 每个 model_name 只保留最新的一条
    seen: set[str] = set()
    deduped = []
    for t in tasks:
        key = f"{t.model_name}||{t.dataset_name}"
        if key not in seen:
            seen.add(key)
            deduped.append(t)

    reports = []
    for t in deduped:
        try:
            r = MetricsCalculator(db).compute(t.id)
            reports.append({
                "task_id":            r.task_id,
                "model_name":         r.model_name,
                "dataset_name":       r.dataset_name,
                "total_results":      r.total_results,
                "passed_count":       r.passed_count,
                "failed_count":       r.failed_count,
                "pass_rate":          r.pass_rate,
                "pass_at_1":          r.pass_at_1,
                "avg_execution_time": r.avg_execution_time,
                "syntax_errors":      r.syntax_errors,
                "runtime_errors":     r.runtime_errors,
                "assertion_errors":   r.assertion_errors,
                "timeout_errors":     r.timeout_errors,
                "other_errors":       r.other_errors,
            })
        except Exception:
            pass  # 跳过无法计算的任务

    # 按 pass_at_1 降序排列（最优模型在前）
    reports.sort(key=lambda x: x["pass_at_1"], reverse=True)
    return reports


# ---------------------------------------------------------------------------
# Report route
# ---------------------------------------------------------------------------


@app.get("/api/tasks/{task_id}/report", response_model=TaskReportSchema, tags=["Report"])
def get_task_report(task_id: int, db: Session = Depends(get_db)):
    """
    Return aggregated evaluation metrics for a completed task.

    Metrics include:
    - pass_rate        — overall fraction of passed results
    - pass_at_1        — fraction of unique questions solved on first attempt
    - avg_execution_time — mean wall-clock time of passing results (seconds)
    - error_distribution — pie-chart breakdown by error kind
    """
    if not db.query(Task).filter(Task.id == task_id).first():
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    try:
        report = MetricsCalculator(db).compute(task_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return TaskReportSchema(
        task_id=report.task_id,
        model_name=report.model_name,
        dataset_name=report.dataset_name,
        status=report.status,
        total_results=report.total_results,
        passed_count=report.passed_count,
        failed_count=report.failed_count,
        pass_rate=report.pass_rate,
        pass_at_1=report.pass_at_1,
        avg_execution_time=report.avg_execution_time,
        error_distribution=[
            {"label": b.label, "count": b.count, "ratio": b.ratio}
            for b in report.error_distribution
        ],
        syntax_errors=report.syntax_errors,
        runtime_errors=report.runtime_errors,
        assertion_errors=report.assertion_errors,
        timeout_errors=report.timeout_errors,
        other_errors=report.other_errors,
    )


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@app.get("/health", tags=["System"])
def health():
    return {"status": "ok", "service": "EvalForge"}
