"use client";

import { useEffect, useRef, useState } from "react";
import { api, Task, TaskProgress } from "@/lib/api";
import clsx from "clsx";

interface Props {
  task: Task;
  /** 评测完成后回调，用于刷新报告和结果 */
  onCompleted: () => void;
  /** 任务状态变化时同步给父组件 */
  onStatusChange: (status: Task["status"]) => void;
}

export default function ProgressBar({ task, onCompleted, onStatusChange }: Props) {
  const [progress, setProgress] = useState<TaskProgress | null>(null);
  const completedRef = useRef(false);

  useEffect(() => {
    // 已完成/失败不需要轮询
    if (task.status === "completed" || task.status === "failed") return;

    completedRef.current = false;

    const tick = async () => {
      try {
        const p = await api.getProgress(task.id);
        setProgress(p);
        onStatusChange(p.status);

        if ((p.status === "completed" || p.status === "failed") && !completedRef.current) {
          completedRef.current = true;
          onCompleted();
        }
      } catch {
        // 网络抖动不影响轮询
      }
    };

    tick(); // 立即执行一次
    const id = setInterval(tick, 1500);
    return () => clearInterval(id);
  }, [task.id, task.status, onCompleted, onStatusChange]);

  // 已完成任务不显示进度条
  if (task.status === "completed" || task.status === "failed") return null;

  const pct     = progress?.percent ?? 0;
  const done    = progress?.completed ?? 0;
  const total   = progress?.total ?? 0;
  const running = progress?.status === "running";

  return (
    <div className="card space-y-3">
      {/* 头部 */}
      <div className="flex items-center justify-between text-xs">
        <span className="text-forge-subtext flex items-center gap-2">
          {running && (
            <span className="w-1.5 h-1.5 rounded-full bg-forge-accent animate-pulse" />
          )}
          {running ? "评测进行中…" : "准备启动…"}
        </span>
        <span className="text-forge-accent font-mono font-semibold tabular-nums">
          {done} / {total} 题
        </span>
      </div>

      {/* 进度条轨道 */}
      <div className="relative h-2 bg-forge-muted/30 rounded-full overflow-hidden">
        {/* 填充条 */}
        <div
          className={clsx(
            "absolute inset-y-0 left-0 rounded-full transition-all duration-500",
            pct === 100 ? "bg-forge-green" : "bg-forge-accent"
          )}
          style={{ width: `${pct}%` }}
        />
        {/* 光扫动画（仅运行时） */}
        {running && pct < 100 && (
          <div className="absolute inset-y-0 left-0 w-full animate-[shimmer_1.5s_ease-in-out_infinite]"
               style={{
                 background: "linear-gradient(90deg,transparent 0%,rgba(34,211,238,0.25) 50%,transparent 100%)",
               }}
          />
        )}
      </div>

      {/* 百分比 + 每题日志 */}
      <div className="flex items-center justify-between text-[11px] text-forge-muted font-mono">
        <span>{pct}%</span>
        {done > 0 && (
          <span>最新完成：题目 #{done}</span>
        )}
      </div>
    </div>
  );
}
