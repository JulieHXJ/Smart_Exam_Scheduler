import { createBrowserRouter, Navigate } from "react-router-dom";
import { AuthLayout } from "@/layouts/AuthLayout";
import { LoginPage } from "@/pages/LoginPage";
import { CodePage } from "@/pages/CodePage";
import { HomePage } from "@/pages/HomePage";
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
    children: [{ path: "/", element: <HomePage /> }],
  },
  { path: "*", element: <Navigate to="/" replace /> },
]);
