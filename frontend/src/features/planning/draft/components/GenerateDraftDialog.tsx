import { useMemo, useState } from "react";
import { ArrowRight, FileText, Info, Lock, SlidersHorizontal, Wand2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogTitle,
} from "@/components/ui/dialog";
import { rooms } from "../../mock-data"; // TODO: replace with rooms from the backend
import { computeCapacity, getExaminationDates } from "../capacity";
import { createDefaultConfig } from "../defaults";
import { useDraftConfig } from "../draft-config-store";
import { generateDraft } from "../generate-draft";
import { toApiPayload } from "../payload";
import type { ScheduleDraftConfig } from "../types";
import { validateConfig } from "../validation";
import { CapacitySection } from "./CapacitySection";
import { RoomExceptionsSection, SlotExceptionsSection } from "./ExceptionSections";
import { PeriodSection, WeekdaysSection } from "./PeriodAndDaysSections";
import { RoomsSection } from "./RoomsSection";
import { RulesSection } from "./RulesSection";
import { TimeSlotsSection } from "./TimeSlotsSection";

type Props = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  examIds: string[];
};

export function GenerateDraftDialog({ open, onOpenChange, examIds }: Props) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        className="flex! max-h-[92vh] w-[92vw]! max-w-[1400px]! flex-col gap-0! overflow-hidden p-0! sm:max-w-[1400px]!"
      >
        {/* Mounted only while open, so local state resets (or reloads the last config) each time. */}
        <DraftForm examIds={examIds} onClose={() => onOpenChange(false)} />
      </DialogContent>
    </Dialog>
  );
}

function DraftForm({ examIds, onClose }: { examIds: string[]; onClose: () => void }) {
  const [config, setConfig] = useState<ScheduleDraftConfig>(
    () => useDraftConfig.getState().lastConfig ?? createDefaultConfig(),
  );
  const [submitting, setSubmitting] = useState(false);

  const update = (patch: Partial<ScheduleDraftConfig>) =>
    setConfig((current) => ({ ...current, ...patch }));

  const availableDates = useMemo(
    () => getExaminationDates(config.startDate, config.endDate, config.weekdays),
    [config.startDate, config.endDate, config.weekdays],
  );
  const capacity = useMemo(() => computeCapacity(config), [config]);
  const errors = useMemo(() => validateConfig(config), [config]);

  async function handleGenerate() {
    setSubmitting(true);
    try {
      useDraftConfig.getState().save(config);
      await generateDraft(toApiPayload(config, examIds));
      onClose();
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <>
      <header className="flex items-start gap-4 border-b px-8 py-6">
        <span className="flex size-11 items-center justify-center rounded-xl bg-primary/10 text-primary">
          <SlidersHorizontal className="size-5" />
        </span>
        <div className="flex-1">
          <p className="text-[11px] font-semibold uppercase tracking-widest text-primary">
            Winter semester 2026/27 · Draft setup
          </p>
          <DialogTitle className="text-2xl font-medium">Configure your exam schedule</DialogTitle>
          <DialogDescription>
            Set your defaults once. Make exceptions only where you need them.
          </DialogDescription>
        </div>
        <span className="mr-10 mt-2 inline-flex items-center gap-1.5 text-xs text-muted-foreground">
          <FileText className="size-3.5" />
          {examIds.length} exams selected
        </span>
      </header>

      <div className="min-h-0 flex-1 space-y-5 overflow-y-auto bg-muted/30 px-8 py-6">
        <p className="flex items-center gap-2 rounded-lg border bg-violet-50 px-4 py-3 text-xs text-muted-foreground dark:bg-violet-500/10">
          <Info className="size-4 shrink-0" />
          General availability applies to all selected examination dates. Date-specific exceptions
          only remove availability for that date.
        </p>
        <div className="grid gap-5 lg:grid-cols-2">
          <PeriodSection config={config} dateCount={availableDates.length} onChange={update} />
          <WeekdaysSection config={config} dateCount={availableDates.length} onChange={update} />
        </div>
        <TimeSlotsSection config={config} onChange={update} />
        <SlotExceptionsSection config={config} availableDates={availableDates} onChange={update} />
        <RoomsSection config={config} rooms={rooms} onChange={update} />
        <RoomExceptionsSection
          config={config}
          rooms={rooms}
          availableDates={availableDates}
          onChange={update}
        />
        <RulesSection config={config} onChange={update} />
        <CapacitySection capacity={capacity} />
      </div>

      <footer className="flex items-center gap-4 border-t px-8 py-4">
        {errors.length > 0 ? (
          <p className="text-xs text-amber-600 dark:text-amber-400">
            {errors[0]}
            {errors.length > 1 && ` (+${errors.length - 1} more)`}
          </p>
        ) : (
          <p className="flex items-center gap-2 text-xs text-muted-foreground">
            <Lock className="size-3.5" /> A draft only. Nothing will be published.
          </p>
        )}
        <div className="ml-auto flex gap-3">
          <Button type="button" variant="outline" size="lg" onClick={onClose}>
            Cancel
          </Button>
          <Button
            type="button"
            size="lg"
            disabled={errors.length > 0 || submitting}
            onClick={handleGenerate}
          >
            <Wand2 /> Generate Draft <ArrowRight />
          </Button>
        </div>
      </footer>
    </>
  );
}
