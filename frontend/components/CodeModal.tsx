"use client";

import { useEffect, useRef } from "react";
import { X, Copy, Check } from "lucide-react";
import { useState } from "react";
import { ResultRow } from "@/lib/api";

interface Props {
  result: ResultRow | null;
  questionId?: number;
  onClose: () => void;
}

export default function CodeModal({ result, onClose }: Props) {
  const [copied, setCopied] = useState(false);
  const overlayRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  if (!result) return null;

  async function copyCode() {
    await navigator.clipboard.writeText(result?.generated_code ?? "");
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  return (
    <div
      ref={overlayRef}
      className="fixed inset-0 z-50 flex items-center justify-center p-4
                 bg-black/70 backdrop-blur-sm"
      onClick={(e) => { if (e.target === overlayRef.current) onClose(); }}
    >
      <div className="bg-forge-surface border border-forge-border rounded-xl
                      w-full max-w-3xl max-h-[85vh] flex flex-col shadow-2xl">
        {/* Modal header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-forge-border">
          <div className="flex items-center gap-3">
            <span
              className={result.passed ? "badge-pass" : "badge-fail"}
            >
              {result.passed ? "✓ 通过" : "✗ 失败"}
            </span>
            <span className="text-forge-subtext text-xs">
              题目 #{result.question_id} · 结果 #{result.id}
            </span>
            {result.execution_time != null && (
              <span className="text-forge-muted text-xs">
                {result.execution_time.toFixed(3)}s
              </span>
            )}
          </div>
          <button
            onClick={onClose}
            className="text-forge-subtext hover:text-forge-text transition-colors p-1 rounded"
          >
            <X size={16} />
          </button>
        </div>

        <div className="overflow-y-auto flex-1 p-5 space-y-5">
          {/* Generated Code */}
          <section>
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-xs uppercase tracking-wider text-forge-subtext">
                生成代码
              </h4>
              <button
                onClick={copyCode}
                className="flex items-center gap-1 text-xs text-forge-subtext
                           hover:text-forge-accent transition-colors"
              >
                {copied ? <Check size={12} /> : <Copy size={12} />}
                {copied ? "已复制！" : "复制"}
              </button>
            </div>
            <pre
              className="bg-forge-bg border border-forge-border rounded-md
                         p-4 text-xs text-forge-text overflow-x-auto leading-relaxed
                         font-mono"
            >
              {result.generated_code
                ? <code>{result.generated_code}</code>
                : <span className="text-forge-muted italic">暂无生成代码</span>
              }
            </pre>
          </section>

          {/* Error Log */}
          {result.error_log && (
            <section>
              <h4 className="text-xs uppercase tracking-wider text-forge-subtext mb-2">
                错误日志
              </h4>
              <pre
                className="bg-red-950/30 border border-red-900/50 rounded-md
                           p-4 text-xs text-forge-red overflow-x-auto leading-relaxed
                           font-mono whitespace-pre-wrap"
              >
                {result.error_log}
              </pre>
            </section>
          )}
        </div>

        {/* Footer */}
        <div className="px-5 py-3 border-t border-forge-border flex justify-end">
          <button onClick={onClose} className="btn-ghost">
            关闭
          </button>
        </div>
      </div>
    </div>
  );
}
