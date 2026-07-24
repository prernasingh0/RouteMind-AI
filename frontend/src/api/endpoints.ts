import { apiClient } from './client';
import type { AIChatResponse, Conversation, Doctor, LoginRequest, NotificationItem, PriorityBreakdown, TokenPair, UserMe, Visit } from '@/types/api';
export const authApi = { login: (payload: LoginRequest) => apiClient.post<TokenPair>('/auth/login', payload).then(r=>r.data), me: () => apiClient.get<UserMe>('/auth/me').then(r=>r.data), logout: (refreshToken: string) => apiClient.post('/auth/logout', { refresh_token: refreshToken }) };
export const dashboardApi = {
  visits: () => apiClient.get<Visit[]>('/visits', { params: { limit: 20, sort: 'scheduled_at' } }).then(r=>r.data),
  doctors: () => apiClient.get<Doctor[]>('/doctors', { params: { limit: 20, sort: 'last_name' } }).then(r=>r.data),
  notifications: () => apiClient.get<NotificationItem[]>('/notifications', { params: { limit: 10, sort: '-created_at' } }).then(r=>r.data),
  conversations: () => apiClient.get<Conversation[]>('/ai/conversations').then(r=>r.data),
  priority: (doctorId: string) => apiClient.get<PriorityBreakdown>(`/doctors/${doctorId}/priority`).then(r=>r.data)
};
export const aiApi = { chat: (message: string, conversation_id?: string) => apiClient.post<AIChatResponse>('/ai/chat', { message, conversation_id }).then(r=>r.data), history: (id: string) => apiClient.get(`/ai/conversations/${id}`).then(r=>r.data) };
