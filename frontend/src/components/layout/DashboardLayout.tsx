'use client';

import { ReactNode } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import {
  LayoutGrid,
  Settings,
  Users,
  ChevronRight,
  Menu,
  X
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import { useState } from 'react';

interface DashboardLayoutProps {
  children: ReactNode;
}

interface SidebarNavProps {
  items: {
    title: string;
    href: string;
    icon: ReactNode;
  }[];
}

const navigation = [
  {
    title: 'Workspaces',
    href: '/dashboard/workspaces',
    icon: <LayoutGrid className="w-5 h-5" />,
  },
  {
    title: 'Users',
    href: '/dashboard/users',
    icon: <Users className="w-5 h-5" />,
  },
  {
    title: 'Settings',
    href: '/dashboard/settings',
    icon: <Settings className="w-5 h-5" />,
  },
];

function SidebarNav({ items }: SidebarNavProps) {
  const pathname = usePathname();

  return (
    <nav className="grid items-start gap-2">
      {items.map((item) => {
        const isActive = pathname === item.href;
        return (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              'flex items-center gap-2 px-3 py-2 text-sm font-medium rounded-lg hover:bg-accent hover:text-accent-foreground transition-colors',
              isActive ? 'bg-accent text-accent-foreground' : 'text-muted-foreground'
            )}
          >
            {item.icon}
            {item.title}
          </Link>
        );
      })}
    </nav>
  );
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const pathname = usePathname();
  
  // Generate breadcrumbs from pathname
  const breadcrumbs = pathname
    .split('/')
    .filter(Boolean)
    .map((segment, index, array) => ({
      title: segment.charAt(0).toUpperCase() + segment.slice(1),
      href: '/' + array.slice(0, index + 1).join('/'),
      isLast: index === array.length - 1,
    }));

  return (
    <div className="flex min-h-screen">
      {/* Desktop Sidebar */}
      <aside className="hidden lg:flex w-64 shrink-0 border-r min-h-screen">
        <div className="flex flex-col gap-4 p-4">
          <div className="flex items-center gap-2 px-2">
            <LayoutGrid className="w-6 h-6" />
            <span className="text-lg font-semibold">IDE</span>
          </div>
          <ScrollArea className="flex-1">
            <SidebarNav items={navigation} />
          </ScrollArea>
        </div>
      </aside>

      {/* Mobile Sidebar */}
      <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
        <SheetTrigger asChild>
          <Button
            variant="ghost"
            className="lg:hidden fixed left-4 top-4 z-40"
            size="icon"
          >
            <Menu className="h-5 w-5" />
          </Button>
        </SheetTrigger>
        <SheetContent side="left" className="w-64 p-0">
          <div className="flex flex-col gap-4 p-4">
            <div className="flex items-center justify-between px-2">
              <div className="flex items-center gap-2">
                <LayoutGrid className="w-6 h-6" />
                <span className="text-lg font-semibold">IDE</span>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setSidebarOpen(false)}
              >
                <X className="h-5 w-5" />
              </Button>
            </div>
            <ScrollArea className="flex-1">
              <SidebarNav items={navigation} />
            </ScrollArea>
          </div>
        </SheetContent>
      </Sheet>

      {/* Main Content */}
      <main className="flex-1">
        <div className="border-b">
          <div className="flex h-16 items-center gap-4 px-4">
            <nav className="flex items-center gap-1 text-sm">
              {breadcrumbs.map((crumb) => (
                <div key={crumb.href} className="flex items-center gap-1">
                  {!crumb.isLast ? (
                    <>
                      <Link
                        href={crumb.href}
                        className="text-muted-foreground hover:text-foreground transition-colors"
                      >
                        {crumb.title}
                      </Link>
                      <ChevronRight className="h-4 w-4 text-muted-foreground" />
                    </>
                  ) : (
                    <span className="font-medium">{crumb.title}</span>
                  )}
                </div>
              ))}
            </nav>
          </div>
        </div>
        <div className="p-6">{children}</div>
      </main>
    </div>
  );
}
