import { InputHTMLAttributes } from 'react';import { cn } from '@/utils/cn';
export function Input({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) { return <input className={cn('focus-ring w-full rounded-lg border bg-background px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground', className)} {...props} />; }
