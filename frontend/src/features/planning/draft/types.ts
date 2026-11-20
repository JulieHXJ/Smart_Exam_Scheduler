/** 0 = Sunday ... 6 = Saturday (same numbering as date-fns `getDay`). */
export type Weekday = 0 | 1 | 2 | 3 | 4 | 5 | 6;

/** Display order is Monday first. */
export const WEEKDAY_OPTIONS: { value: Weekday; label: string }[] = [
  { value: 1, label: "Mon" },
  { value: 2, label: "Tue" },
  { value: 3, label: "Wed" },
  { value: 4, label: "Thu" },
  { value: 5, label: "Fri" },
  { value: 6, label: "Sat" },
  { value: 0, label: "Sun" },
];

/** Times are "HH:mm" strings. */
export type TimeSlot = { id: string; start: string; end: string };

/**
 * One date-specific exception. `ids` are the slot ids (time-slot exceptions)
 * or room ids (room exceptions) that are UNAVAILABLE on `date` (ISO yyyy-MM-dd).
 */
export type DateException = { id: string; date: string; ids: string[] };

export type SchedulingRules = {
  maxExamsPerDay: number | null;
  minDaysBetweenExams: number | null;
  notes: string;
};

export type ScheduleDraftConfig = {
  /** ISO yyyy-MM-dd */
  startDate: string;
  endDate: string;
  weekdays: Weekday[];
  timeSlots: TimeSlot[];
  slotExceptions: DateException[];
  roomIds: string[];
  roomExceptions: DateException[];
  rules: SchedulingRules;
};

export type DraftCapacity = {
  days: number;
  slots: number;
  rooms: number;
  /** days x slots x rooms */
  gross: number;
  excluded: number;
  /** gross - excluded */
  net: number;
};
