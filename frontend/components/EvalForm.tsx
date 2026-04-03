"use client";

import { useState } from "react";
import { Play, ChevronDown, Cpu, Database } from "lucide-react";
import { api, Task } from "@/lib/api";

const LLM_MODELS = [
  { value: "gpt-4o",              label: "GPT-4o",              provider: "OpenAI"   },
  { value: "gpt-4o-mini",         label: "GPT-4o mini",         provider: "OpenAI"   },
  { value: "deepseek-coder",      label: "DeepSeek Coder",      provider: "DeepSeek" },
  { value: "deepseek-chat",       label: "DeepSeek Chat",       provider: "DeepSeek" },
  { value: "moonshot-v1-8k",      label: "Moonshot v1-8k",      provider: "Moonshot" },
  { value: "qwen2.5-coder-7b",    label: "Qwen2.5 Coder 7B",   provider: "Alibaba"  },
];

const DATASETS = [
  { value: "HumanEval",     label: "HumanEval",      desc: "164 道人工编写的 Python 编程题" },
  { value: "MBPP",          label: "MBPP",            desc: "基础 Python 编程问题集" },
  { value: "LeetCode-Easy", label: "LeetCode 简单级", desc: "精选简单级算法题" },
  { value: "Custom",        label: "自定义题库",      desc: "使用数据库中的自定义题目" },
];

interface Props {
  onTaskCreated: (task: Task) => void;
}

export default function EvalForm({ onTaskCreated }: Props) {
  const [model,   setModel]   = useState(LLM_MODELS[0].value);
  const [dataset, setDataset] = useState(DATASETS[0].value);
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const task = await api.createTask(model, dataset);
      onTaskCreated(task);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "创建任务失败，请检查后端连接";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  const selectedModel   = LLM_MODELS.find((m) => m.value === model)!;
  const selectedDataset = DATASETS.find((d)  => d.value === dataset)!;

  return (
    <form onSubmit={handleSubmit} className="card space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3 pb-2 border-b border-forge-border">
        <span className="text-forge-accent text-lg">⬡</span>
        <div>
          <h2 className="text-forge-text font-semibold text-sm">新建评测任务</h2>
          <p className="text-forge-subtext text-xs mt-0.5">
            选择模型和题库，点击启动开始评测
          </p>
        </div>
      </div>

      {/* Two-column grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
        {/* Model selector */}
        <div className="space-y-2">
          <label className="flex items-center gap-1.5 text-xs text-forge-subtext uppercase tracking-wider">
            <Cpu size={12} className="text-forge-accent" />
            选择模型
          </label>
          <div className="relative">
            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="input appearance-none pr-8 cursor-pointer"
            >
              {LLM_MODELS.map((m) => (
                <option key={m.value} value={m.value}>
                  [{m.provider}] {m.label}
                </option>
              ))}
            </select>
            <ChevronDown
              size={14}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-forge-subtext pointer-events-none"
            />
          </div>
          <p className="text-xs text-forge-muted">
            服务商：<span className="text-forge-accent">{selectedModel.provider}</span>
          </p>
        </div>

        {/* Dataset selector */}
        <div className="space-y-2">
          <label className="flex items-center gap-1.5 text-xs text-forge-subtext uppercase tracking-wider">
            <Database size={12} className="text-forge-accent" />
            选择题库
          </label>
          <div className="relative">
            <select
              value={dataset}
              onChange={(e) => setDataset(e.target.value)}
              className="input appearance-none pr-8 cursor-pointer"
            >
              {DATASETS.map((d) => (
                <option key={d.value} value={d.value}>
                  {d.label}
                </option>
              ))}
            </select>
            <ChevronDown
              size={14}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-forge-subtext pointer-events-none"
            />
          </div>
          <p className="text-xs text-forge-muted">{selectedDataset.desc}</p>
        </div>
      </div>

      {/* Config preview */}
      <div className="bg-forge-bg border border-forge-border rounded-md px-4 py-3 font-mono text-xs text-forge-subtext">
        <span className="text-forge-muted">$ </span>
        <span className="text-forge-green">evalforge run</span>
        <span className="text-forge-text"> --model </span>
        <span className="text-forge-accent">{model}</span>
        <span className="text-forge-text"> --dataset </span>
        <span className="text-forge-accent">{dataset}</span>
      </div>

      {/* Error */}
      {error && (
        <div className="flex items-start gap-2 text-forge-red bg-red-950/50 border border-red-900 rounded-md px-4 py-3 text-xs">
          <span className="mt-0.5">✖</span>
          <span>{error}</span>
        </div>
      )}

      {/* Submit */}
      <div className="flex justify-end">
        <button type="submit" className="btn-primary flex items-center gap-2" disabled={loading}>
          {loading ? (
            <>
              <span className="w-3.5 h-3.5 border-2 border-forge-bg border-t-transparent rounded-full animate-spin" />
              启动中…
            </>
          ) : (
            <>
              <Play size={14} />
              开始评测
            </>
          )}
        </button>
      </div>
    </form>
  );
}
