export type UUID = string;
export interface TokenPair { access_token: string; refresh_token: string; token_type: 'bearer'; expires_in: number }
export interface LoginRequest { organization_slug: string; email: string; password: string }
export interface UserMe { id: UUID; organization_id: UUID; email: string; full_name: string; roles: string[]; permissions: string[] }
export interface Visit { id: UUID; hcp_id: UUID; scheduled_at: string; status: string; outcome?: string | null }
export interface Doctor { id: UUID; first_name: string; last_name: string; npi?: string | null; engagement_score: number; prescription_trend: number }
export interface NotificationItem { id: UUID; title: string; body: string; notification_type: string; read_at?: string | null; created_at: string }
export interface Conversation { id: UUID; title: string; summary?: string | null; created_at: string; updated_at: string }
export interface PriorityBreakdown { hcp_id: UUID; total_score: number; classification: 'low' | 'medium' | 'high' | string; factors: Record<string, number> }
export interface AIChatResponse { content: string; intent: string; references: string[]; tool_calls: string[]; metadata: Record<string, unknown> }
export interface DoctorProfile { doctor: Doctor; territory?: { id: string; name: string } | null; region?: { id: string; name: string } | null; products: Record<string, unknown>[]; visit_history: Record<string, unknown>[]; campaigns: Record<string, unknown>[]; recommendations: Record<string, unknown>[]; current_priority: PriorityBreakdown; recent_ai_interactions: Record<string, unknown>[]; tags: string[] }
export interface TimelineItem { id: string; type: string; occurred_at: string; title: string; description: string; metadata: Record<string, unknown> }
export interface PriorityHistoryItem { id: string; total_score: number; classification: string; factors: Record<string, number>; explanation: string; created_at: string }
export interface Route { id: UUID; name: string; route_date: string; status: string }
export interface CalendarItem { id: UUID; type: string; title: string; starts_at: string; ends_at: string; hcp_id?: UUID | null; status?: string }
