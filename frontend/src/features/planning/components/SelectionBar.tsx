import { Wand2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useSelection } from "../selection-store";

type Props = { visibleIds: string[] };

export function SelectionBar({ visibleIds }: Props) {
  const count = useSelection((state) => state.selected.size);
  const setMany = useSelection((state) => state.setMany);
  const clear = useSelection((state) => state.clear);
  if (count === 0) return null;

  return (
    <div className="sticky bottom-6 z-10 mt-6 flex items-center gap-4 rounded-xl bg-zinc-900 px-5 py-3 text-white shadow-lg">
      <span className="text-sm font-semibold">{count} exams selected</span>
      <button
        type="button"
        onClick={() => setMany(visibleIds, true)}
        className="text-xs text-white/70 hover:text-white"
      >
        Select all in filter
      </button>
      <button
        type="button"
        onClick={clear}
        className="text-xs text-white/70 hover:text-white"
      >
        Clear
      </button>
      <Button
        disabled
        title="Available once schedule generation is connected"
        className="ml-auto gap-2"
      >
        <Wand2 className="size-4" />
        Generate schedule draft
      </Button>
    </div>
  );
}
