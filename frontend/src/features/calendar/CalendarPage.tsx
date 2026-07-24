import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { calendarApi } from '@/api/operations';
import { Card } from '@/components/ui/Card';
import { EmptyState, ErrorState, LoadingSkeleton } from '@/components/feedback/States';

export function CalendarPage() {
  const [anchor, setAnchor] = useState(() => new Date());
  const start = useMemo(() => { const d = new Date(anchor); d.setHours(0, 0, 0, 0); return d; }, [anchor]);
  const end = new Date(start); end.setDate(end.getDate() + 7);
  const query = useQuery({ queryKey: ['calendar', start.toISOString()], queryFn: () => calendarApi(start.toISOString(), end.toISOString()) });
  if (query.isLoading) return <LoadingSkeleton />; if (query.error) return <ErrorState message={(query.error as Error).message} />;
  const days = Array.from({ length: 7 }, (_, index) => { const d = new Date(start); d.setDate(d.getDate() + index); return d; });
  return <div className="space-y-5"><div className="flex flex-wrap items-center justify-between gap-3"><div><h1 className="text-3xl font-bold">Calendar</h1><p className="text-muted-foreground">Scheduled HCP visits and field activities.</p></div><div className="flex gap-2"><button className="rounded border px-3 py-2" onClick={() => setAnchor(new Date())}>Today</button><button className="rounded border px-3 py-2" onClick={() => setAnchor(new Date(start.getTime() - 7 * 86400000))}>←</button><button className="rounded border px-3 py-2" onClick={() => setAnchor(new Date(start.getTime() + 7 * 86400000))}>→</button></div></div><Card><div className="grid min-w-[900px] grid-cols-7 divide-x">{days.map((day) => { const items = (query.data ?? []).filter((item) => new Date(item.starts_at).toDateString() === day.toDateString()); return <div className="min-h-72 p-2" key={day.toISOString()}><div className="mb-3 border-b pb-2 text-sm font-semibold">{day.toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric' })}</div>{items.map((item) => <div className="mb-2 rounded-lg bg-primary/10 p-2 text-xs" key={item.id}><b>{item.hcp_name ?? item.title}</b><p>{new Date(item.starts_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p><span className="text-muted-foreground">{item.status ?? item.type}</span></div>)}</div>; })}</div>{!query.data?.length && <EmptyState title="No events" description="Scheduled visits appear here automatically." />}</Card></div>;
}
