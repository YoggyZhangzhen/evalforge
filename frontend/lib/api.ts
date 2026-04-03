import axios from "axios";

// ---------------------------------------------------------------------------
// Types (mirror backend Pydantic schemas)
// ---------------------------------------------------------------------------

export type TaskStatus = "pending" | "running" | "completed" | "failed";

export interface Task {
  id: number;
  model_name: string;
  dataset_name: string;
  status: TaskStatus;
  created_at: string;
  updated_at: string | null;
}

export interface ResultRow {
  id: number;
  task_id: number;
  question_id: number;
  generated_code: string | null;
  execution_time: number | null;
  passed: boolean | null;
  error_log: string | null;
  created_at: string;
}

export interface ErrorBucket {
  label: string;
  count: number;
  ratio: number;
}

export interface TaskReport {
  task_id: number;
  model_name: string;
  dataset_name: string;
  status: string;
  total_results: number;
  passed_count: number;
  failed_count: number;
  pass_rate: number;
  pass_at_1: number;
  avg_execution_time: number | null;
  error_distribution: ErrorBucket[];
  syntax_errors: number;
  runtime_errors: number;
  assertion_errors: number;
  timeout_errors: number;
  other_errors: number;
}

export interface Question {
  id: number;
  dataset_name: string;
  description: string;
  function_signature: string;
  test_cases: Array<{ input: unknown; expected_output: unknown }>;
}

export interface ModelCompareRow {
  task_id: number;
  model_name: string;
  dataset_name: string;
  total_results: number;
  passed_count: number;
  failed_count: number;
  pass_rate: number;
  pass_at_1: number;
  avg_execution_time: number | null;
  syntax_errors: number;
  runtime_errors: number;
  assertion_errors: number;
  timeout_errors: number;
  other_errors: number;
}

export interface QuestionCreate {
  dataset_name: string;
  description: string;
  function_signature: string;
  test_cases: Array<{ input: string; expected_output: string }>;
}

export interface TaskProgress {
  task_id: number;
  status: TaskStatus;
  completed: number;
  total: number;
  percent: number;
}

// ---------------------------------------------------------------------------
// Axios instance
// ---------------------------------------------------------------------------

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ||
  (typeof window !== "undefined" ? "/api" : "http://localhost:8000");

export const http = axios.create({
  baseURL: API_BASE,
  timeout: 15_000,
  headers: { "Content-Type": "application/json" },
});

// Attach JWT token on every request (reads from localStorage at call time)
http.interceptors.request.use((cfg) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("evalforge_token");
    if (token) cfg.headers.Authorization = `Bearer ${token}`;
  }
  return cfg;
});

// ---------------------------------------------------------------------------
// API helpers
// ---------------------------------------------------------------------------

export const api = {
  // Tasks
  createTask: (model_name: string, dataset_name: string) =>
    http.post<Task>("/tasks", { model_name, dataset_name }).then((r) => r.data),

  listTasks: (status?: TaskStatus, limit = 20, offset = 0) =>
    http
      .get<Task[]>("/tasks", { params: { status, limit, offset } })
      .then((r) => r.data),

  getTask: (id: number) =>
    http.get<Task & { results: ResultRow[] }>(`/tasks/${id}`).then((r) => r.data),

  updateTaskStatus: (id: number, status: TaskStatus) =>
    http.patch<Task>(`/tasks/${id}/status`, { status }).then((r) => r.data),

  // Report
  getReport: (taskId: number) =>
    http.get<TaskReport>(`/api/tasks/${taskId}/report`).then((r) => r.data),

  // Results
  listResultsForTask: (taskId: number, passed?: boolean) =>
    http
      .get<ResultRow[]>(`/tasks/${taskId}/results`, { params: { passed } })
      .then((r) => r.data),

  // Progress
  getProgress: (taskId: number) =>
    http.get<TaskProgress>(`/tasks/${taskId}/progress`).then((r) => r.data),

  // Questions
  listQuestions: (dataset?: string, limit = 100) =>
    http.get<Question[]>("/questions", { params: { dataset, limit } }).then((r) => r.data),

  createQuestion: (payload: QuestionCreate) =>
    http.post<Question>("/questions", payload).then((r) => r.data),

  deleteQuestion: (id: number) =>
    http.delete(`/questions/${id}`),

  listDatasets: () =>
    http.get<string[]>("/questions/datasets").then((r) => r.data),

  // Compare
  compareModels: (dataset?: string) =>
    http.get<ModelCompareRow[]>("/compare", { params: { dataset } }).then((r) => r.data),
};
