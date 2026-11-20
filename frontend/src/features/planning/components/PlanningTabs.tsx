import { NavLink } from "react-router-dom";
import { exams } from "../mock-data";

const TABS = [
  { label: "Exams", to: "/planning/exams", count: exams.length },
  { label: "Rooms", to: "/planning/rooms" },
  { label: "Examiners", to: "/planning/examiners" },
  { label: "Archive", to: "/planning/archive" },
];

export function PlanningTabs() {
  return (
    <nav
      aria-label="Planning sections"
      className="mb-6 overflow-x-auto border-b"
    >
      <ul className="flex min-w-max gap-8">
        {TABS.map((tab) => (
          <li key={tab.to}>
            <NavLink
              to={tab.to}
              className="-mb-px block border-b-2 border-transparent px-1 pb-3 pt-2 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground aria-[current=page]:border-primary aria-[current=page]:text-primary"
            >
              {tab.label}
              {tab.count !== undefined && (
                <span className="ml-2 rounded-full bg-muted px-2 py-0.5 text-[10px] font-semibold text-muted-foreground">
                  {tab.count}
                </span>
              )}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  );
}
