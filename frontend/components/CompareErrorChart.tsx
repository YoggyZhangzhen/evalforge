"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { ModelCompareRow } from "@/lib/api";

interface Props {
  data: ModelCompareRow[];
}

const ERROR_BARS = [
  { key: "syntax_errors",    label: "语法错误",   color: "#fb923c" },
  { key: "runtime_errors",   label: "运行时错误", color: "#f87171" },
  { key: "assertion_errors", label: "答案错误",   color: "#facc15" },
  { key: "timeout_errors",   label: "执行超时",   color: "#a78bfa" },
  { key: "other_errors",     label: "其他异常",   color: "#64748b" },
] as const;

interface TooltipPayload {
  name: string;
  value: number;
  color: string;
}

function CustomTooltip({ active, payload, label }: {
  active?: boolean;
  payload?: TooltipPayload[];
  label?: string;
}) {
  if (!active || !payload?.length) return null;
  const total = payload.reduce((s, p) => s + (p.value ?? 0), 0);
  return (
    <div className="bg-forge-surface border border-forge-border rounded-md px-3 py-2 text-xs shadow-xl space-y-1 min-w-[160px]">
      <p className="font-semibold text-forge-text mb-2">{label}</p>
      {payload.filter((p) => p.value > 0).map((p) => (
        <div key={p.name} className="flex items-center justify-between gap-4">
          <span className="flex items-center gap-1.5 text-forge-subtext">
            <span className="w-2 h-2 rounded-sm flex-shrink-0" style={{ background: p.color }} />
            {p.name}
          </span>
          <span className="text-forge-text tabular-nums">{p.value}</span>
        </div>
      ))}
      <div className="border-t border-forge-border mt-1 pt-1 flex justify-between text-forge-muted">
        <span>失败合计</span>
        <span>{total}</span>
      </div>
    </div>
  );
}

export default function CompareErrorChart({ data }: Props) {
  const chartData = data.map((d) => ({
    model_name:        d.model_name,
    语法错误:          d.syntax_errors,
    运行时错误:        d.runtime_errors,
    答案错误:          d.assertion_errors,
    执行超时:          d.timeout_errors,
    其他异常:          d.other_errors,
  }));

  const hasErrors = data.some((d) =>
    d.syntax_errors + d.runtime_errors + d.assertion_errors +
    d.timeout_errors + d.other_errors > 0
  );

  return (
    <div className="card space-y-3">
      <h3 className="text-sm font-semibold text-forge-text flex items-center gap-2">
        <span className="w-1.5 h-4 rounded-sm bg-forge-red" />
        错误类型分布对比
      </h3>

      {!hasErrors ? (
        <div className="h-48 flex items-center justify-center text-forge-muted text-sm gap-2">
          <span className="text-2xl">✓</span>
          <span>所有模型均无失败用例</span>
        </div>
      ) : (
        <>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 4, right: 8, left: -8, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                <XAxis
                  dataKey="model_name"
                  tick={{ fill: "#94a3b8", fontSize: 11 }}
                  axisLine={{ stroke: "#1f2937" }}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fill: "#94a3b8", fontSize: 11 }}
                  axisLine={false}
                  tickLine={false}
                  allowDecimals={false}
                />
                <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(255,255,255,0.04)" }} />
                <Legend
                  wrapperStyle={{ fontSize: 11, color: "#94a3b8", paddingTop: 8 }}
                />
                {ERROR_BARS.map((bar) => (
                  <Bar
                    key={bar.key}
                    dataKey={bar.label}
                    stackId="errors"
                    fill={bar.color}
                    radius={bar.key === "other_errors" ? [4, 4, 0, 0] : [0, 0, 0, 0]}
                    maxBarSize={56}
                  />
                ))}
              </BarChart>
            </ResponsiveContainer>
          </div>
          <p className="text-[11px] text-forge-muted">每段颜色代表该类错误的数量，越矮越好</p>
        </>
      )}
    </div>
  );
}
