import { apiClient } from './client';
import type { CalendarItem, Route, Visit } from '@/types/api';
export const visitsApi = {
  list: () => apiClient.get<Visit[]>('/visits', { params: { limit: 100, sort: 'scheduled_at' } }).then((r) => r.data),
  create: (payload: { hcp_id: string; scheduled_at: string; outcome?: string; follow_up_at?: string }) => apiClient.post<Visit>('/visits', payload).then((r) => r.data),
  update: (id: string, payload: Partial<Visit>) => apiClient.patch<Visit>(`/visits/${id}`, payload).then((r) => r.data),
  timeline: (id: string) => apiClient.get(`/visits/${id}/timeline`).then((r) => r.data),
};
export const routesApi = {
  list: () => apiClient.get<Route[]>('/routes', { params: { limit: 100, sort: 'route_date' } }).then((r) => r.data),
  create: (payload: { name: string; route_date: string; stops: { hcp_id: string }[] }) => apiClient.post<Route>('/routes', payload).then((r) => r.data),
  optimize: (id: string) => apiClient.post(`/routes/${id}/optimize`).then((r) => r.data),
  plan: (payload: { route_date: string; hcp_ids: string[]; workday_start: string; workday_end: string; origin_latitude?: number; origin_longitude?: number }) => apiClient.post('/routes/plan', payload).then((r) => r.data),
};
export const calendarApi = (starts_at: string, ends_at: string) => apiClient.get<CalendarItem[]>('/calendar', { params: { starts_at, ends_at } }).then((r) => r.data);
