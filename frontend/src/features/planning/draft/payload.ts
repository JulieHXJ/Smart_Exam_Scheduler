import type { ScheduleDraftConfig } from "./types";

/**
 * Shape sent to the backend. Dates are ISO yyyy-MM-dd, times "HH:mm".
 * Slot exceptions reference slots by start/end (client slot ids are not stable).
 */
export type GenerateDraftRequest = {
  examIds: string[];
  period: { start: string; end: string };
  weekdays: number[];
  timeSlots: { start: string; end: string }[];
  slotExceptions: {
    date: string;
    unavailable: { start: string; end: string }[];
  }[];
  roomIds: string[];
  roomExceptions: { date: string; unavailableRoomIds: string[] }[];
  rules: {
    maxExamsPerDay: number | null;
    minDaysBetweenExams: number | null;
    notes: string;
  };
};

export function toApiPayload(
  config: ScheduleDraftConfig,
  examIds: string[],
): GenerateDraftRequest {
  const slotById = new Map(config.timeSlots.map((slot) => [slot.id, slot]));
  const roomIds = new Set(config.roomIds);
  return {
    examIds,
    period: { start: config.startDate, end: config.endDate },
    weekdays: config.weekdays,
    timeSlots: config.timeSlots.map(({ start, end }) => ({ start, end })),
    slotExceptions: config.slotExceptions
      .map((e) => ({
        date: e.date,
        unavailable: e.ids.flatMap((id) => {
          const slot = slotById.get(id);
          return slot ? [{ start: slot.start, end: slot.end }] : [];
        }),
      }))
      .filter((e) => e.unavailable.length > 0),
    roomIds: config.roomIds,
    roomExceptions: config.roomExceptions
      .map((e) => ({
        date: e.date,
        unavailableRoomIds: e.ids.filter((id) => roomIds.has(id)),
      }))
      .filter((e) => e.unavailableRoomIds.length > 0),
    rules: config.rules,
  };
}
