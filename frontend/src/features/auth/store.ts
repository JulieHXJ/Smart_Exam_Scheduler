import { create } from "zustand";
import { fetchMe, logout, type User } from "./api";

type Status = "loading" | "authenticated" | "anonymous";

type AuthStore = {
  user: User | null;
  status: Status;
  load: () => Promise<void>;
  signOut: () => Promise<void>;
};

export const useAuth = create<AuthStore>((set) => ({
  user: null,
  status: "loading",
  load: async () => {
    try {
      set({ user: await fetchMe(), status: "authenticated" });
    } catch {
      set({ user: null, status: "anonymous" });
    }
  },
  signOut: async () => {
    try {
      await logout();
    } finally {
      set({ user: null, status: "anonymous" });
    }
  },
}));
