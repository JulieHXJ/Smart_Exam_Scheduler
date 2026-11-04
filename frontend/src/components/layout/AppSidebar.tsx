import { NavLink, useLocation } from "react-router-dom";
import {
  CalendarDays,
  FileText,
  House,
  TriangleAlert,
  type LucideIcon,
} from "lucide-react";
import { Logo } from "@/components/Logo";
import { Progress } from "@/components/ui/progress";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuBadge,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
  useSidebar,
} from "@/components/ui/sidebar";
import { UserMenu } from "./UserMenu";

type NavItem = { title: string; to: string; icon: LucideIcon; badge?: number };

const NAV: NavItem[] = [
  { title: "Home", to: "/", icon: House },
  { title: "Planning", to: "/planning", icon: FileText },
  { title: "Schedule", to: "/schedule", icon: CalendarDays },
  { title: "Conflicts", to: "/conflicts", icon: TriangleAlert, badge: 3 }, // placeholder count
];

export function AppSidebar() {
  const { pathname } = useLocation();
  const { state } = useSidebar();
  const isActive = (to: string) =>
    to === "/" ? pathname === "/" : pathname.startsWith(to);

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader className="h-16 justify-center border-b border-sidebar-border px-4 group-data-[collapsible=icon]:px-2">
        <Logo compact={state === "collapsed"} />
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel className="text-[11px] font-semibold uppercase tracking-widest text-sidebar-foreground/50">
            Workspace
          </SidebarGroupLabel>
          <SidebarMenu>
            {NAV.map((item) => (
              <SidebarMenuItem key={item.to}>
                <SidebarMenuButton
                  asChild
                  tooltip={item.title}
                  isActive={isActive(item.to)}
                  className="h-10 data-[active=true]:ring-1 data-[active=true]:ring-primary/60"
                >
                  <NavLink to={item.to}>
                    <item.icon />
                    <span>{item.title}</span>
                  </NavLink>
                </SidebarMenuButton>
                {item.badge !== undefined && (
                  <SidebarMenuBadge className="rounded-full bg-primary text-primary-foreground">
                    {item.badge}
                  </SidebarMenuBadge>
                )}
              </SidebarMenuItem>
            ))}
          </SidebarMenu>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="gap-3">
        {/* Placeholder numbers until real schedule data exists */}
        <div className="rounded-xl border border-sidebar-border p-4 group-data-[collapsible=icon]:hidden">
          <div className="flex items-center justify-between text-xs">
            <span>Schedule readiness</span>
            <span className="font-semibold text-primary">86%</span>
          </div>
          <Progress value={86} className="mt-3 h-1 bg-white/10" />
          <p className="mt-3 text-[11px] opacity-50">
            159 of 184 exams scheduled
          </p>
        </div>
        <UserMenu />
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  );
}
