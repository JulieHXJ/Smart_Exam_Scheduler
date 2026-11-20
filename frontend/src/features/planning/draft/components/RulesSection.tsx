import { SlidersHorizontal } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { ScheduleDraftConfig, SchedulingRules } from "../types";
import { DraftSection } from "./DraftSection";

type Props = {
  config: ScheduleDraftConfig;
  onChange: (patch: Partial<ScheduleDraftConfig>) => void;
};

const toNumber = (value: string) => (value === "" ? null : Math.max(1, Number(value)));

export function RulesSection({ config, onChange }: Props) {
  const rules = config.rules;
  const set = (patch: Partial<SchedulingRules>) => onChange({ rules: { ...rules, ...patch } });

  return (
    <DraftSection
      step="07"
      icon={SlidersHorizontal}
      title="Additional Scheduling Rules"
      description="Fine-tune daily limits, exam spacing, and review notes."
      badge="Optional"
      collapsible
      defaultOpen={false}
    >
      <div className="grid gap-4 md:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="rule-max">Max. exams per day</Label>
          <Input
            id="rule-max"
            type="number"
            min={1}
            placeholder="No limit"
            value={rules.maxExamsPerDay ?? ""}
            onChange={(e) => set({ maxExamsPerDay: toNumber(e.target.value) })}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="rule-gap">Min. days between exams (same program and semester)</Label>
          <Input
            id="rule-gap"
            type="number"
            min={1}
            placeholder="No minimum"
            value={rules.minDaysBetweenExams ?? ""}
            onChange={(e) => set({ minDaysBetweenExams: toNumber(e.target.value) })}
          />
        </div>
        <div className="space-y-2 md:col-span-2">
          <Label htmlFor="rule-notes">Notes for the review</Label>
          <textarea
            id="rule-notes"
            rows={3}
            value={rules.notes}
            onChange={(e) => set({ notes: e.target.value })}
            className="w-full rounded-lg border border-input bg-transparent px-2.5 py-2 text-sm outline-none placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 dark:bg-input/30"
            placeholder="Special requirements, restrictions on specific exams…"
          />
        </div>
      </div>
    </DraftSection>
  );
}
