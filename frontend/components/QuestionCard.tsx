"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp, Trash2 } from "lucide-react";
import { Question } from "@/lib/api";
import clsx from "clsx";

interface Props {
  question: Question;
  onDelete: (id: number) => void;
}

export default function QuestionCard({ question: q, onDelete }: Props) {
  const [expanded, setExpanded] = useState(false);
  const [confirming, setConfirming] = useState(false);

  function handleDelete() {
    if (!confirming) { setConfirming(true); return; }
    onDelete(q.id);
  }

  return (
    <div className={clsx(
      "border rounded-lg transition-colors duration-150",
      expanded ? "border-forge-accent/50 bg-cyan-950/10" : "border-forge-border bg-forge-surface",
    )}>
      {/* 题目头部 */}
      <div className="flex items-start gap-3 px-4 py-3">
        {/* ID badge */}
        <span className="flex-shrink-0 mt-0.5 text-[10px] font-mono text-forge-muted
                         bg-forge-muted/20 border border-forge-border rounded px-1.5 py-0.5">
          #{q.id}
        </span>

        {/* 描述 + 签名 */}
        <div className="flex-1 min-w-0">
          <p className="text-sm text-forge-text leading-snug">{q.description}</p>
          <code className="text-xs text-forge-accent font-mono mt-1 block truncate">
            {q.function_signature}
          </code>
        </div>

        {/* 操作 */}
        <div className="flex items-center gap-1 flex-shrink-0">
          <span className="text-[10px] text-forge-muted mr-1 hidden sm:block">
            {q.test_cases.length} 用例
          </span>

          {/* 删除按钮 */}
          <button
            onClick={handleDelete}
            onBlur={() => setConfirming(false)}
            className={clsx(
              "p-1.5 rounded text-xs transition-colors",
              confirming
                ? "bg-red-950/60 text-forge-red border border-red-900 px-2"
                : "text-forge-muted hover:text-forge-red hover:bg-red-950/30"
            )}
            title={confirming ? "再次点击确认删除" : "删除题目"}
          >
            {confirming ? "确认删除?" : <Trash2 size={13} />}
          </button>

          {/* 展开按钮 */}
          <button
            onClick={() => setExpanded((v) => !v)}
            className="p-1.5 rounded text-forge-muted hover:text-forge-text transition-colors"
          >
            {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          </button>
        </div>
      </div>

      {/* 展开的测试用例 */}
      {expanded && (
        <div className="px-4 pb-4 space-y-2 border-t border-forge-border/50 pt-3">
          <p className="text-xs text-forge-subtext uppercase tracking-wider mb-2">测试用例</p>
          {q.test_cases.map((tc, idx) => (
            <div
              key={idx}
              className="flex items-center gap-3 text-xs font-mono bg-forge-bg
                         border border-forge-border rounded-md px-3 py-2"
            >
              <span className="text-forge-muted w-4 flex-shrink-0">{idx + 1}</span>
              <span className="text-forge-accent flex-1 truncate">{String(tc.input)}</span>
              <span className="text-forge-muted flex-shrink-0">→</span>
              <span className="text-forge-green flex-shrink-0">{String(tc.expected_output)}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
