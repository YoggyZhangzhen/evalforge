"use client";

import { useCallback, useEffect, useState } from "react";
import { api, ModelCompareRow } from "@/lib/api";
import CompareBarChart   from "@/components/CompareBarChart";
import CompareErrorChart from "@/components/CompareErrorChart";
import { RefreshCw, Trophy, ChevronDown } from "lucide-react";
import clsx from "clsx";

// 排行榜徽章
const RANK_BADGE = ["🥇", "🥈", "🥉"];

function RankTable({ data }: { data: ModelCompareRow[] }) {
  return (
    <div className="card overflow-x-auto">
      <h3 className="text-sm font-semibold text-forge-text mb-4 flex items-center gap-2">
        <Trophy size={14} className="text-forge-yellow" />
        模型排行榜
        <span className="text-forge-muted font-normal text-xs ml-auto">按 Pass@1 降序</span>
      </h3>
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-forge-border text-left">
            {["排名", "模型", "题库", "Pass@1", "通过率", "平均耗时", "语法错", "运行错", "答案错", "超时"].map((h) => (
              <th key={h} className="px-3 py-2 text-xs text-forge-subtext uppercase tracking-wider font-medium">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((d, i) => (
            <tr
              key={d.task_id}
              className={clsx(
                "border-b border-forge-border/50 transition-colors hover:bg-forge-border/20",
                i === 0 && "bg-yellow-950/10"
              )}
            >
              <td className="px-3 py-3 text-base">{RANK_BADGE[i] ?? `#${i + 1}`}</td>
              <td className="px-3 py-3 font-mono text-forge-accent text-xs">{d.model_name}</td>
              <td className="px-3 py-3 text-forge-muted text-xs">{d.dataset_name}</td>

              {/* Pass@1 */}
              <td className="px-3 py-3">
                <span className={clsx(
                  "font-bold tabular-nums",
                  d.pass_at_1 >= 0.8 ? "text-forge-green"
                  : d.pass_at_1 >= 0.5 ? "text-forge-yellow"
                  : "text-forge-red"
                )}>
                  {(d.pass_at_1 * 100).toFixed(1)}%
                </span>
              </td>

              {/* 通过率 */}
              <td className="px-3 py-3 tabular-nums text-forge-text">
                {(d.pass_rate * 100).toFixed(1)}%
              </td>

              {/* 平均耗时 */}
              <td className="px-3 py-3 font-mono text-forge-subtext tabular-nums text-xs">
                {d.avg_execution_time != null ? `${d.avg_execution_time.toFixed(3)}s` : "—"}
              </td>

              {/* 错误分类 */}
              <td className="px-3 py-3 text-forge-orange tabular-nums text-xs">
                {d.syntax_errors || "—"}
              </td>
              <td className="px-3 py-3 text-forge-red tabular-nums text-xs">
                {d.runtime_errors || "—"}
              </td>
              <td className="px-3 py-3 text-forge-yellow tabular-nums text-xs">
                {d.assertion_errors || "—"}
              </td>
              <td className="px-3 py-3 text-forge-accent tabular-nums text-xs">
                {d.timeout_errors || "—"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function ComparePage() {
  const [data,          setData]          = useState<ModelCompareRow[]>([]);
  const [datasets,      setDatasets]      = useState<string[]>([]);
  const [activeDataset, setActiveDataset] = useState<string>("");
  const [loading,       setLoading]       = useState(false);

  const fetchDatasets = useCallback(async () => {
    const ds = await api.listDatasets();
    setDatasets(ds);
    if (ds.length > 0 && !activeDataset) setActiveDataset(ds[0]);
  }, [activeDataset]);

  const fetchCompare = useCallback(async () => {
    setLoading(true);
    try {
      const rows = await api.compareModels(activeDataset || undefined);
      setData(rows);
    } finally {
      setLoading(false);
    }
  }, [activeDataset]);

  useEffect(() => { fetchDatasets(); }, [fetchDatasets]);
  useEffect(() => { if (activeDataset !== undefined) fetchCompare(); }, [fetchCompare, activeDataset]);

  const noData = !loading && data.length === 0;
  const singleModel = data.length === 1;

  return (
    <div className="space-y-6">
      {/* 页头 */}
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-bold text-forge-text tracking-tight">模型对比</h1>
          <p className="text-forge-subtext text-sm mt-1">
            横向对比同一题库下多个模型的评测表现
          </p>
        </div>
        <div className="flex items-center gap-2">
          {/* Dataset 选择 */}
          <div className="relative">
            <select
              value={activeDataset}
              onChange={(e) => setActiveDataset(e.target.value)}
              className="input pr-7 text-xs appearance-none cursor-pointer"
            >
              <option value="">全部题库</option>
              {datasets.map((d) => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>
            <ChevronDown size={12} className="absolute right-2 top-1/2 -translate-y-1/2 text-forge-subtext pointer-events-none" />
          </div>
          <button
            onClick={fetchCompare}
            disabled={loading}
            className="btn-ghost flex items-center gap-1.5"
          >
            <RefreshCw size={13} className={loading ? "animate-spin" : ""} />
            刷新
          </button>
        </div>
      </div>

      {/* 空状态 */}
      {noData && (
        <div className="card flex flex-col items-center justify-center py-20 text-forge-muted gap-3">
          <span className="text-4xl opacity-20">📊</span>
          <p className="text-sm">暂无已完成的评测任务</p>
          <p className="text-xs">请先在「评测控制台」完成至少两个模型的评测</p>
        </div>
      )}

      {/* 只有一个模型时提示 */}
      {singleModel && (
        <div className="bg-yellow-950/30 border border-yellow-900/50 rounded-lg px-4 py-3 text-forge-yellow text-xs">
          当前题库下只有 1 个模型的评测数据，再跑一个模型即可生成对比图表
        </div>
      )}

      {/* 排行榜 */}
      {data.length > 0 && <RankTable data={data} />}

      {/* 图表区（至少两个模型才显示） */}
      {data.length >= 2 && (
        <>
          {/* 三张核心指标柱状图 */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            <CompareBarChart
              data={data}
              metric="pass_at_1"
              title="Pass@1 对比"
            />
            <CompareBarChart
              data={data}
              metric="pass_rate"
              title="通过率对比"
            />
            <CompareBarChart
              data={data}
              metric="avg_execution_time"
              title="平均耗时对比"
              lowerIsBetter
            />
          </div>

          {/* 错误类型堆叠图 */}
          <CompareErrorChart data={data} />
        </>
      )}
    </div>
  );
}
