import { createBrowserRouter, Navigate } from "react-router-dom";
import { AuthLayout } from "@/layouts/AuthLayout";
import { AppLayout } from "@/layouts/AppLayout";
import { LoginPage } from "@/pages/LoginPage";
import { CodePage } from "@/pages/CodePage";
import { HomePage } from "@/pages/HomePage";
import { SchedulePage } from "@/pages/SchedulePage";
import { ConflictsPage } from "@/pages/ConflictsPage";
import { PlanningPage } from "@/pages/PlanningPage";
import { ExamsTab } from "@/pages/planning/ExamsTab";
import { RoomsTab } from "@/pages/planning/RoomsTab";
import { ExaminersTab } from "@/pages/planning/ExaminersTab";
import { ArchiveTab } from "@/pages/planning/ArchiveTab";
import { GuestOnly, RequireAuth } from "@/features/auth/components/RouteGuards";

export const router = createBrowserRouter([
  {
    element: <AuthLayout />,
    children: [
      {
        element: <GuestOnly />,
        children: [
          { path: "/login", element: <LoginPage /> },
          { path: "/login/code", element: <CodePage /> },
        ],
      },
    ],
  },
  {
    element: <RequireAuth />,
    children: [
      {
        element: <AppLayout />,
        children: [
          { path: "/", element: <HomePage /> },
          {
            path: "/planning",
            element: <PlanningPage />,
            children: [
              { index: true, element: <Navigate to="exams" replace /> },
              { path: "exams", element: <ExamsTab /> },
              { path: "rooms", element: <RoomsTab /> },
              { path: "examiners", element: <ExaminersTab /> },
              { path: "archive", element: <ArchiveTab /> },
            ],
          },
          { path: "/schedule", element: <SchedulePage /> },
          { path: "/conflicts", element: <ConflictsPage /> },
        ],
      },
    ],
  },
  { path: "*", element: <Navigate to="/" replace /> },
]);
