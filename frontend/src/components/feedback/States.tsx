import { AlertTriangle, Loader2 } from 'lucide-react';
export function LoadingSkeleton() { return <div className="animate-pulse space-y-3"><div className="h-5 w-1/3 rounded bg-muted"/><div className="h-20 rounded bg-muted"/></div>; }
export function EmptyState({ title, description }: { title: string; description: string }) { return <div className="rounded-xl border border-dashed p-6 text-center"><p className="font-semibold">{title}</p><p className="text-sm text-muted-foreground">{description}</p></div>; }
export function ErrorState({ message }: { message: string }) { return <div className="flex items-center gap-2 rounded-xl border border-red-300 bg-red-50 p-4 text-red-700 dark:bg-red-950"><AlertTriangle size={18}/>{message}</div>; }
export function Spinner() { return <Loader2 className="animate-spin" size={18}/>; }
