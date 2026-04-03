import os
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
    text,
)
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker

# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./evalforge.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _migrate() -> None:
    """为旧版数据库补充新增列，幂等操作。"""
    try:
        with engine.connect() as conn:
            conn.execute(text(
                "ALTER TABLE questions ADD COLUMN dataset_name VARCHAR(256) NOT NULL DEFAULT 'HumanEval'"
            ))
            conn.commit()
    except Exception:
        pass  # 列已存在，忽略


_migrate()


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# SQLAlchemy ORM models
# ---------------------------------------------------------------------------


class User(Base):
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True, index=True)
    username   = Column(String(64), unique=True, nullable=False, index=True)
    hashed_pwd = Column(String(256), nullable=False)
    is_admin   = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class TaskStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(128), nullable=False)
    dataset_name = Column(String(256), nullable=False)
    status = Column(String(32), default=TaskStatus.pending, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    results = relationship("Result", back_populates="task", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    dataset_name = Column(String(256), nullable=False, default="HumanEval", index=True)
    description = Column(Text, nullable=False)
    function_signature = Column(Text, nullable=False)
    test_cases = Column(JSON, nullable=False)  # list of {input, expected_output}

    results = relationship("Result", back_populates="question")


class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    generated_code = Column(Text, nullable=True)
    execution_time = Column(Float, nullable=True)   # seconds
    passed = Column(Boolean, nullable=True)
    error_log = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    task = relationship("Task", back_populates="results")
    question = relationship("Question", back_populates="results")


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


# --- Task ---

class TaskCreate(BaseModel):
    model_name: str = Field(..., min_length=1, max_length=128, examples=["gpt-4o"])
    dataset_name: str = Field(..., min_length=1, max_length=256, examples=["HumanEval"])


class TaskRead(BaseModel):
    id: int
    model_name: str
    dataset_name: str
    status: TaskStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class TaskStatusUpdate(BaseModel):
    status: TaskStatus


# --- Question ---

class TestCase(BaseModel):
    input: Any
    expected_output: Any


class QuestionCreate(BaseModel):
    dataset_name: str = Field(default="HumanEval", min_length=1, max_length=256)
    description: str = Field(..., min_length=1)
    function_signature: str = Field(..., min_length=1)
    test_cases: list[TestCase] = Field(..., min_length=1)


class QuestionRead(BaseModel):
    id: int
    dataset_name: str
    description: str
    function_signature: str
    test_cases: list[TestCase]

    model_config = {"from_attributes": True}


# --- Result ---

class ResultCreate(BaseModel):
    task_id: int
    question_id: int
    generated_code: Optional[str] = None
    execution_time: Optional[float] = Field(default=None, ge=0)
    passed: Optional[bool] = None
    error_log: Optional[str] = None


class ResultRead(BaseModel):
    id: int
    task_id: int
    question_id: int
    generated_code: Optional[str] = None
    execution_time: Optional[float] = None
    passed: Optional[bool] = None
    error_log: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Task detail (task + all its results) ---

class TaskDetail(TaskRead):
    results: list[ResultRead] = []


# --- Report / Metrics ---

class ErrorBucketSchema(BaseModel):
    label: str
    count: int
    ratio: float


class TaskReportSchema(BaseModel):
    task_id: int
    model_name: str
    dataset_name: str
    status: str

    total_results: int
    passed_count: int
    failed_count: int

    pass_rate: float
    pass_at_1: float
    avg_execution_time: Optional[float]

    error_distribution: list[ErrorBucketSchema]

    syntax_errors: int
    runtime_errors: int
    assertion_errors: int
    timeout_errors: int
    other_errors: int


# --- Auth ---

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=64, pattern=r"^\w+$")
    password: str = Field(..., min_length=6, max_length=128)


class UserLogin(BaseModel):
    username: str
    password: str


class UserRead(BaseModel):
    id: int
    username: str
    is_admin: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead
