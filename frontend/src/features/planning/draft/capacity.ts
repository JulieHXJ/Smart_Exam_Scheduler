import { eachDayOfInterval, format, getDay, isValid, parseISO } from "date-fns";
import type {
  DateException,
  DraftCapacity,
  ScheduleDraftConfig,
  Weekday,
} from "./types";

const ISO = "yyyy-MM-dd";

/** ISO date -> German display format, e.g. 05.02.2027 */
export function formatDisplayDate(iso: string): string {
  const date = parseISO(iso);
  return isValid(date) ? format(date, "dd.MM.yyyy") : iso;
}

export function formatDisplayDateWithWeekday(iso: string): string {
  const date = parseISO(iso);
  return isValid(date) ? format(date, "dd.MM.yyyy · EEE") : iso;
}

export function toMinutes(time: string): number {
  const [h, m] = time.split(":").map(Number);
  return Number.isFinite(h) && Number.isFinite(m) ? h * 60 + m : NaN;
}

export function toTime(minutes: number): string {
  const clamped = Math.max(0, Math.min(23 * 60 + 59, minutes));
  const h = String(Math.floor(clamped / 60)).padStart(2, "0");
  const m = String(clamped % 60).padStart(2, "0");
  return `${h}:${m}`;
}

export function slotMinutes(start: string, end: string): number | null {
  const diff = toMinutes(end) - toMinutes(start);
  return Number.isFinite(diff) && diff > 0 ? diff : null;
}

/** All ISO dates in the period that fall on an enabled weekday. */
export function getExaminationDates(
  startDate: string,
  endDate: string,
  weekdays: Weekday[],
): string[] {
  const start = parseISO(startDate);
  const end = parseISO(endDate);
  if (!isValid(start) || !isValid(end) || start > end) return [];
  const allowed = new Set<number>(weekdays);
  return eachDayOfInterval({ start, end })
    .filter((day) => allowed.has(getDay(day)))
    .map((day) => format(day, ISO));
}

/** date -> set of unavailable ids (only ids that still exist in the general config). */
function indexExceptions(
  exceptions: DateException[],
  validIds: Set<string>,
): Map<string, Set<string>> {
  const index = new Map<string, Set<string>>();
  for (const exception of exceptions) {
    const set = index.get(exception.date) ?? new Set<string>();
    for (const id of exception.ids) if (validIds.has(id)) set.add(id);
    index.set(exception.date, set);
  }
  return index;
}

/**
 * Potential room-time combinations. Computed per date so a slot exception and a
 * room exception on the same date are never double-counted:
 * (slots - unavailableSlots) x (rooms - unavailableRooms).
 */
export function computeCapacity(config: ScheduleDraftConfig): DraftCapacity {
  const dates = getExaminationDates(
    config.startDate,
    config.endDate,
    config.weekdays,
  );
  const slots = config.timeSlots.length;
  const rooms = config.roomIds.length;
  const slotOff = indexExceptions(
    config.slotExceptions,
    new Set(config.timeSlots.map((slot) => slot.id)),
  );
  const roomOff = indexExceptions(
    config.roomExceptions,
    new Set(config.roomIds),
  );

  let net = 0;
  for (const date of dates) {
    net +=
      (slots - (slotOff.get(date)?.size ?? 0)) *
      (rooms - (roomOff.get(date)?.size ?? 0));
  }
  const gross = dates.length * slots * rooms;
  return {
    days: dates.length,
    slots,
    rooms,
    gross,
    net,
    excluded: gross - net,
  };
}
