import type { ProgramCode } from "../types";

const COLOR: Partial<Record<ProgramCode, string>> = {
  IN: "bg-blue-100 text-blue-700 dark:bg-blue-500/20 dark:text-blue-300",
  TI: "bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-300",
  WI: "bg-orange-100 text-orange-700 dark:bg-orange-500/20 dark:text-orange-300",
  IIS: "bg-violet-100 text-violet-700 dark:bg-violet-500/20 dark:text-violet-300",
  KIR: "bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-300",
};

const FALLBACK =
  "bg-rose-100 text-rose-700 dark:bg-rose-500/20 dark:text-rose-300";

export function ProgramBadge({ program }: { program: ProgramCode }) {
  return (
    <span
      className={`rounded px-2 py-0.5 text-[11px] font-semibold ${COLOR[program] ?? FALLBACK}`}
    >
      {program}
    </span>
  );
}
