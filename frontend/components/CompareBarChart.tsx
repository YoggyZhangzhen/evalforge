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
  Cell,
} from "recharts";
import { ModelCompareRow } from "@/lib/api";

interface Props {
  data: ModelCompareRow[];
  /** "pass_at_1" | "pass_rate" | "avg_execution_time" */
  metric: "pass_at_1" | "pass_rate" | "avg_execution_time";
  title: string;
  unit?: string;
  /** 是否越小越好（执行耗时） */
  lowerIsBetter?: boolean;
}

// 每个模型固定一个颜色，最多 8 种
const COLORS = [
  "#22d3ee", // cyan
  "#4ade80", // green
  "#f472b6", // pink
  "#fb923c", // orange
  "#a78bfa", // violet
  "#facc15", // yellow
  "#38bdf8", // sky
  "#f87171", // red
];

interface TooltipPayload {
  payload: ModelCompareRow & { fill: string };
  value: number;
}

function CustomTooltip({
  active, payload, unit, lowerIsBetter,
}: {
  active?: boolean;
  payload?: TooltipPayload[];
  label?: string;
  unit?: string;
  lowerIsBetter?: boolean;
}) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  const val = payload[0].value;
  return (
    <div className="bg-forge-surface border border-forge-border rounded-md px-3 py-2 text-xs shadow-xl space-y-1">
      <p className="font-semibold text-forge-text">{d.model_name}</p>
      <p className="text-forge-subtext">
        数值：<span className="text-forge-accent">{val}{unit}</span>
        {lowerIsBetter && <span className="text-forge-muted ml-1">（越低越好）</span>}
      </p>
      <p className="text-forge-muted">通过 {d.passed_count} / {d.total_results} 题</p>
    </div>
  );
}

export default function CompareBarChart({ data, metric, title, unit = "", lowerIsBetter = false }: Props) {
  const chartData = data.map((d, i) => ({
    ...d,
    // 百分比类指标乘 100；耗时保留 3 位小数
    value: metric === "avg_execution_time"
      ? d.avg_execution_time != null ? Math.round(d.avg_execution_time * 1000) / 1000 : 0
      : Math.round((d[metric] ?? 0) * 1000) / 10,
    fill: COLORS[i % COLORS.length],
  }));

  const displayUnit = metric === "avg_execution_time" ? unit || "s" : unit || "%";

  // 找最优值用于高亮
  const best = lowerIsBetter
    ? Math.min(...chartData.map((d) => d.value))
    : Math.max(...chartData.map((d) => d.value));

  return (
    <div className="card space-y-3">
      <h3 className="text-sm font-semibold text-forge-text flex items-center gap-2">
        <span className="w-1.5 h-4 rounded-sm bg-forge-accent" />
        {title}
      </h3>
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
              unit={displayUnit}
            />
            <Tooltip
              content={<CustomTooltip unit={displayUnit} lowerIsBetter={lowerIsBetter} />}
              cursor={{ fill: "rgba(255,255,255,0.04)" }}
            />
            <Bar dataKey="value" radius={[4, 4, 0, 0]} maxBarSize={56}>
              {chartData.map((entry, i) => (
                <Cell
                  key={i}
                  fill={entry.value === best ? entry.fill : entry.fill + "99"}
                  stroke={entry.value === best ? entry.fill : "transparent"}
                  strokeWidth={1.5}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <p className="text-[11px] text-forge-muted text-right">
        {lowerIsBetter ? "★ 高亮为最低值" : "★ 高亮为最高值"}
      </p>
    </div>
  );
}
