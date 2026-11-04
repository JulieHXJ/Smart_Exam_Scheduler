import { createBrowserRouter, Navigate } from "react-router-dom";
import { AuthLayout } from "@/layouts/AuthLayout";
import { AppLayout } from "@/layouts/AppLayout";
import { LoginPage } from "@/pages/LoginPage";
import { CodePage } from "@/pages/CodePage";
import { HomePage } from "@/pages/HomePage";
import { PlanningPage } from "@/pages/PlanningPage";
import { SchedulePage } from "@/pages/SchedulePage";
import { ConflictsPage } from "@/pages/ConflictsPage";
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
          { path: "/planning", element: <PlanningPage /> },
          { path: "/schedule", element: <SchedulePage /> },
          { path: "/conflicts", element: <ConflictsPage /> },
        ],
      },
    ],
  },
  { path: "*", element: <Navigate to="/" replace /> },
]);
