"use client";

import { useState } from "react";
import { X, Plus, Trash2 } from "lucide-react";
import { api, Question, QuestionCreate } from "@/lib/api";
import clsx from "clsx";

interface TestCaseRow {
  input: string;
  expected_output: string;
}

interface Props {
  datasets: string[];
  onClose: () => void;
  onCreated: (q: Question) => void;
}

const DEFAULT_DATASET = "HumanEval";

export default function AddQuestionModal({ datasets, onClose, onCreated }: Props) {
  const [datasetName,       setDatasetName]       = useState(datasets[0] ?? DEFAULT_DATASET);
  const [newDataset,        setNewDataset]        = useState("");
  const [useNewDataset,     setUseNewDataset]     = useState(datasets.length === 0);
  const [description,       setDescription]       = useState("");
  const [functionSignature, setFunctionSignature] = useState("");
  const [testCases,         setTestCases]         = useState<TestCaseRow[]>([
    { input: "", expected_output: "" },
  ]);
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState<string | null>(null);

  function addTestCase() {
    setTestCases((prev) => [...prev, { input: "", expected_output: "" }]);
  }

  function removeTestCase(idx: number) {
    setTestCases((prev) => prev.filter((_, i) => i !== idx));
  }

  function updateTestCase(idx: number, field: keyof TestCaseRow, value: string) {
    setTestCases((prev) =>
      prev.map((tc, i) => (i === idx ? { ...tc, [field]: value } : tc))
    );
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    const finalDataset = useNewDataset ? newDataset.trim() : datasetName;
    if (!finalDataset) { setError("题库名称不能为空"); return; }

    const emptyCase = testCases.findIndex((tc) => !tc.input.trim() || !tc.expected_output.trim());
    if (emptyCase >= 0) { setError(`测试用例 #${emptyCase + 1} 输入或期望输出为空`); return; }

    const payload: QuestionCreate = {
      dataset_name:       finalDataset,
      description:        description.trim(),
      function_signature: functionSignature.trim(),
      test_cases:         testCases,
    };

    setLoading(true);
    try {
      const q = await api.createQuestion(payload);
      onCreated(q);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "创建失败");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4
                 bg-black/70 backdrop-blur-sm"
      onClick={(e) => { if (e.currentTarget === e.target) onClose(); }}
    >
      <div className="bg-forge-surface border border-forge-border rounded-xl
                      w-full max-w-2xl max-h-[90vh] flex flex-col shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-forge-border">
          <h2 className="text-sm font-semibold text-forge-text">新增题目</h2>
          <button onClick={onClose} className="text-forge-subtext hover:text-forge-text p-1 rounded">
            <X size={16} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="overflow-y-auto flex-1 p-6 space-y-5">
          {/* Dataset */}
          <div className="space-y-2">
            <label className="text-xs text-forge-subtext uppercase tracking-wider">所属题库</label>
            <div className="flex gap-2">
              {!useNewDataset ? (
                <select
                  value={datasetName}
                  onChange={(e) => setDatasetName(e.target.value)}
                  className="input flex-1"
                >
                  {datasets.map((d) => <option key={d} value={d}>{d}</option>)}
                </select>
              ) : (
                <input
                  value={newDataset}
                  onChange={(e) => setNewDataset(e.target.value)}
                  placeholder="输入新题库名称，如 MyDataset"
                  className="input flex-1"
                />
              )}
              <button
                type="button"
                onClick={() => setUseNewDataset((v) => !v)}
                className="btn-ghost flex-shrink-0 text-xs"
              >
                {useNewDataset ? "选已有题库" : "+ 新建题库"}
              </button>
            </div>
          </div>

          {/* Description */}
          <div className="space-y-2">
            <label className="text-xs text-forge-subtext uppercase tracking-wider">题目描述</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="用自然语言描述函数的功能，例如：返回两个整数的和"
              rows={3}
              required
              className="input resize-none"
            />
          </div>

          {/* Function signature */}
          <div className="space-y-2">
            <label className="text-xs text-forge-subtext uppercase tracking-wider">函数签名</label>
            <input
              value={functionSignature}
              onChange={(e) => setFunctionSignature(e.target.value)}
              placeholder="def add(a: int, b: int) -> int:"
              required
              className="input font-mono"
            />
            <p className="text-xs text-forge-muted">LLM 将以此为起点补全函数体</p>
          </div>

          {/* Test cases */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-xs text-forge-subtext uppercase tracking-wider">
                测试用例 ({testCases.length})
              </label>
              <button
                type="button"
                onClick={addTestCase}
                className="flex items-center gap-1 text-xs text-forge-accent hover:brightness-110 transition-all"
              >
                <Plus size={12} /> 添加用例
              </button>
            </div>

            <div className="space-y-2">
              {testCases.map((tc, idx) => (
                <div key={idx} className="flex gap-2 items-start">
                  <span className="text-forge-muted text-xs mt-2.5 w-4 flex-shrink-0">
                    {idx + 1}
                  </span>
                  <input
                    value={tc.input}
                    onChange={(e) => updateTestCase(idx, "input", e.target.value)}
                    placeholder={`调用表达式，如 add(1, 2)`}
                    className="input flex-1 font-mono text-xs"
                  />
                  <span className="text-forge-muted text-xs mt-2.5 flex-shrink-0">→</span>
                  <input
                    value={tc.expected_output}
                    onChange={(e) => updateTestCase(idx, "expected_output", e.target.value)}
                    placeholder="期望返回值，如 3"
                    className="input flex-1 font-mono text-xs"
                  />
                  <button
                    type="button"
                    onClick={() => removeTestCase(idx)}
                    disabled={testCases.length === 1}
                    className={clsx(
                      "mt-1.5 p-1.5 rounded text-forge-muted transition-colors flex-shrink-0",
                      testCases.length > 1
                        ? "hover:text-forge-red hover:bg-red-950/40"
                        : "opacity-30 cursor-not-allowed"
                    )}
                  >
                    <Trash2 size={13} />
                  </button>
                </div>
              ))}
            </div>

            <div className="bg-forge-bg border border-forge-border rounded-md px-3 py-2 text-xs text-forge-muted space-y-1">
              <p className="text-forge-subtext font-medium">格式说明</p>
              <p>· 调用表达式直接写函数调用，如 <code className="text-forge-accent">add(1, 2)</code></p>
              <p>· 期望值写 Python 字面量，如 <code className="text-forge-accent">3</code>、<code className="text-forge-accent">True</code>、<code className="text-forge-accent">"hello"</code></p>
            </div>
          </div>

          {error && (
            <div className="flex items-start gap-2 text-forge-red bg-red-950/40 border border-red-900 rounded-md px-4 py-3 text-xs">
              <span>✖</span><span>{error}</span>
            </div>
          )}
        </form>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-forge-border flex justify-end gap-2">
          <button onClick={onClose} className="btn-ghost">取消</button>
          <button
            onClick={(e) => handleSubmit(e as unknown as React.FormEvent)}
            disabled={loading || !description.trim() || !functionSignature.trim()}
            className="btn-primary flex items-center gap-2"
          >
            {loading ? (
              <><span className="w-3 h-3 border-2 border-forge-bg border-t-transparent rounded-full animate-spin" />保存中…</>
            ) : "保存题目"}
          </button>
        </div>
      </div>
    </div>
  );
}
