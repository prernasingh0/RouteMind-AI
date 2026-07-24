import { Bell, Bot, CalendarDays, LayoutDashboard, LogOut, Menu, Moon, Route, Search, Settings, Stethoscope, Sun, X } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link, NavLink, Outlet, useLocation, useNavigate } from 'react-router';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { APP_NAME } from '@/constants/env';
import { useAuth } from '@/contexts/AuthContext';
import { useOnlineStatus } from '@/hooks/useOnlineStatus';
import { cn } from '@/utils/cn';

const nav = [{ to: '/', label: 'Dashboard', icon: LayoutDashboard }, { to: '/ai', label: 'AI Chat', icon: Bot }, { to: '/doctors', label: 'Doctors', icon: Stethoscope }, { to: '/visits', label: 'Visits', icon: CalendarDays }, { to: '/routes', label: 'Routes', icon: Route }, { to: '/calendar', label: 'Calendar', icon: CalendarDays }, { to: '/settings', label: 'Settings', icon: Settings }];

export function AppLayout() {
  const online = useOnlineStatus();
  const [open, setOpen] = useState(false);
  const [dark, setDark] = useState(() => localStorage.theme === 'dark' || (!localStorage.theme && matchMedia('(prefers-color-scheme: dark)').matches));
  const auth = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const current = nav.find((item) => item.to !== '/' && location.pathname.startsWith(item.to)) ?? nav[0];
  useEffect(() => { document.documentElement.classList.toggle('dark', dark); localStorage.theme = dark ? 'dark' : 'light'; }, [dark]);
  return <div className="min-h-screen lg:grid lg:grid-cols-[280px_1fr]">
    <div className={cn('fixed inset-0 z-30 bg-black/40 lg:hidden', open ? 'block' : 'hidden')} onClick={() => setOpen(false)} />
    <aside className={cn('fixed inset-y-0 z-40 w-72 border-r bg-card p-4 transition lg:static lg:translate-x-0', open ? 'translate-x-0' : '-translate-x-full lg:translate-x-0')}>
      <Link to="/" onClick={() => setOpen(false)} className="text-xl font-bold text-foreground">{APP_NAME}</Link><p className="mt-1 text-xs text-muted-foreground">Enterprise field intelligence</p>
      <nav className="mt-8 space-y-2">{nav.map(({ to, label, icon: Icon }) => <NavLink key={to} to={to} onClick={() => setOpen(false)} className={({ isActive }) => cn('flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-foreground hover:bg-muted', isActive && 'bg-muted')}><Icon size={18} />{label}</NavLink>)}</nav>
      <div className="absolute bottom-4 left-4 right-4 rounded-lg bg-muted p-3 text-sm"><p className="font-medium">{auth.user?.full_name}</p><p className="truncate text-muted-foreground">{auth.user?.email}</p></div>
    </aside>
    <div className="min-w-0"><header className="sticky top-0 z-50 flex h-16 items-center gap-3 border-b bg-background/95 px-4 backdrop-blur"><Button className="lg:hidden" onClick={() => setOpen(!open)}>{open ? <X size={18} /> : <Menu size={18} />}</Button><Button className="bg-muted text-foreground" onClick={() => navigate(-1)} aria-label="Go back">←</Button><div className="text-sm text-muted-foreground">{current.label}</div><div className="ml-auto flex items-center gap-2">{!online && <span className="rounded-full bg-red-100 px-2 py-1 text-xs text-red-700">Offline</span>}<div className="relative hidden md:block"><Search className="absolute left-3 top-2.5" size={16} /><Input className="w-80 pl-9" placeholder="Search doctors, visits, campaigns" /></div><Button className="bg-muted text-foreground"><Bell size={18} /></Button><Button className="bg-muted text-foreground" onClick={() => setDark(!dark)}>{dark ? <Sun size={18} /> : <Moon size={18} />}</Button><Button onClick={auth.logout}><LogOut size={18} /></Button></div></header><main className="min-w-0 p-4 lg:p-8"><Outlet /></main></div>
  </div>;
}
