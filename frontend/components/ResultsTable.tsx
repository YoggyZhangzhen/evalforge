"use client";

import { useState } from "react";
import { ChevronUp, ChevronDown, Eye, Filter } from "lucide-react";
import { ResultRow } from "@/lib/api";
import CodeModal from "./CodeModal";
import clsx from "clsx";

type SortKey = "question_id" | "execution_time" | "passed";
type SortDir = "asc" | "desc";
type FilterVal = "all" | "passed" | "failed";

interface Props {
  results: ResultRow[];
  loading: boolean;
}

export default function ResultsTable({ results, loading }: Props) {
  const [sortKey, setSortKey]   = useState<SortKey>("question_id");
  const [sortDir, setSortDir]   = useState<SortDir>("asc");
  const [filter,  setFilter]    = useState<FilterVal>("all");
  const [selected, setSelected] = useState<ResultRow | null>(null);

  function toggleSort(key: SortKey) {
    if (sortKey === key) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else { setSortKey(key); setSortDir("asc"); }
  }

  const filtered = results.filter((r) => {
    if (filter === "passed") return r.passed === true;
    if (filter === "failed") return r.passed !== true;
    return true;
  });

  const sorted = [...filtered].sort((a, b) => {
    let av: number | boolean | null = a[sortKey];
    let bv: number | boolean | null = b[sortKey];
    if (av == null) av = sortDir === "asc" ? Infinity : -Infinity;
    if (bv == null) bv = sortDir === "asc" ? Infinity : -Infinity;
    if (typeof av === "boolean") av = av ? 1 : 0;
    if (typeof bv === "boolean") bv = bv ? 1 : 0;
    return sortDir === "asc" ? (av as number) - (bv as number) : (bv as number) - (av as number);
  });

  function SortIcon({ col }: { col: SortKey }) {
    if (sortKey !== col) return <ChevronUp size={12} className="opacity-20" />;
    return sortDir === "asc"
      ? <ChevronUp   size={12} className="text-forge-accent" />
      : <ChevronDown size={12} className="text-forge-accent" />;
  }

  function Th({
    label, col, className,
  }: { label: string; col?: SortKey; className?: string }) {
    return (
      <th
        onClick={col ? () => toggleSort(col) : undefined}
        className={clsx(
          "px-4 py-3 text-left text-xs uppercase tracking-wider text-forge-subtext",
          "border-b border-forge-border",
          col && "cursor-pointer hover:text-forge-text select-none",
          className,
        )}
      >
        <span className="flex items-center gap-1">
          {label}
          {col && <SortIcon col={col} />}
        </span>
      </th>
    );
  }

  return (
    <>
      <div className="card">
        {/* Table header */}
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-forge-text flex items-center gap-2">
            <span className="w-1.5 h-4 rounded-sm bg-forge-green" />
            逐题评测结果
            <span className="text-forge-muted font-normal text-xs">
              ({filtered.length} / {results.length})
            </span>
          </h3>

          {/* Filter pills */}
          <div className="flex items-center gap-1 text-xs">
            <Filter size={12} className="text-forge-subtext mr-1" />
            {(["all", "passed", "failed"] as FilterVal[]).map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={clsx(
                  "px-3 py-1 rounded-full border transition-colors duration-150",
                  filter === f
                    ? "border-forge-accent text-forge-accent bg-cyan-950/30"
                    : "border-forge-border text-forge-subtext hover:border-forge-muted",
                )}
              >
                {{ all: "全部", passed: "通过", failed: "失败" }[f]}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div className="space-y-2">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="h-10 bg-forge-muted/20 animate-pulse rounded" />
            ))}
          </div>
        ) : sorted.length === 0 ? (
          <div className="text-center py-12 text-forge-muted text-sm">
            当前筛选条件下暂无结果
          </div>
        ) : (
          <div className="overflow-x-auto -mx-5 px-5">
            <table className="w-full text-sm">
              <thead>
                <tr>
                  <Th label="题目"     col="question_id"    className="w-16"  />
                  <Th label="状态"     col="passed"         className="w-28"  />
                  <Th label="执行耗时" col="execution_time" className="w-32"  />
                  <Th label="错误摘要"                                         />
                  <Th label="操作"     className="w-24 text-right"           />
                </tr>
              </thead>
              <tbody>
                {sorted.map((r) => (
                  <tr
                    key={r.id}
                    className="border-b border-forge-border/50 hover:bg-forge-border/20
                               transition-colors duration-100"
                  >
                    {/* Q# */}
                    <td className="px-4 py-3 font-mono text-forge-subtext">
                      #{r.question_id}
                    </td>

                    {/* Status badge */}
                    <td className="px-4 py-3">
                      {r.passed === true  && <span className="badge-pass">✓ 通过</span>}
                      {r.passed === false && <span className="badge-fail">✗ 失败</span>}
                      {r.passed == null   && <span className="badge-pending">? 待测</span>}
                    </td>

                    {/* Exec time */}
                    <td className="px-4 py-3 font-mono text-forge-subtext tabular-nums">
                      {r.execution_time != null
                        ? `${r.execution_time.toFixed(3)}s`
                        : <span className="text-forge-muted">—</span>
                      }
                    </td>

                    {/* Error summary */}
                    <td className="px-4 py-3 max-w-xs">
                      {r.error_log ? (
                        <span className="text-forge-red text-xs font-mono truncate block">
                          {r.error_log.split("\n")[0].slice(0, 80)}
                          {r.error_log.length > 80 && "…"}
                        </span>
                      ) : (
                        <span className="text-forge-muted text-xs">—</span>
                      )}
                    </td>

                    {/* Actions */}
                    <td className="px-4 py-3 text-right">
                      <button
                        onClick={() => setSelected(r)}
                        className="btn-ghost flex items-center gap-1.5 ml-auto"
                        title="查看代码与日志"
                      >
                        <Eye size={12} />
                        查看
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <CodeModal result={selected} onClose={() => setSelected(null)} />
    </>
  );
}
