import { useState, type ReactNode } from "react";
import { ChevronDown, type LucideIcon } from "lucide-react";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";

type Tone = "default" | "exception" | "capacity";

const TONE: Record<Tone, { card: string; icon: string; badge: string }> = {
  default: {
    card: "bg-card",
    icon: "bg-muted text-muted-foreground",
    badge: "bg-muted text-muted-foreground",
  },
  exception: {
    card: "bg-violet-50/60 dark:bg-violet-500/5",
    icon: "bg-violet-100 text-violet-600 dark:bg-violet-500/20 dark:text-violet-300",
    badge: "bg-violet-100 text-violet-700 dark:bg-violet-500/20 dark:text-violet-300",
  },
  capacity: {
    card: "bg-emerald-50/70 dark:bg-emerald-500/5",
    icon: "bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-300",
    badge: "bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-300",
  },
};

type Props = {
  step: string;
  title: string;
  description: string;
  icon: LucideIcon;
  badge?: string;
  tone?: Tone;
  collapsible?: boolean;
  defaultOpen?: boolean;
  children: ReactNode;
};

export function DraftSection({
  step,
  title,
  description,
  icon: Icon,
  badge,
  tone = "default",
  collapsible = false,
  defaultOpen = true,
  children,
}: Props) {
  const [open, setOpen] = useState(defaultOpen);
  const t = TONE[tone];

  const heading = (
    <div className="flex w-full items-start gap-4">
      <span className={`flex size-10 shrink-0 items-center justify-center rounded-xl ${t.icon}`}>
        <Icon className="size-5" />
      </span>
      <div className="min-w-0 flex-1 text-left">
        <p className="text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">
          Section {step}
        </p>
        <h3 className="text-base font-semibold">{title}</h3>
        <p className="text-xs text-muted-foreground">{description}</p>
      </div>
      {badge && (
        <span className={`rounded-md px-2 py-1 text-[10px] font-semibold uppercase tracking-wide ${t.badge}`}>
          {badge}
        </span>
      )}
      {collapsible && (
        <ChevronDown className={`mt-2 size-4 shrink-0 transition-transform ${open ? "rotate-180" : ""}`} />
      )}
    </div>
  );

  return (
    <section className={`rounded-xl border p-6 ${t.card}`}>
      {collapsible ? (
        <Collapsible open={open} onOpenChange={setOpen}>
          <CollapsibleTrigger asChild>
            <button type="button" className="w-full">
              {heading}
            </button>
          </CollapsibleTrigger>
          <CollapsibleContent className="mt-5">{children}</CollapsibleContent>
        </Collapsible>
      ) : (
        <>
          {heading}
          <div className="mt-5">{children}</div>
        </>
      )}
    </section>
  );
}
