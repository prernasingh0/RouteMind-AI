import { apiClient } from './client';
import type { Doctor, DoctorProfile, PriorityBreakdown, PriorityHistoryItem, TimelineItem } from '@/types/api';
export interface DoctorFilters { limit?: number; offset?: number; sort?: string; search?: string; territory_id?: string; region_id?: string; specialty_id?: string; status?: string; tag?: string }
export interface DoctorPayload { territory_id: string; specialty_id?: string | null; first_name: string; last_name: string; npi?: string | null; email?: string | null; phone?: string | null; status?: string; engagement_score?: number; prescription_trend?: number; manager_adjustment?: number }
export const doctorsApi = {
  list: (params: DoctorFilters) => apiClient.get<Doctor[]>('/doctors/search', { params }).then(r=>r.data),
  create: (payload: DoctorPayload) => apiClient.post<Doctor>('/doctors', payload).then(r=>r.data),
  update: (id: string, payload: Partial<DoctorPayload>) => apiClient.patch<Doctor>(`/doctors/${id}`, payload).then(r=>r.data),
  delete: (id: string) => apiClient.delete(`/doctors/${id}`),
  bulk: (doctor_ids: string[], operation: string, value?: string) => apiClient.post('/doctors/bulk', { doctor_ids, operation, value }).then(r=>r.data),
  exportCsv: () => apiClient.get('/doctors/export', { responseType: 'blob' }).then(r=>r.data),
  importCsv: (file: File) => { const form = new FormData(); form.append('file', file); return apiClient.post('/doctors/import', form).then(r=>r.data); },
  profile: (id: string) => apiClient.get<DoctorProfile>(`/doctors/${id}/profile`).then(r=>r.data),
  timeline: (id: string) => apiClient.get<TimelineItem[]>(`/doctors/${id}/timeline`).then(r=>r.data),
  priority: (id: string) => apiClient.get<PriorityBreakdown>(`/doctors/${id}/priority`).then(r=>r.data),
  priorityHistory: (id: string) => apiClient.get<PriorityHistoryItem[]>(`/doctors/${id}/priority/history`).then(r=>r.data),
  simulatePriority: (id: string, payload: Record<string, number>) => apiClient.post(`/doctors/${id}/priority/simulate`, payload).then(r=>r.data)
};
