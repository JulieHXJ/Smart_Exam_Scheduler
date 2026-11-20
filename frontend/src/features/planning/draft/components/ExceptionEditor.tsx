import { Plus, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { formatDisplayDateWithWeekday } from "../capacity";
import type { DateException } from "../types";

export type ExceptionOption = { id: string; label: string };

type Props = {
  exceptions: DateException[];
  onChange: (exceptions: DateException[]) => void;
  /** Items that can be marked unavailable (slots or rooms). */
  options: ExceptionOption[];
  /** Valid examination dates (ISO) in the current period. */
  availableDates: string[];
  addLabel: string;
  emptyText: string;
};

export function ExceptionEditor({
  exceptions,
  onChange,
  options,
  availableDates,
  addLabel,
  emptyText,
}: Props) {
  const usedDates = new Set(exceptions.map((e) => e.date));
  const freeDates = availableDates.filter((d) => !usedDates.has(d));

  const patch = (id: string, p: Partial<DateException>) =>
    onChange(exceptions.map((e) => (e.id === id ? { ...e, ...p } : e)));

  const toggle = (exception: DateException, optionId: string) =>
    patch(exception.id, {
      ids: exception.ids.includes(optionId)
        ? exception.ids.filter((id) => id !== optionId)
        : [...exception.ids, optionId],
    });

  const add = () => {
    if (freeDates.length === 0) return;
    onChange([...exceptions, { id: crypto.randomUUID(), date: freeDates[0], ids: [] }]);
  };

  return (
    <div className="space-y-3">
      {exceptions.length === 0 ? (
        <div className="rounded-lg border border-dashed px-4 py-3 text-xs text-muted-foreground">
          {emptyText}
        </div>
      ) : (
        exceptions.map((exception) => {
          const dateOptions = [...new Set([exception.date, ...freeDates])].sort();
          const outside = !availableDates.includes(exception.date);
          const allOff = options.length > 0 && options.every((o) => exception.ids.includes(o.id));
          return (
            <div key={exception.id} className="rounded-lg border border-violet-200 bg-card p-4 dark:border-violet-500/30">
              <div className="flex flex-wrap items-center gap-3">
                <select
                  aria-label="Exception date"
                  value={exception.date}
                  onChange={(e) => patch(exception.id, { date: e.target.value })}
                  className="h-8 rounded-lg border border-input bg-transparent px-2.5 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 dark:bg-input/30"
                >
                  {dateOptions.map((date) => (
                    <option key={date} value={date}>
                      {formatDisplayDateWithWeekday(date)}
                      {!availableDates.includes(date) ? " (outside period)" : ""}
                    </option>
                  ))}
                </select>
                <span className="text-xs text-muted-foreground">
                  {exception.ids.length} unavailable
                </span>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="ml-auto text-muted-foreground"
                  onClick={() => onChange(exceptions.filter((e) => e.id !== exception.id))}
                >
                  <Trash2 /> Remove
                </Button>
              </div>

              <div className="mt-3 flex flex-wrap gap-2">
                {options.map((option) => {
                  const off = exception.ids.includes(option.id);
                  return (
                    <button
                      key={option.id}
                      type="button"
                      aria-pressed={off}
                      onClick={() => toggle(exception, option.id)}
                      className={`rounded-md border px-2.5 py-1 text-xs font-medium transition-colors ${
                        off
                          ? "border-destructive/40 bg-destructive/10 text-destructive line-through"
                          : "hover:bg-muted"
                      }`}
                    >
                      {option.label}
                    </button>
                  );
                })}
              </div>
              {outside && (
                <p className="mt-2 text-xs text-amber-600 dark:text-amber-400">
                  This date is outside the examination period and will be ignored.
                </p>
              )}
              {allOff && (
                <p className="mt-2 text-xs text-amber-600 dark:text-amber-400">
                  Everything is unavailable on this date.
                </p>
              )}
            </div>
          );
        })
      )}
      <Button
        type="button"
        variant="ghost"
        size="sm"
        className="text-primary"
        disabled={freeDates.length === 0}
        onClick={add}
      >
        <Plus /> {addLabel}
      </Button>
    </div>
  );
}
