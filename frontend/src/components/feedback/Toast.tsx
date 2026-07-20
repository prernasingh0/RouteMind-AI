import { createContext, ReactNode, useContext, useState } from 'react';
const ToastContext = createContext<(message: string) => void>(()=>undefined);
export function ToastProvider({ children }: { children: ReactNode }) { const [message,setMessage]=useState<string>(); return <ToastContext.Provider value={(m)=>{setMessage(m); setTimeout(()=>setMessage(undefined), 3500);}}>{children}{message && <div className="fixed bottom-4 right-4 rounded-lg bg-foreground px-4 py-3 text-background shadow-lg">{message}</div>}</ToastContext.Provider>; }
export function useToast(){return useContext(ToastContext);}
