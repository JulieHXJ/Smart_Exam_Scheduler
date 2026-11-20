import { rooms } from "../mock-data";
import type { ScheduleDraftConfig, TimeSlot } from "./types";

/** TODO: load from the backend (term settings). Placeholder values. */
export const PERIOD_PRESETS = [
  { label: "Early period", start: "2027-01-25", end: "2027-02-05" },
  { label: "Regular period", start: "2027-02-08", end: "2027-02-19" },
];

export function createSlot(start = "", end = ""): TimeSlot {
  return { id: crypto.randomUUID(), start, end };
}

export function createDefaultConfig(): ScheduleDraftConfig {
  return {
    startDate: PERIOD_PRESETS[0].start,
    endDate: PERIOD_PRESETS[0].end,
    weekdays: [1, 2, 3, 4, 5],
    timeSlots: [
      createSlot("08:00", "10:00"),
      createSlot("10:00", "12:00"),
      createSlot("12:00", "14:00"),
      createSlot("14:00", "16:00"),
    ],
    slotExceptions: [],
    roomIds: rooms.map((room) => room.id),
    roomExceptions: [],
    rules: { maxExamsPerDay: null, minDaysBetweenExams: null, notes: "" },
  };
}
