"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { http } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [tab, setTab] = useState<"login" | "register">("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const endpoint = tab === "login" ? "/auth/login" : "/auth/register";
      const res = await http.post<{ access_token: string; user: { id: number; username: string; is_admin: boolean } }>(
        endpoint,
        { username, password }
      );
      login(res.data.access_token, res.data.user);
      router.push("/");
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(detail ?? "请求失败，请稍后重试");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-[70vh] flex items-center justify-center">
      <div className="w-full max-w-sm">
        {/* Logo */}
        <div className="text-center mb-8">
          <span className="text-forge-accent text-2xl font-bold tracking-tight">⬡ EvalForge</span>
          <p className="text-forge-subtext text-xs mt-1">大模型代码评测平台</p>
        </div>

        {/* Card */}
        <div className="bg-forge-surface border border-forge-border rounded-xl p-6 relative">
          <button
            onClick={() => router.back()}
            className="absolute top-4 right-4 text-forge-muted hover:text-forge-text transition-colors"
            title="返回"
          >
            ✕
          </button>
          {/* Tabs */}
          <div className="flex mb-6 border-b border-forge-border">
            {(["login", "register"] as const).map((t) => (
              <button
                key={t}
                onClick={() => { setTab(t); setError(""); }}
                className={`flex-1 pb-2 text-sm font-medium transition-colors ${
                  tab === t
                    ? "text-forge-accent border-b-2 border-forge-accent -mb-px"
                    : "text-forge-subtext hover:text-forge-text"
                }`}
              >
                {t === "login" ? "登录" : "注册"}
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs text-forge-subtext mb-1">用户名</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                minLength={3}
                placeholder="至少 3 个字符"
                className="w-full bg-forge-bg border border-forge-border rounded-lg px-3 py-2 text-sm
                           text-forge-text placeholder-forge-muted focus:outline-none
                           focus:border-forge-accent transition-colors"
              />
            </div>
            <div>
              <label className="block text-xs text-forge-subtext mb-1">密码</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={6}
                placeholder="至少 6 个字符"
                className="w-full bg-forge-bg border border-forge-border rounded-lg px-3 py-2 text-sm
                           text-forge-text placeholder-forge-muted focus:outline-none
                           focus:border-forge-accent transition-colors"
              />
            </div>

            {error && (
              <p className="text-xs text-forge-red bg-forge-red/10 border border-forge-red/30 rounded-lg px-3 py-2">
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-forge-accent text-black font-semibold rounded-lg px-4 py-2.5 text-sm
                         hover:brightness-110 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {loading ? "请稍候…" : tab === "login" ? "登录" : "注册并登录"}
            </button>
          </form>

          {tab === "register" && (
            <p className="text-xs text-forge-muted text-center mt-4">
              首个注册账号自动获得管理员权限
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
