import axios, { AxiosError, type AxiosRequestConfig } from 'axios';
import { API_BASE_URL } from '@/constants/env';
import { tokenStorage } from '@/services/tokenStorage';
import type { TokenPair } from '@/types/api';

interface RetryConfig extends AxiosRequestConfig { _retry?: boolean; _attempt?: number }
export class ApiError extends Error { constructor(public status: number, message: string, public details?: unknown) { super(message); } }
export const apiClient = axios.create({ baseURL: API_BASE_URL, timeout: 30000 });
let refreshPromise: Promise<string> | null = null;
async function refreshAccessToken(): Promise<string> {
  const refreshToken = tokenStorage.getRefreshToken(); if (!refreshToken) throw new ApiError(401, 'Missing refresh token');
  const { data } = await axios.post<TokenPair>(`${API_BASE_URL}/auth/refresh`, { refresh_token: refreshToken });
  tokenStorage.setTokens(data.access_token, data.refresh_token); return data.access_token;
}
apiClient.interceptors.request.use((config) => { const token = tokenStorage.getAccessToken(); if (token) config.headers.Authorization = `Bearer ${token}`; return config; });
apiClient.interceptors.response.use((response) => response, async (error: AxiosError) => {
  const config = error.config as RetryConfig | undefined; const status = error.response?.status;
  if (status === 401 && config && !config._retry) { config._retry = true; refreshPromise ??= refreshAccessToken().finally(() => { refreshPromise = null; }); const token = await refreshPromise; config.headers = { ...config.headers, Authorization: `Bearer ${token}` }; return apiClient(config); }
  if ((!status || status >= 500) && config && (config._attempt ?? 0) < 2) { config._attempt = (config._attempt ?? 0) + 1; await new Promise((r) => setTimeout(r, 300 * config._attempt!)); return apiClient(config); }
  throw new ApiError(status ?? 0, (error.response?.data as { detail?: string } | undefined)?.detail ?? error.message, error.response?.data);
});
export function cancellableRequest<T>(config: AxiosRequestConfig) { const controller = new AbortController(); const request = apiClient.request<T>({ ...config, signal: controller.signal }); return { request, cancel: () => controller.abort() }; }
