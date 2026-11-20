import { getExaminationDates, toMinutes } from "./capacity";
import type { ScheduleDraftConfig } from "./types";

/** Returns blocking problems; an empty array means the config can be submitted. */
export function validateConfig(config: ScheduleDraftConfig): string[] {
  const errors: string[] = [];

  if (!config.startDate || !config.endDate) {
    errors.push("Choose a start and end date.");
  } else if (config.startDate > config.endDate) {
    errors.push("The end date must be after the start date.");
  } else if (
    getExaminationDates(config.startDate, config.endDate, config.weekdays)
      .length === 0
  ) {
    errors.push("No examination dates in the selected period and weekdays.");
  }

  if (config.timeSlots.length === 0) {
    errors.push("Add at least one time slot.");
  } else {
    const ranges = config.timeSlots.map((slot) => ({
      start: toMinutes(slot.start),
      end: toMinutes(slot.end),
    }));
    if (ranges.some((r) => !(r.end > r.start))) {
      errors.push("Every time slot needs an end time after its start time.");
    } else {
      const sorted = [...ranges].sort((a, b) => a.start - b.start);
      if (sorted.some((r, i) => i > 0 && r.start < sorted[i - 1].end)) {
        errors.push("Time slots must not overlap.");
      }
    }
  }

  if (config.roomIds.length === 0) errors.push("Select at least one room.");
  return errors;
}
