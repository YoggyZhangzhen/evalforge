"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";

export default function NavUser() {
  const { user, logout, loading } = useAuth();
  const router = useRouter();

  if (loading) return <span className="text-forge-muted">…</span>;

  if (!user) {
    return (
      <Link
        href="/login"
        className="px-3 py-1 rounded-md border border-forge-border text-xs
                   text-forge-subtext hover:text-forge-text hover:border-forge-accent transition-colors"
      >
        登录
      </Link>
    );
  }

  return (
    <div className="flex items-center gap-3">
      <span className="text-forge-text font-medium">
        {user.is_admin && (
          <span className="text-forge-accent mr-1 text-[10px]">[管理员]</span>
        )}
        {user.username}
      </span>
      <button
        onClick={() => { logout(); router.push("/login"); }}
        className="px-3 py-1 rounded-md border border-forge-border text-xs
                   text-forge-subtext hover:text-forge-red hover:border-forge-red transition-colors"
      >
        退出
      </button>
    </div>
  );
}
