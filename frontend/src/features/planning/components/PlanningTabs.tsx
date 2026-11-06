import { NavLink } from "react-router-dom";

const TABS = [
  { label: "Exams", to: "/planning/exams" },
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
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  );
}
