import { Outlet } from "react-router-dom";
import { PageHeader } from "@/components/layout/PageHeader";
import { PlanningTabs } from "@/features/planning/components/PlanningTabs";

export function PlanningPage() {
  return (
    <>
      <PageHeader
        eyebrow="Data inventory"
        title="Planning"
        description="Select and prepare the exams, rooms, and examiners for this term."
      />
      <PlanningTabs />
      <Outlet />
    </>
  );
}
