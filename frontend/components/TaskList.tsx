"use client";

import { Task, TaskStatus } from "@/lib/api";
import clsx from "clsx";
import { ChevronRight } from "lucide-react";

const STATUS_STYLES: Record<TaskStatus, string> = {
  pending:   "bg-yellow-950/40 text-forge-yellow  border-yellow-900/60",
  running:   "bg-cyan-950/40   text-forge-accent   border-cyan-900/60 animate-pulse",
  completed: "bg-green-950/40  text-forge-green    border-green-900/60",
  failed:    "bg-red-950/40    text-forge-red      border-red-900/60",
};

const STATUS_LABELS: Record<TaskStatus, string> = {
  pending:   "待运行",
  running:   "运行中",
  completed: "已完成",
  failed:    "已失败",
};

interface Props {
  tasks: Task[];
  selectedId: number | null;
  onSelect: (task: Task) => void;
  loading: boolean;
}

export default function TaskList({ tasks, selectedId, onSelect, loading }: Props) {
  if (loading) {
    return (
      <div className="space-y-2">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="h-14 bg-forge-muted/20 animate-pulse rounded-lg" />
        ))}
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <div className="text-center py-8 text-forge-muted text-xs">
        暂无任务，请在上方创建
      </div>
    );
  }

  return (
    <div className="space-y-1.5">
      {tasks.map((t) => (
        <button
          key={t.id}
          onClick={() => onSelect(t)}
          className={clsx(
            "w-full flex items-center gap-3 px-4 py-3 rounded-lg border text-left",
            "transition-all duration-150 group",
            selectedId === t.id
              ? "border-forge-accent bg-cyan-950/20 text-forge-text"
              : "border-forge-border bg-forge-surface hover:border-forge-muted text-forge-subtext",
          )}
        >
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-0.5">
              <span className="text-xs font-semibold text-forge-text truncate">
                {t.model_name}
              </span>
              <span
                className={clsx(
                  "text-[10px] px-1.5 py-0.5 rounded border font-medium flex-shrink-0",
                  STATUS_STYLES[t.status],
                )}
              >
                {STATUS_LABELS[t.status]}
              </span>
            </div>
            <div className="flex items-center gap-2 text-[11px] text-forge-muted">
              <span className="truncate">{t.dataset_name}</span>
              <span>·</span>
              <span className="flex-shrink-0">
                #{t.id} · {new Date(t.created_at).toLocaleDateString()}
              </span>
            </div>
          </div>
          <ChevronRight
            size={14}
            className={clsx(
              "flex-shrink-0 transition-transform duration-150",
              selectedId === t.id ? "text-forge-accent translate-x-0.5" : "text-forge-muted",
            )}
          />
        </button>
      ))}
    </div>
  );
}
