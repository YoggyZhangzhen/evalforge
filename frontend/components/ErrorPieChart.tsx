"use client";

import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { ErrorBucket, TaskReport } from "@/lib/api";

// Palette aligned with dark theme
const PALETTE = [
  "#f87171",   // red    — runtime error
  "#facc15",   // yellow — assertion / wrong answer
  "#fb923c",   // orange — syntax error
  "#a78bfa",   // violet — timeout
  "#64748b",   // slate  — other
];

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{ name: string; value: number; payload: ErrorBucket & { fill: string } }>;
}

function CustomTooltip({ active, payload }: CustomTooltipProps) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="bg-forge-surface border border-forge-border rounded-md px-3 py-2 text-xs shadow-xl">
      <p className="font-semibold text-forge-text mb-1">{d.label}</p>
      <p className="text-forge-subtext">
        数量：<span className="text-forge-text">{d.count}</span>
      </p>
      <p className="text-forge-subtext">
        占比：<span className="text-forge-text">{(d.ratio * 100).toFixed(1)}%</span>
      </p>
    </div>
  );
}

interface LegendItemProps {
  label: string;
  color: string;
  count: number;
  ratio: number;
}

function LegendItem({ label, color, count, ratio }: LegendItemProps) {
  return (
    <div className="flex items-center justify-between gap-4 py-1.5 border-b border-forge-border/50 last:border-0">
      <div className="flex items-center gap-2 min-w-0">
        <span className="w-2.5 h-2.5 rounded-sm flex-shrink-0" style={{ background: color }} />
        <span className="text-xs text-forge-subtext truncate">{label}</span>
      </div>
      <div className="flex items-center gap-3 flex-shrink-0 text-xs tabular-nums">
        <span className="text-forge-text font-medium">{count}</span>
        <span className="text-forge-muted w-10 text-right">{(ratio * 100).toFixed(1)}%</span>
      </div>
    </div>
  );
}

interface Props {
  report: TaskReport | null;
}

export default function ErrorPieChart({ report }: Props) {
  if (!report || report.failed_count === 0) {
    return (
      <div className="card flex flex-col items-center justify-center h-64 text-forge-muted text-sm gap-2">
        <span className="text-3xl">✓</span>
        <span>暂无失败用例</span>
      </div>
    );
  }

  const data = report.error_distribution.map((b, i) => ({
    ...b,
    fill: PALETTE[i % PALETTE.length],
  }));

  return (
    <div className="card">
      <h3 className="text-sm font-semibold text-forge-text mb-4 flex items-center gap-2">
        <span className="w-1.5 h-4 rounded-sm bg-forge-accent" />
        错误类型分布
        <span className="text-forge-muted font-normal text-xs ml-auto">
          共 {report.failed_count} 次失败
        </span>
      </h3>

      <div className="flex flex-col lg:flex-row gap-6 items-center">
        {/* Pie */}
        <div className="w-full lg:w-56 h-52 flex-shrink-0">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={55}
                outerRadius={85}
                paddingAngle={3}
                dataKey="count"
                strokeWidth={0}
              >
                {data.map((entry, i) => (
                  <Cell key={i} fill={entry.fill} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Legend table */}
        <div className="flex-1 w-full">
          {data.map((d, i) => (
            <LegendItem
              key={i}
              label={d.label}
              color={d.fill}
              count={d.count}
              ratio={d.ratio}
            />
          ))}
          {/* Summary row */}
          <div className="flex items-center justify-between pt-2 mt-1 text-xs font-semibold text-forge-text">
            <span>失败总计</span>
            <span>{report.failed_count}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
