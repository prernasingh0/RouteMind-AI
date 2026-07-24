import { HTMLAttributes } from 'react';import { cn } from '@/utils/cn';
export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) { return <section className={cn('rounded-xl border bg-card p-5 text-card-foreground shadow-sm', className)} {...props} />; }
