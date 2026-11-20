import { useState, type ReactNode } from "react";
import { ChevronDown, Link2, Lock, Users } from "lucide-react";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useSelection } from "../selection-store";
import {
  EXAM_TYPE_LABEL,
  type Exam,
  type ExamFlag,
} from "../types";
import { ProgramBadge } from "./ProgramBadge";

const FLAG_ICON: Record<ExamFlag, { label: string; node: ReactNode }> = {
  locked: {
    label: "Fixed date or room",
    node: <Lock className="size-3.5" />,
  },
  digital: { label: "Digital exam", node: "D" },
  repeater: { label: "Repeater exam", node: "R" },
  mapped: {
    label: "Mapped across programs",
    node: <Link2 className="size-3.5" />,
  },
};

function Flags({ flags }: { flags: ExamFlag[] }) {
  return (
    <div className="flex gap-1.5">
      {flags.map((flag) => (
        <span
          key={flag}
          title={FLAG_ICON[flag].label}
          aria-label={FLAG_ICON[flag].label}
          className="flex size-7 items-center justify-center rounded-md bg-muted text-[11px] font-semibold text-muted-foreground"
        >
          {FLAG_ICON[flag].node}
        </span>
      ))}
    </div>
  );
}

function StatusBadge({ exam, checked }: { exam: Exam; checked: boolean }) {
  if (checked) {
    return (
      <span className="rounded bg-emerald-100 px-2 py-0.5 text-[11px] font-semibold text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-300">
        Selected
      </span>
    );
  }
  if (exam.status === "review") {
    return (
      <span className="rounded bg-amber-100 px-2 py-0.5 text-[11px] font-semibold text-amber-700 dark:bg-amber-500/20 dark:text-amber-300">
        Review
      </span>
    );
  }
  return (
    <span className="rounded bg-muted px-2 py-0.5 text-[11px] font-semibold text-muted-foreground">
      Not selected
    </span>
  );
}

function ExamGroup({ area, exams }: { area: string; exams: Exam[] }) {
  const [open, setOpen] = useState(true);
  const selected = useSelection((state) => state.selected);
  const toggle = useSelection((state) => state.toggle);
  const setMany = useSelection((state) => state.setMany);

  const ids = exams.map((exam) => exam.id);
  const count = ids.filter((id) => selected.has(id)).length;
  const all: boolean | "indeterminate" =
    count === 0 ? false : count === ids.length ? true : "indeterminate";

  return (
    <section className="overflow-hidden rounded-xl border bg-card">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        aria-expanded={open}
        className="flex w-full items-center gap-3 bg-muted/40 px-4 py-3 text-left"
      >
        <ChevronDown
          className={`size-4 transition-transform ${open ? "" : "-rotate-90"}`}
        />
        <span className="text-sm font-semibold">{area}</span>
        <span className="text-xs text-muted-foreground">
          {exams.length} exams · {count} selected
        </span>
      </button>

      {open && (
        <Table>
          <TableHeader>
            <TableRow className="text-[11px] uppercase tracking-wide">
              <TableHead className="w-12 pl-4">
                <Checkbox
                  checked={all}
                  aria-label={`Select all in ${area}`}
                  onCheckedChange={(value) => setMany(ids, value === true)}
                />
              </TableHead>
              <TableHead>Title</TableHead>
              <TableHead>Program</TableHead>
              <TableHead>Sem.</TableHead>
              <TableHead>Faculty</TableHead>
              <TableHead>Examiner</TableHead>
              <TableHead>Duration</TableHead>
              <TableHead>Est.</TableHead>
              <TableHead>Flags</TableHead>
              <TableHead>Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {exams.map((exam) => {
              const checked = selected.has(exam.id);
              return (
                <TableRow
                  key={exam.id}
                  data-state={checked ? "selected" : undefined}
                  className="h-[54px]"
                >
                  <TableCell className="pl-4">
                    <Checkbox
                      checked={checked}
                      aria-label={`Select ${exam.title}`}
                      onCheckedChange={() => toggle(exam.id)}
                    />
                  </TableCell>
                  <TableCell>
                    <p className="text-sm font-semibold">{exam.title}</p>
                    <p className="text-[11px] text-muted-foreground">
                      {exam.spo} · {EXAM_TYPE_LABEL[exam.type]}
                    </p>
                  </TableCell>
                  <TableCell>
                    <ProgramBadge program={exam.program} />
                  </TableCell>
                  <TableCell>
                    <span className="rounded bg-muted px-1.5 py-0.5 text-[11px] font-medium">
                      {exam.semester}
                    </span>
                  </TableCell>
                  <TableCell className="text-xs">{exam.faculty}</TableCell>
                  <TableCell className="text-xs">{exam.examiner}</TableCell>
                  <TableCell className="text-xs">
                    {exam.durationMinutes} min
                  </TableCell>
                  <TableCell>
                    <span className="inline-flex items-center gap-1.5 text-xs">
                      <Users className="size-3.5 text-muted-foreground" />
                      {exam.estimatedStudents}
                    </span>
                  </TableCell>
                  <TableCell>
                    <Flags flags={exam.flags} />
                  </TableCell>
                  <TableCell>
                    <StatusBadge exam={exam} checked={checked} />
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      )}
    </section>
  );
}

export function ExamsTable({ exams }: { exams: Exam[] }) {
  if (exams.length === 0) {
    return (
      <div className="rounded-xl border border-dashed bg-card p-12 text-center text-sm text-muted-foreground">
        No exams match these filters.
      </div>
    );
  }

  const areas = [...new Set(exams.map((exam) => exam.area))];
  return (
    <div className="space-y-4">
      {areas.map((area) => (
        <ExamGroup
          key={area}
          area={area}
          exams={exams.filter((exam) => exam.area === area)}
        />
      ))}
    </div>
  );
}
