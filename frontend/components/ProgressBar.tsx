"use client";

import { useEffect, useRef, useState } from "react";
import { api, Task, TaskProgress } from "@/lib/api";
import clsx from "clsx";

interface Props {
  task: Task;
  onCompleted: () => void;
  onStatusChange: (status: Task["status"]) => void;
}

export default function ProgressBar({ task, onCompleted, onStatusChange }: Props) {
  const [progress, setProgress] = useState<TaskProgress | null>(null);
  const [cancelling, setCancelling] = useState(false);
  const completedRef = useRef(false);

  const isDone = ["completed", "failed", "cancelled"].includes(task.status);

  useEffect(() => {
    if (isDone) return;

    completedRef.current = false;

    const tick = async () => {
      try {
        const p = await api.getProgress(task.id);
        setProgress(p);
        onStatusChange(p.status);

        if (["completed", "failed", "cancelled"].includes(p.status) && !completedRef.current) {
          completedRef.current = true;
          onCompleted();
        }
      } catch {
        // 网络抖动不影响轮询
      }
    };

    tick();
    const id = setInterval(tick, 1500);
    return () => clearInterval(id);
  }, [task.id, task.status, onCompleted, onStatusChange, isDone]);

  if (isDone) return null;

  const pct     = progress?.percent ?? 0;
  const done    = progress?.completed ?? 0;
  const total   = progress?.total ?? 0;
  const running = progress?.status === "running";

  async function handleCancel() {
    setCancelling(true);
    try {
      await api.cancelTask(task.id);
      onStatusChange("cancelled");
      onCompleted();
    } catch {
      // ignore
    } finally {
      setCancelling(false);
    }
  }

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
        <div className="flex items-center gap-3">
          <span className="text-forge-accent font-mono font-semibold tabular-nums">
            {done} / {total} 题
          </span>
          <button
            onClick={handleCancel}
            disabled={cancelling}
            className="px-2 py-0.5 rounded border border-forge-red/50 text-forge-red
                       hover:bg-forge-red/10 transition-colors disabled:opacity-40 text-[11px]"
          >
            {cancelling ? "终止中…" : "■ 终止"}
          </button>
        </div>
      </div>

      {/* 进度条轨道 */}
      <div className="relative h-2 bg-forge-muted/30 rounded-full overflow-hidden">
        <div
          className={clsx(
            "absolute inset-y-0 left-0 rounded-full transition-all duration-500",
            pct === 100 ? "bg-forge-green" : "bg-forge-accent"
          )}
          style={{ width: `${pct}%` }}
        />
        {running && pct < 100 && (
          <div className="absolute inset-y-0 left-0 w-full animate-[shimmer_1.5s_ease-in-out_infinite]"
               style={{
                 background: "linear-gradient(90deg,transparent 0%,rgba(34,211,238,0.25) 50%,transparent 100%)",
               }}
          />
        )}
      </div>

      {/* 百分比 */}
      <div className="flex items-center justify-between text-[11px] text-forge-muted font-mono">
        <span>{pct}%</span>
        {done > 0 && <span>最新完成：题目 #{done}</span>}
      </div>
    </div>
  );
}
