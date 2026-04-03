/**
 * 前端鉴权工具
 * - Token 存储在 localStorage
 * - 提供 AuthContext 供全局使用
 */

export interface AuthUser {
  id: number;
  username: string;
  is_admin: boolean;
}

const TOKEN_KEY = "evalforge_token";
const USER_KEY  = "evalforge_user";

export const tokenStore = {
  get: (): string | null => {
    if (typeof window === "undefined") return null;
    return localStorage.getItem(TOKEN_KEY);
  },
  set: (token: string) => localStorage.setItem(TOKEN_KEY, token),
  clear: () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  },
};

export const userStore = {
  get: (): AuthUser | null => {
    if (typeof window === "undefined") return null;
    const raw = localStorage.getItem(USER_KEY);
    return raw ? (JSON.parse(raw) as AuthUser) : null;
  },
  set: (user: AuthUser) => localStorage.setItem(USER_KEY, JSON.stringify(user)),
};
