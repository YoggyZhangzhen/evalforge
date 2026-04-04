"use client";

import { useCallback, useEffect, useState } from "react";
import { api, Task, TaskReport, ResultRow } from "@/lib/api";
import EvalForm       from "@/components/EvalForm";
import MetricsCards   from "@/components/MetricsCards";
import ErrorPieChart  from "@/components/ErrorPieChart";
import ResultsTable   from "@/components/ResultsTable";
import TaskList       from "@/components/TaskList";
import ProgressBar    from "@/components/ProgressBar";
import { RefreshCw, BarChart2, List } from "lucide-react";

export default function HomePage() {
  const [tasks,       setTasks]       = useState<Task[]>([]);
  const [taskLoading, setTaskLoading] = useState(false);

  const [selectedTask,  setSelectedTask]  = useState<Task | null>(null);
  const [report,        setReport]        = useState<TaskReport | null>(null);
  const [results,       setResults]       = useState<ResultRow[]>([]);
  const [detailLoading, setDetailLoading] = useState(false);
  const [liveStatus,    setLiveStatus]    = useState<Task["status"] | null>(null);

  // ── Load task list ────────────────────────────────────────────────
  const fetchTasks = useCallback(async () => {
    setTaskLoading(true);
    try {
      const data = await api.listTasks(undefined, 50);
      setTasks(data);
    } finally {
      setTaskLoading(false);
    }
  }, []);

  useEffect(() => { fetchTasks(); }, [fetchTasks]);

  // ── Load task detail when selection changes ───────────────────────
  useEffect(() => {
    if (!selectedTask) return;
    setDetailLoading(true);
    setReport(null);
    setResults([]);

    Promise.allSettled([
      api.getReport(selectedTask.id),
      api.listResultsForTask(selectedTask.id),
    ]).then(([reportRes, resultsRes]) => {
      if (reportRes.status  === "fulfilled") setReport(reportRes.value);
      if (resultsRes.status === "fulfilled") setResults(resultsRes.value);
    }).finally(() => setDetailLoading(false));
  }, [selectedTask]);

  // ── Handle new task created ───────────────────────────────────────
  function handleTaskCreated(task: Task) {
    setTasks((prev) => [task, ...prev]);
    setSelectedTask(task);
    setLiveStatus(task.status);
  }

  // ── 评测完成后刷新报告+结果（由 ProgressBar 触发）────────────────
  const handleCompleted = useCallback(() => {
    if (!selectedTask) return;
    Promise.allSettled([
      api.getReport(selectedTask.id),
      api.listResultsForTask(selectedTask.id),
    ]).then(([reportRes, resultsRes]) => {
      if (reportRes.status  === "fulfilled") setReport(reportRes.value);
      if (resultsRes.status === "fulfilled") setResults(resultsRes.value);
    });
    // 同步任务列表状态
    fetchTasks();
  }, [selectedTask, fetchTasks]);

  // ── ProgressBar 回调：实时同步状态标签 ───────────────────────────
  const handleStatusChange = useCallback((s: Task["status"]) => {
    setLiveStatus(s);
    setTasks((prev) =>
      prev.map((t) => (t.id === selectedTask?.id ? { ...t, status: s } : t))
    );
  }, [selectedTask?.id]);

  return (
    <div className="space-y-8">
      {/* ── Page title ─────────────────────────────────────────── */}
      <div className="space-y-1">
        <h1 className="text-2xl font-bold text-forge-text tracking-tight">
          评测控制台
        </h1>
        <p className="text-forge-subtext text-sm">
          基于标准题库，对大模型代码生成能力进行系统性评测
        </p>
      </div>

      {/* ── Main layout: sidebar + content ──────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-[320px_1fr] gap-6 items-start">

        {/* LEFT COLUMN */}
        <div className="space-y-5">
          {/* Config form */}
          <EvalForm onTaskCreated={handleTaskCreated} />

          {/* Task list */}
          <div className="card space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs uppercase tracking-wider text-forge-subtext flex items-center gap-1.5">
                <List size={12} className="text-forge-accent" />
                历史任务
              </h3>
              <button
                onClick={fetchTasks}
                disabled={taskLoading}
                className="text-forge-subtext hover:text-forge-accent transition-colors p-1 rounded"
                title="Refresh"
              >
                <RefreshCw size={13} className={taskLoading ? "animate-spin" : ""} />
              </button>
            </div>
            <TaskList
              tasks={tasks}
              selectedId={selectedTask?.id ?? null}
              onSelect={setSelectedTask}
              loading={taskLoading}
            />
          </div>
        </div>

        {/* RIGHT COLUMN */}
        <div className="space-y-5">
          {!selectedTask ? (
            <EmptyState />
          ) : (
            <>
              {/* Task meta bar */}
              <div className="flex items-center gap-3 flex-wrap">
                <div className="bg-forge-surface border border-forge-border rounded-md
                                px-3 py-1.5 text-xs font-mono text-forge-subtext flex items-center gap-2">
                  <BarChart2 size={12} className="text-forge-accent" />
                  <span className="text-forge-accent">{selectedTask.model_name}</span>
                  <span className="text-forge-muted">·</span>
                  <span className="text-forge-text">{selectedTask.dataset_name}</span>
                  <span className="text-forge-muted">· 任务 #{selectedTask.id}</span>
                </div>
                {(() => {
                  const s = liveStatus ?? selectedTask.status;
                  return (
                    <span className={`text-xs px-2 py-1 rounded border font-medium
                      ${s === "completed" ? "badge-pass"
                      : s === "failed"    ? "badge-fail"
                      : s === "cancelled" ? "border-forge-muted text-forge-muted"
                      : s === "running"   ? "badge-pending"
                      : "border-forge-border text-forge-subtext"}`}>
                      {s === "running" && (
                        <span className="inline-block w-1.5 h-1.5 rounded-full bg-forge-yellow animate-pulse mr-1" />
                      )}
                      {{ pending: "待运行", running: "运行中", completed: "已完成", failed: "已失败", cancelled: "已取消" }[s]}
                    </span>
                  );
                })()}
              </div>

              {/* 进度条（评测运行中时显示） */}
              <ProgressBar
                task={{ ...selectedTask, status: liveStatus ?? selectedTask.status }}
                onCompleted={handleCompleted}
                onStatusChange={handleStatusChange}
              />

              {/* Metrics cards */}
              <MetricsCards report={report} loading={detailLoading} />

              {/* Chart + Table (two-column on wide screens) */}
              <div className="grid grid-cols-1 xl:grid-cols-[auto_1fr] gap-5 items-start">
                <div className="xl:w-80">
                  <ErrorPieChart report={report} />
                </div>
                <ResultsTable results={results} loading={detailLoading} />
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="card flex flex-col items-center justify-center py-20 text-center gap-4">
      <div className="text-5xl opacity-20 select-none">⬡</div>
      <div>
        <p className="text-forge-text font-semibold mb-1">未选择任务</p>
        <p className="text-forge-muted text-sm">
          在左侧新建评测任务，或从历史任务中选择一条
        </p>
      </div>
      <div className="mt-2 font-mono text-xs text-forge-muted bg-forge-bg border
                      border-forge-border rounded-md px-4 py-2">
        <span className="text-forge-muted">$ </span>
        <span className="text-forge-green">evalforge</span>
        <span className="text-forge-subtext"> select --task &lt;id&gt;</span>
      </div>
    </div>
  );
}
