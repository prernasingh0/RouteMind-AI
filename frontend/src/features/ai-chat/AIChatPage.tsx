import { useMutation, useQuery } from '@tanstack/react-query';
import { Send, Wrench } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { useEffect, useRef, useState } from 'react';
import { useSearchParams } from 'react-router';
import { aiApi } from '@/api/endpoints';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
interface ChatMessage { role: 'user'|'assistant'; content: string; references?: string[]; tools?: string[] }
export function AIChatPage() {
  const [params] = useSearchParams(); const [input,setInput]=useState(''); const [messages,setMessages]=useState<ChatMessage[]>([]); const [sentPrompt, setSentPrompt]=useState<string | null>(null); const endRef=useRef<HTMLDivElement>(null);
  const conversation=params.get('conversation'); const prompt=params.get('prompt');
  const history=useQuery({queryKey:['ai-history',conversation],queryFn:()=>aiApi.history(conversation!),enabled:!!conversation});
  useEffect(()=>{ if(history.data) setMessages(history.data as ChatMessage[]) },[history.data]);
  const mutation=useMutation({mutationFn:(m:string)=>aiApi.chat(m),onSuccess:r=>setMessages(m=>[...m,{role:'assistant',content:r.content,references:r.references,tools:r.tool_calls}])});
  useEffect(()=>{ if(prompt && !conversation && messages.length===0 && sentPrompt!==prompt){ setMessages([{role:'user',content:prompt}]); setSentPrompt(prompt); mutation.mutate(prompt); } },[prompt,conversation,messages.length,sentPrompt]);
  useEffect(()=>{endRef.current?.scrollIntoView({behavior:'smooth'})},[messages,mutation.isPending]);
  const submit=(e:React.FormEvent)=>{e.preventDefault(); const value=input.trim(); if(!value||mutation.isPending)return; setMessages(m=>[...m,{role:'user',content:value}]); mutation.mutate(value); setInput('');};
  return <div className="mx-auto max-w-4xl space-y-4"><div><h1 className="text-3xl font-bold">RouteMind AI Chat</h1><p className="text-muted-foreground">Ask about doctors, visit history, routes, or follow-ups.</p></div><Card className="min-h-[60vh] space-y-4 overflow-y-auto">{messages.map((m,i)=><div key={i} className={m.role==='user'?'text-right':'text-left'}><div className="inline-block max-w-[85%] rounded-xl bg-muted p-3 text-sm"><ReactMarkdown>{m.content}</ReactMarkdown>{Boolean(m.tools?.length)&&<p className="mt-2 flex items-center gap-1 text-xs text-muted-foreground"><Wrench size={14}/>{m.tools?.join(', ')}</p>}</div></div>)}{mutation.isPending&&<p className="text-sm text-muted-foreground">RouteMind AI is typing…</p>}<div ref={endRef}/></Card><form className="flex gap-2" onSubmit={submit}><Input value={input} onChange={e=>setInput(e.target.value)} placeholder="Ask RouteMind AI"/><Button disabled={mutation.isPending}><Send size={18}/></Button></form>{mutation.isError&&<p className="text-sm text-destructive">The AI provider is unavailable. Check GEMINI_API_KEY and try again.</p>}</div>;
}
