import { api } from "@/lib/api";

export type User = { email: string; role: "admin" | "tester" };

export const requestCode = (email: string) =>
  api<{ message: string }>("/auth/request-code", {
    method: "POST",
    body: JSON.stringify({ email }),
  });

export const verifyCode = (email: string, code: string) =>
  api<{ message: string }>("/auth/verify-code", {
    method: "POST",
    body: JSON.stringify({ email, code }),
  });

export const fetchMe = () => api<User>("/auth/me");

export const logout = () =>
  api<{ message: string }>("/auth/logout", { method: "POST" });
