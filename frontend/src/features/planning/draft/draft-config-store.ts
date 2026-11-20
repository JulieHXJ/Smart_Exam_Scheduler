import { create } from "zustand";
import type { ScheduleDraftConfig } from "./types";

type DraftConfigStore = {
  /** Last submitted configuration, reused when the dialog is opened again. */
  lastConfig: ScheduleDraftConfig | null;
  save: (config: ScheduleDraftConfig) => void;
};

export const useDraftConfig = create<DraftConfigStore>((set) => ({
  lastConfig: null,
  save: (config) => set({ lastConfig: config }),
}));
