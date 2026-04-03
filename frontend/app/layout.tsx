import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";
import { AuthProvider } from "@/context/AuthContext";
import NavUser from "@/components/NavUser";

export const metadata: Metadata = {
  title: "EvalForge — 大模型代码评测平台",
  description: "大规模评测大模型代码生成质量",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN" className="dark">
      <body className="scanlines min-h-screen">
        <AuthProvider>
          {/* Top nav bar */}
          <header className="border-b border-forge-border bg-forge-surface/60 backdrop-blur-sm sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
              <div className="flex items-center gap-5">
                <Link href="/" className="text-forge-accent font-bold text-lg tracking-tight hover:brightness-110">
                  ⬡ EvalForge
                </Link>
                {/* 导航链接 */}
                <nav className="hidden sm:flex items-center gap-1">
                  <Link
                    href="/"
                    className="px-3 py-1.5 rounded-md text-xs text-forge-subtext
                               hover:text-forge-text hover:bg-forge-muted/20 transition-colors"
                  >
                    评测控制台
                  </Link>
                  <Link
                    href="/questions"
                    className="px-3 py-1.5 rounded-md text-xs text-forge-subtext
                               hover:text-forge-text hover:bg-forge-muted/20 transition-colors"
                  >
                    题库管理
                  </Link>
                  <Link
                    href="/compare"
                    className="px-3 py-1.5 rounded-md text-xs text-forge-subtext
                               hover:text-forge-text hover:bg-forge-muted/20 transition-colors"
                  >
                    模型对比
                  </Link>
                </nav>
              </div>
              <div className="flex items-center gap-4 text-xs text-forge-subtext">
                <span className="flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-forge-green animate-pulse-slow" />
                  接口在线
                </span>
                <NavUser />
              </div>
            </div>
          </header>

          <main className="max-w-7xl mx-auto px-6 py-8">{children}</main>

          <footer className="border-t border-forge-border mt-16 py-6 text-center text-xs text-forge-muted">
            EvalForge · Python 3.10+ · FastAPI · SQLite · Next.js · 大模型代码评测平台
          </footer>
        </AuthProvider>
      </body>
    </html>
  );
}
