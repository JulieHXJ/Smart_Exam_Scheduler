import { Clock, Plus, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { slotMinutes, toMinutes, toTime } from "../capacity";
import { createSlot } from "../defaults";
import type { ScheduleDraftConfig, TimeSlot } from "../types";
import { DraftSection } from "./DraftSection";

type Props = {
  config: ScheduleDraftConfig;
  onChange: (patch: Partial<ScheduleDraftConfig>) => void;
};

export function TimeSlotsSection({ config, onChange }: Props) {
  const { timeSlots } = config;

  const patchSlot = (id: string, patch: Partial<TimeSlot>) =>
    onChange({
      timeSlots: timeSlots.map((slot) => (slot.id === id ? { ...slot, ...patch } : slot)),
    });

  const removeSlot = (id: string) =>
    onChange({
      timeSlots: timeSlots.filter((slot) => slot.id !== id),
      // keep exceptions consistent: forget the removed slot
      slotExceptions: config.slotExceptions.map((e) => ({
        ...e,
        ids: e.ids.filter((slotId) => slotId !== id),
      })),
    });

  const addSlot = () => {
    const last = timeSlots[timeSlots.length - 1];
    const start = last && Number.isFinite(toMinutes(last.end)) ? last.end : "08:00";
    onChange({ timeSlots: [...timeSlots, createSlot(start, toTime(toMinutes(start) + 120))] });
  };

  return (
    <DraftSection
      step="03"
      icon={Clock}
      title="General Daily Examination Time Slots"
      description="These default time slots apply to every selected examination date."
      badge="General availability"
    >
      <div className="overflow-hidden rounded-lg border bg-card">
        <Table>
          <TableHeader>
            <TableRow className="text-[11px] uppercase tracking-wide">
              <TableHead className="pl-4">Time slot</TableHead>
              <TableHead>Start time</TableHead>
              <TableHead>End time</TableHead>
              <TableHead>Duration</TableHead>
              <TableHead className="w-12" />
            </TableRow>
          </TableHeader>
          <TableBody>
            {timeSlots.map((slot, index) => {
              const minutes = slotMinutes(slot.start, slot.end);
              return (
                <TableRow key={slot.id}>
                  <TableCell className="pl-4 text-sm">
                    <span className="mr-2 rounded bg-muted px-1.5 py-0.5 font-mono text-[11px]">
                      {String(index + 1).padStart(2, "0")}
                    </span>
                    Daily slot {index + 1}
                  </TableCell>
                  <TableCell>
                    <Input
                      type="time"
                      className="w-40"
                      value={slot.start}
                      aria-invalid={minutes === null}
                      aria-label={`Slot ${index + 1} start`}
                      onChange={(e) => patchSlot(slot.id, { start: e.target.value })}
                    />
                  </TableCell>
                  <TableCell>
                    <Input
                      type="time"
                      className="w-40"
                      value={slot.end}
                      aria-invalid={minutes === null}
                      aria-label={`Slot ${index + 1} end`}
                      onChange={(e) => patchSlot(slot.id, { end: e.target.value })}
                    />
                  </TableCell>
                  <TableCell className="text-xs text-muted-foreground">
                    {minutes === null ? "Invalid" : `${minutes} min`}
                  </TableCell>
                  <TableCell>
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon-sm"
                      aria-label={`Remove slot ${index + 1}`}
                      onClick={() => removeSlot(slot.id)}
                    >
                      <X />
                    </Button>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>
      <Button type="button" variant="ghost" size="sm" className="mt-3 text-primary" onClick={addSlot}>
        <Plus /> Add time slot
      </Button>
    </DraftSection>
  );
}
