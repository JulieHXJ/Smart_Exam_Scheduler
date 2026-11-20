import { useState } from "react";
import { DoorOpen, Monitor, Search } from "lucide-react";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import type { Room } from "../../types";
import type { ScheduleDraftConfig } from "../types";
import { DraftSection } from "./DraftSection";

type Props = {
  config: ScheduleDraftConfig;
  rooms: Room[];
  onChange: (patch: Partial<ScheduleDraftConfig>) => void;
};

export function RoomsSection({ config, rooms, onChange }: Props) {
  const [query, setQuery] = useState("");
  const q = query.trim().toLowerCase();
  const visible = rooms.filter(
    (room) =>
      !q ||
      room.name.toLowerCase().includes(q) ||
      room.type.includes(q) ||
      room.building.toLowerCase().includes(q),
  );
  const selected = new Set(config.roomIds);

  const setRooms = (ids: string[]) =>
    onChange({
      roomIds: ids,
      // forget room exceptions for rooms that are no longer selected
      roomExceptions: config.roomExceptions.map((e) => ({
        ...e,
        ids: e.ids.filter((id) => ids.includes(id)),
      })),
    });

  const toggle = (id: string, on: boolean) =>
    setRooms(on ? [...config.roomIds, id] : config.roomIds.filter((r) => r !== id));

  const visibleIds = visible.map((room) => room.id);
  const hasCombined = rooms.some((room) => room.name.includes("+"));

  return (
    <DraftSection
      step="05"
      icon={DoorOpen}
      title="General Available Examination Rooms"
      description="Select the rooms available throughout the examination period."
      badge={`${selected.size} of ${rooms.length} selected`}
    >
      <div className="flex items-center gap-3">
        <div className="relative w-full max-w-sm">
          <Search className="pointer-events-none absolute left-2.5 top-2 size-4 text-muted-foreground" />
          <Input
            className="pl-8"
            placeholder="Search rooms or room type…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
        <div className="ml-auto flex gap-4 text-xs font-medium text-primary">
          <button
            type="button"
            onClick={() => setRooms([...new Set([...config.roomIds, ...visibleIds])])}
          >
            Select all
          </button>
          <button
            type="button"
            className="text-muted-foreground"
            onClick={() => setRooms(config.roomIds.filter((id) => !visibleIds.includes(id)))}
          >
            Clear selection
          </button>
        </div>
      </div>

      <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
        {visible.map((room) => {
          const on = selected.has(room.id);
          const Icon = room.type === "lab" ? Monitor : DoorOpen;
          return (
            <label
              key={room.id}
              className={`flex cursor-pointer items-center gap-3 rounded-lg border p-3 transition-colors ${
                on ? "border-primary/40 bg-primary/5" : "hover:bg-muted"
              }`}
            >
              <span className="flex size-8 items-center justify-center rounded-md bg-muted text-muted-foreground">
                <Icon className="size-4" />
              </span>
              <span className="min-w-0 flex-1">
                <span className="block truncate text-sm font-semibold">{room.name}</span>
                <span className="block truncate text-[11px] text-muted-foreground">
                  {room.capacity} seats · {room.type === "lab" ? "Computer lab" : "Classroom"}
                </span>
              </span>
              <Checkbox checked={on} onCheckedChange={(v) => toggle(room.id, v === true)} />
            </label>
          );
        })}
      </div>
      {visible.length === 0 && (
        <p className="mt-4 text-xs text-muted-foreground">No rooms match your search.</p>
      )}
      {hasCombined && (
        <p className="mt-3 text-xs text-muted-foreground">
          Combined labs (e.g. Lab 1 + 2) share physical rooms with their single labs; the draft
          avoids double-booking these spaces.
        </p>
      )}
    </DraftSection>
  );
}
