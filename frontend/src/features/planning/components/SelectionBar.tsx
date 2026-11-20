import { useState } from "react";
import { Wand2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useSelection } from "../selection-store";
import { GenerateDraftDialog } from "../draft/components/GenerateDraftDialog";

type Props = { visibleIds: string[] };

export function SelectionBar({ visibleIds }: Props) {
  const [dialogOpen, setDialogOpen] = useState(false);
  const selected = useSelection((state) => state.selected);
  const setMany = useSelection((state) => state.setMany);
  const clear = useSelection((state) => state.clear);
  const count = selected.size;
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
      <Button className="ml-auto gap-2" onClick={() => setDialogOpen(true)}>
        <Wand2 className="size-4" />
        Generate schedule draft
      </Button>
      <GenerateDraftDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        examIds={[...selected]}
      />
    </div>
  );
}
