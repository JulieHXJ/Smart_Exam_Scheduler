import { Check } from "lucide-react";

export function Logo({ compact = false }: { compact?: boolean }) {
  return (
    <div className="flex items-center gap-3">
      <div
        className={`flex shrink-0 items-center justify-center bg-primary text-primary-foreground ${
          compact ? "size-8 rounded-lg" : "size-10 rounded-xl"
        }`}
      >
        <Check className={compact ? "size-4" : "size-5"} strokeWidth={3} />
      </div>
      {!compact && (
        <div className="leading-tight">
          <p className="text-base font-semibold">SmartExam</p>
          <p className="text-xs opacity-60">Faculty of Computer Science</p>
        </div>
      )}
    </div>
  );
}
