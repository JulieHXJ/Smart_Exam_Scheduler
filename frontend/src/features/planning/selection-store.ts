import { create } from "zustand";
import { exams } from "./mock-data";

type SelectionStore = {
  selected: Set<string>;
  toggle: (id: string) => void;
  setMany: (ids: string[], on: boolean) => void;
  clear: () => void;
};

export const useSelection = create<SelectionStore>((set) => ({
  selected: new Set(
    exams.filter((exam) => exam.status === "selected").map((exam) => exam.id),
  ),
  toggle: (id) =>
    set((state) => {
      const selected = new Set(state.selected);
      if (selected.has(id)) selected.delete(id);
      else selected.add(id);
      return { selected };
    }),
  setMany: (ids, on) =>
    set((state) => {
      const selected = new Set(state.selected);
      for (const id of ids) {
        if (on) selected.add(id);
        else selected.delete(id);
      }
      return { selected };
    }),
  clear: () => set({ selected: new Set() }),
}));
