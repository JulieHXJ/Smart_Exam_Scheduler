import { ListFilter, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ALL, emptyFilters, unique, type Filters } from "../filters";
import { EXAM_TYPE_LABEL, type Exam, type ExamFlag } from "../types";

const FLAG_LABEL: Record<ExamFlag, string> = {
  locked: "Locked",
  digital: "Digital",
  repeater: "Repeater",
  mapped: "Mapped",
};

type Option = { value: string; label: string };

function FilterSelect({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: string;
  options: Option[];
  onChange: (value: string) => void;
}) {
  return (
    <select
      aria-label={label}
      value={value}
      onChange={(event) => onChange(event.target.value)}
      className="h-10 min-w-32 rounded-lg border border-input bg-background px-3 text-sm text-foreground outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
    >
      <option value={ALL}>{label}</option>
      {options.map((option) => (
        <option key={option.value} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
  );
}

type Props = {
  exams: Exam[];
  filters: Filters;
  onChange: (filters: Filters) => void;
};

export function ExamFilters({ exams, filters, onChange }: Props) {
  const set = (key: keyof Filters) => (value: string) =>
    onChange({ ...filters, [key]: value });
  const plainOptions = (values: string[]) =>
    unique(values)
      .sort()
      .map((value) => ({ value, label: value }));

  return (
    <div className="flex flex-wrap items-center gap-3 rounded-xl border bg-card p-3">
      <div className="relative min-w-56 flex-1">
        <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          aria-label="Search exams"
          value={filters.search}
          onChange={(event) => set("search")(event.target.value)}
          placeholder="Search title or examiner…"
          className="h-10 pl-9"
        />
      </div>
      <FilterSelect
        label="Faculty / Area"
        value={filters.faculty}
        options={plainOptions(exams.map((exam) => exam.faculty))}
        onChange={set("faculty")}
      />
      <FilterSelect
        label="Degree program"
        value={filters.program}
        options={plainOptions(exams.map((exam) => exam.program))}
        onChange={set("program")}
      />
      <FilterSelect
        label="Semester"
        value={filters.semester}
        options={unique(exams.map((exam) => exam.semester))
          .sort((a, b) => a - b)
          .map((semester) => ({
            value: String(semester),
            label: `Semester ${semester}`,
          }))}
        onChange={set("semester")}
      />
      <FilterSelect
        label="SPO"
        value={filters.spo}
        options={plainOptions(exams.map((exam) => exam.spo))}
        onChange={set("spo")}
      />
      <FilterSelect
        label="Type"
        value={filters.type}
        options={unique(exams.map((exam) => exam.type)).map((type) => ({
          value: type,
          label: EXAM_TYPE_LABEL[type],
        }))}
        onChange={set("type")}
      />
      <FilterSelect
        label="Flags"
        value={filters.flag}
        options={Object.entries(FLAG_LABEL).map(([value, label]) => ({
          value,
          label,
        }))}
        onChange={set("flag")}
      />
      <Button
        variant="outline"
        size="icon"
        className="size-10"
        aria-label="Reset filters"
        onClick={() => onChange(emptyFilters)}
      >
        <ListFilter className="size-4" />
      </Button>
    </div>
  );
}
