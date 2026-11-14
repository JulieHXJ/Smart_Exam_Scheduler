import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { ThemeProvider } from "next-themes";
import { RouterProvider } from "react-router-dom";
import { router } from "@/app/router";
import "@fontsource-variable/inter";
import "./index.css";
import { useAuth } from "./features/auth/store";

void useAuth.getState().load();

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
      <RouterProvider router={router} />
    </ThemeProvider>
  </StrictMode>,
);
