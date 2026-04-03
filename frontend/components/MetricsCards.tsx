"use client";

import { TaskReport } from "@/lib/api";
import { TrendingUp, CheckCircle, Clock, AlertTriangle } from "lucide-react";
import clsx from "clsx";

interface StatCardProps {
  icon: React.ReactNode;
  label: string;
  value: string;
  sub?: string;
  accent?: "cyan" | "green" | "yellow" | "red";
  loading?: boolean;
}

function StatCard({ icon, label, value, sub, accent = "cyan", loading }: StatCardProps) {
  const accentMap = {
    cyan:   "text-forge-accent border-forge-accent/30 bg-cyan-950/20",
    green:  "text-forge-green  border-green-900/50   bg-green-950/20",
    yellow: "text-forge-yellow border-yellow-900/50  bg-yellow-950/20",
    red:    "text-forge-red    border-red-900/50      bg-red-950/20",
  };

  return (
    <div className={clsx("card flex items-start gap-4 border", accentMap[accent])}>
      <div className={clsx("p-2 rounded-md border", accentMap[accent])}>{icon}</div>
      <div className="flex-1 min-w-0">
        <p className="text-forge-subtext text-xs uppercase tracking-wider mb-1">{label}</p>
        {loading ? (
          <div className="h-7 w-20 bg-forge-muted/30 animate-pulse rounded" />
        ) : (
          <p className="text-2xl font-bold text-forge-text tabular-nums">{value}</p>
        )}
        {sub && <p className="text-forge-muted text-xs mt-1">{sub}</p>}
      </div>
    </div>
  );
}

interface Props {
  report: TaskReport | null;
  loading: boolean;
}

export default function MetricsCards({ report, loading }: Props) {
  const passRate   = report ? `${(report.pass_rate * 100).toFixed(1)}%`  : "—";
  const passAt1    = report ? `${(report.pass_at_1  * 100).toFixed(1)}%` : "—";
  const avgTime    = report?.avg_execution_time != null
    ? `${report.avg_execution_time.toFixed(3)}s`
    : "—";
  const failedRate = report
    ? `${((report.failed_count / (report.total_results || 1)) * 100).toFixed(1)}%`
    : "—";

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard
        icon={<TrendingUp size={16} className="text-forge-accent" />}
        label="Pass@1"
        value={passAt1}
        sub={report ? `${report.passed_count} / ${report.total_results} 题通过` : undefined}
        accent="cyan"
        loading={loading}
      />
      <StatCard
        icon={<CheckCircle size={16} className="text-forge-green" />}
        label="通过率"
        value={passRate}
        sub={report ? `${report.passed_count} 题通过` : undefined}
        accent="green"
        loading={loading}
      />
      <StatCard
        icon={<Clock size={16} className="text-forge-yellow" />}
        label="平均执行耗时"
        value={avgTime}
        sub="仅统计通过用例"
        accent="yellow"
        loading={loading}
      />
      <StatCard
        icon={<AlertTriangle size={16} className="text-forge-red" />}
        label="失败率"
        value={failedRate}
        sub={report ? `${report.failed_count} 题失败` : undefined}
        accent="red"
        loading={loading}
      />
    </div>
  );
}
