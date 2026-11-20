import { Info, Sigma } from "lucide-react";
import type { DraftCapacity } from "../types";
import { DraftSection } from "./DraftSection";

const n = (value: number) => value.toLocaleString("de-DE");

function Figure({ value, label }: { value: number; label: string }) {
  return (
    <div className="text-center">
      <p className="text-3xl font-semibold tabular-nums text-emerald-700 dark:text-emerald-300">
        {n(value)}
      </p>
      <p className="text-[11px] text-muted-foreground">{label}</p>
    </div>
  );
}

const Op = ({ children }: { children: string }) => (
  <span className="text-lg text-muted-foreground">{children}</span>
);

export function CapacitySection({ capacity }: { capacity: DraftCapacity }) {
  return (
    <DraftSection
      step="08"
      tone="capacity"
      icon={Sigma}
      title="Scheduling Capacity Overview"
      description="Your available room-time combinations, updated as you configure."
      badge="Live"
    >
      <div className="flex flex-wrap items-center justify-between gap-4 px-2">
        <Figure value={capacity.days} label="examination days" />
        <Op>×</Op>
        <Figure value={capacity.slots} label="daily time slots" />
        <Op>×</Op>
        <Figure value={capacity.rooms} label="selected rooms" />
        <Op>=</Op>
        <Figure value={capacity.gross} label="before exceptions" />
        <Op>−</Op>
        <Figure value={capacity.excluded} label="excluded by exceptions" />
      </div>
      <div className="mt-5 flex items-center justify-between rounded-lg bg-emerald-100/70 px-5 py-4 dark:bg-emerald-500/10">
        <p>
          <span className="text-3xl font-semibold tabular-nums text-emerald-700 dark:text-emerald-300">
            {n(capacity.net)}
          </span>
          <span className="ml-3 text-sm">potential room-time combinations</span>
        </p>
        <span className="text-xs text-muted-foreground">After all date-specific exceptions</span>
      </div>
      <p className="mt-3 flex items-start gap-2 text-xs text-muted-foreground">
        <Info className="mt-0.5 size-3.5 shrink-0" />
        This is potential availability, not the number of exams that can be scheduled. Exam
        duration, room capacity, shared labs, examiner availability and scheduling rules can
        reduce actual capacity.
      </p>
    </DraftSection>
  );
}
