"use client";

import { useCallback, useEffect, useState } from "react";
import { api, Question } from "@/lib/api";
import QuestionCard    from "@/components/QuestionCard";
import AddQuestionModal from "@/components/AddQuestionModal";
import { Plus, RefreshCw, Search, Database } from "lucide-react";
import clsx from "clsx";

export default function QuestionsPage() {
  const [questions,       setQuestions]       = useState<Question[]>([]);
  const [datasets,        setDatasets]        = useState<string[]>([]);
  const [activeDataset,   setActiveDataset]   = useState<string>("__all__");
  const [search,          setSearch]          = useState("");
  const [loading,         setLoading]         = useState(false);
  const [showAddModal,    setShowAddModal]    = useState(false);

  // ── 初始化 ──────────────────────────────────────────────────────
  const fetchAll = useCallback(async () => {
    setLoading(true);
    try {
      const [qs, ds] = await Promise.all([
        api.listQuestions(undefined, 200),
        api.listDatasets(),
      ]);
      setQuestions(qs);
      setDatasets(ds);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  // ── 删除 ────────────────────────────────────────────────────────
  async function handleDelete(id: number) {
    await api.deleteQuestion(id);
    setQuestions((prev) => prev.filter((q) => q.id !== id));
    // 重新拉取 dataset 列表（可能某个 dataset 已经空了）
    api.listDatasets().then(setDatasets);
  }

  // ── 新建完成 ────────────────────────────────────────────────────
  function handleCreated(q: Question) {
    setQuestions((prev) => [...prev, q]);
    setDatasets((prev) => prev.includes(q.dataset_name) ? prev : [...prev, q.dataset_name]);
    setActiveDataset(q.dataset_name);
    setShowAddModal(false);
  }

  // ── 过滤 ────────────────────────────────────────────────────────
  const filtered = questions.filter((q) => {
    const matchDataset = activeDataset === "__all__" || q.dataset_name === activeDataset;
    const keyword = search.trim().toLowerCase();
    const matchSearch = !keyword
      || q.description.toLowerCase().includes(keyword)
      || q.function_signature.toLowerCase().includes(keyword);
    return matchDataset && matchSearch;
  });

  // ── 按 dataset 分组统计 ─────────────────────────────────────────
  const countByDataset = questions.reduce<Record<string, number>>((acc, q) => {
    acc[q.dataset_name] = (acc[q.dataset_name] ?? 0) + 1;
    return acc;
  }, {});

  return (
    <div className="space-y-6">
      {/* 页头 */}
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-bold text-forge-text tracking-tight">题库管理</h1>
          <p className="text-forge-subtext text-sm mt-1">
            管理评测题目，每道题包含函数签名和测试用例
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={fetchAll}
            disabled={loading}
            className="btn-ghost flex items-center gap-1.5"
            title="刷新"
          >
            <RefreshCw size={13} className={loading ? "animate-spin" : ""} />
            刷新
          </button>
          <button
            onClick={() => setShowAddModal(true)}
            className="btn-primary flex items-center gap-2"
          >
            <Plus size={14} />
            新增题目
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-[220px_1fr] gap-5 items-start">

        {/* ── 左侧：Dataset 分类栏 ──────────────────────────────── */}
        <div className="card space-y-1">
          <p className="text-xs uppercase tracking-wider text-forge-subtext mb-3 flex items-center gap-1.5">
            <Database size={11} className="text-forge-accent" />
            题库
          </p>

          {/* 全部 */}
          <button
            onClick={() => setActiveDataset("__all__")}
            className={clsx(
              "w-full flex items-center justify-between px-3 py-2 rounded-md text-sm transition-colors",
              activeDataset === "__all__"
                ? "bg-cyan-950/30 text-forge-accent border border-forge-accent/40"
                : "text-forge-subtext hover:bg-forge-muted/20"
            )}
          >
            <span>全部题目</span>
            <span className="text-xs tabular-nums text-forge-muted">{questions.length}</span>
          </button>

          {/* 各 dataset */}
          {datasets.map((ds) => (
            <button
              key={ds}
              onClick={() => setActiveDataset(ds)}
              className={clsx(
                "w-full flex items-center justify-between px-3 py-2 rounded-md text-sm transition-colors",
                activeDataset === ds
                  ? "bg-cyan-950/30 text-forge-accent border border-forge-accent/40"
                  : "text-forge-subtext hover:bg-forge-muted/20"
              )}
            >
              <span className="truncate text-left">{ds}</span>
              <span className="text-xs tabular-nums text-forge-muted flex-shrink-0 ml-1">
                {countByDataset[ds] ?? 0}
              </span>
            </button>
          ))}

          {datasets.length === 0 && !loading && (
            <p className="text-xs text-forge-muted text-center py-4">暂无题库</p>
          )}
        </div>

        {/* ── 右侧：题目列表 ───────────────────────────────────── */}
        <div className="space-y-4">
          {/* 搜索框 */}
          <div className="relative">
            <Search
              size={13}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-forge-muted pointer-events-none"
            />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="搜索题目描述或函数名…"
              className="input pl-8"
            />
          </div>

          {/* 统计行 */}
          <div className="flex items-center justify-between text-xs text-forge-muted">
            <span>
              显示 <span className="text-forge-text">{filtered.length}</span> /
              共 <span className="text-forge-text">{questions.length}</span> 道题
            </span>
            {activeDataset !== "__all__" && (
              <span className="text-forge-accent">{activeDataset}</span>
            )}
          </div>

          {/* 骨架屏 */}
          {loading && (
            <div className="space-y-2">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="h-14 bg-forge-muted/20 animate-pulse rounded-lg" />
              ))}
            </div>
          )}

          {/* 题目卡片列表 */}
          {!loading && filtered.length === 0 && (
            <div className="card flex flex-col items-center justify-center py-16 text-forge-muted gap-3">
              <span className="text-4xl opacity-20">📭</span>
              <p className="text-sm">
                {search ? "没有匹配的题目" : "该题库暂无题目"}
              </p>
              <button
                onClick={() => setShowAddModal(true)}
                className="btn-ghost text-xs flex items-center gap-1"
              >
                <Plus size={11} /> 立即新增
              </button>
            </div>
          )}

          {!loading && filtered.length > 0 && (
            <div className="space-y-2">
              {filtered.map((q) => (
                <QuestionCard key={q.id} question={q} onDelete={handleDelete} />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* 新增题目弹窗 */}
      {showAddModal && (
        <AddQuestionModal
          datasets={datasets}
          onClose={() => setShowAddModal(false)}
          onCreated={handleCreated}
        />
      )}
    </div>
  );
}
