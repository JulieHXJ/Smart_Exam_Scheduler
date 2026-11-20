import { ArrowRight, Check, CalendarRange, CalendarDays } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { PERIOD_PRESETS } from "../defaults";
import { WEEKDAY_OPTIONS, type ScheduleDraftConfig, type Weekday } from "../types";
import { DraftSection } from "./DraftSection";

type Props = {
  config: ScheduleDraftConfig;
  dateCount: number;
  onChange: (patch: Partial<ScheduleDraftConfig>) => void;
};

export function PeriodSection({ config, dateCount, onChange }: Props) {
  return (
    <DraftSection
      step="01"
      icon={CalendarRange}
      title="Examination Period"
      description="Define the date range for this draft."
    >
      <div className="flex items-end gap-3">
        <div className="flex-1 space-y-2">
          <Label htmlFor="draft-start">Start date</Label>
          <Input
            id="draft-start"
            type="date"
            lang="de-DE"
            value={config.startDate}
            onChange={(e) => onChange({ startDate: e.target.value })}
          />
        </div>
        <ArrowRight className="mb-2 size-4 text-muted-foreground" />
        <div className="flex-1 space-y-2">
          <Label htmlFor="draft-end">End date</Label>
          <Input
            id="draft-end"
            type="date"
            lang="de-DE"
            min={config.startDate}
            value={config.endDate}
            onChange={(e) => onChange({ endDate: e.target.value })}
          />
        </div>
      </div>
      <div className="mt-3 flex flex-wrap items-center gap-3 text-xs">
        <span className="text-muted-foreground">Quick select</span>
        {PERIOD_PRESETS.map((preset) => (
          <button
            key={preset.label}
            type="button"
            className="font-medium text-primary hover:underline"
            onClick={() => onChange({ startDate: preset.start, endDate: preset.end })}
          >
            {preset.label}
          </button>
        ))}
      </div>
    </DraftSection>
  );
}

export function WeekdaysSection({ config, dateCount, onChange }: Props) {
  const toggle = (day: Weekday) =>
    onChange({
      weekdays: config.weekdays.includes(day)
        ? config.weekdays.filter((d) => d !== day)
        : [...config.weekdays, day],
    });

  return (
    <DraftSection
      step="02"
      icon={CalendarDays}
      title="Available Examination Days"
      description="Only enabled weekdays will be included."
    >
      <div className="grid grid-cols-7 gap-2">
        {WEEKDAY_OPTIONS.map(({ value, label }) => {
          const on = config.weekdays.includes(value);
          return (
            <button
              key={value}
              type="button"
              aria-pressed={on}
              onClick={() => toggle(value)}
              className={`flex flex-col items-center gap-2 rounded-lg border py-3 text-xs font-medium transition-colors ${
                on
                  ? "border-primary/40 bg-primary/5 text-primary"
                  : "text-muted-foreground hover:bg-muted"
              }`}
            >
              {label}
              <span
                className={`flex size-4 items-center justify-center rounded-[4px] border ${
                  on ? "border-primary bg-primary text-primary-foreground" : "border-input"
                }`}
              >
                {on && <Check className="size-3" />}
              </span>
            </button>
          );
        })}
      </div>
      <p className="mt-3 text-xs text-muted-foreground">
        {dateCount} examination {dateCount === 1 ? "date" : "dates"} in your selected period
      </p>
    </DraftSection>
  );
}
