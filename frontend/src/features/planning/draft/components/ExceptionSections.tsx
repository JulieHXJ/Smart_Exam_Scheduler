import { CalendarX2, DoorClosed } from "lucide-react";
import type { Room } from "../../types";
import type { ScheduleDraftConfig } from "../types";
import { DraftSection } from "./DraftSection";
import { ExceptionEditor } from "./ExceptionEditor";

type Props = {
  config: ScheduleDraftConfig;
  availableDates: string[];
  onChange: (patch: Partial<ScheduleDraftConfig>) => void;
};

export function SlotExceptionsSection({ config, availableDates, onChange }: Props) {
  const options = config.timeSlots.map((slot, i) => ({
    id: slot.id,
    label: slot.start && slot.end ? `${slot.start}–${slot.end}` : `Slot ${i + 1}`,
  }));
  return (
    <DraftSection
      step="04"
      tone="exception"
      icon={CalendarX2}
      title="Date-Specific Exceptions"
      description="Make individual time slots unavailable without changing your daily defaults."
      badge="Time-slot overrides"
    >
      <ExceptionEditor
        exceptions={config.slotExceptions}
        onChange={(slotExceptions) => onChange({ slotExceptions })}
        options={options}
        availableDates={availableDates}
        addLabel="Add time-slot exception"
        emptyText="No exceptions. General time slots apply to every examination date."
      />
    </DraftSection>
  );
}

export function RoomExceptionsSection({
  config,
  rooms,
  availableDates,
  onChange,
}: Props & { rooms: Room[] }) {
  const options = rooms
    .filter((room) => config.roomIds.includes(room.id))
    .map((room) => ({ id: room.id, label: room.name }));
  return (
    <DraftSection
      step="06"
      tone="exception"
      icon={DoorClosed}
      title="Date-Specific Room Exceptions"
      description="Make selected rooms unavailable on individual examination dates only."
      badge="Room overrides"
    >
      <ExceptionEditor
        exceptions={config.roomExceptions}
        onChange={(roomExceptions) => onChange({ roomExceptions })}
        options={options}
        availableDates={availableDates}
        addLabel="Add room exception"
        emptyText="No exceptions. General rooms apply to every examination date."
      />
    </DraftSection>
  );
}
