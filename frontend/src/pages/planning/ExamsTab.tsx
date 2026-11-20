import { useMemo, useState } from "react";
import { Plus, Upload } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ExamFilters } from "@/features/planning/components/ExamFilters";
import { ExamsTable } from "@/features/planning/components/ExamsTable";
import { SelectionBar } from "@/features/planning/components/SelectionBar";
import { applyFilters, emptyFilters } from "@/features/planning/filters";
import { exams } from "@/features/planning/mock-data";

export function ExamsTab() {
  const [filters, setFilters] = useState(emptyFilters);
  const visible = useMemo(() => applyFilters(exams, filters), [filters]);

  return (
    <div>
      <div className="mb-4 flex justify-end gap-3">
        <Button type="button" variant="outline" className="h-10 gap-2">
          <Upload className="size-4" />
          Import Modulhandbuch
        </Button>
        <Button type="button" className="h-10 gap-2">
          <Plus className="size-4" />
          Add exam
        </Button>
      </div>
      <div className="space-y-4">
        <ExamFilters exams={exams} filters={filters} onChange={setFilters} />
        <ExamsTable exams={visible} />
      </div>
      <SelectionBar visibleIds={visible.map((exam) => exam.id)} />
    </div>
  );
}
