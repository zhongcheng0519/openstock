import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_info')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    if (error.response) {
      const message = error.response.data?.detail || '请求失败'
      return Promise.reject(new Error(message))
    }
    return Promise.reject(error)
  }
)

export interface StockFilterRequest {
  trade_date: string
  min_pct?: number
  max_pct?: number
  min_circ_mv?: number
  max_circ_mv?: number | null
  min_pe?: number
  max_pe?: number
  min_turnover_rate?: number
  max_turnover_rate?: number | null
  min_net_mf_amount?: number | null
  mf_top_n?: number
}

export interface PctFilterRequest {
  trade_date: string
  min_pct: number
  max_pct: number
}

export interface DailyQuote {
  ts_code: string
  symbol: string
  name: string
  trade_date: string
  open: number | null
  high: number | null
  low: number | null
  close: number | null
  pre_close: number | null
  change: number | null
  pct_chg: number | null
  vol: number | null
  amount: number | null
  circ_mv: number | null
  pe: number | null
  turnover_rate: number | null
  net_mf_amount: number | null
  net_mf_vol: number | null
}

export interface StockFilterResponse {
  trade_date: string
  count: number
  data: DailyQuote[]
}

export interface PctFilterResponse {
  trade_date: string
  count: number
  data: DailyQuote[]
}

export interface SyncStatusResponse {
  message: string
  synced_count: number
}

export interface UserResponse {
  id: number
  username: string
  nickname: string
  email: string | null
  phone: string | null
  role: string
  is_active: boolean
  created_at: string
  updated_at: string | null
}

export interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: UserResponse
}

export interface UserRegisterRequest {
  username: string
  nickname: string
  password: string
  email: string
  phone?: string
}

export interface UserLoginRequest {
  username: string
  password: string
}

export interface PasswordChangeRequest {
  old_password: string
  new_password: string
}

export interface ProfileUpdateRequest {
  nickname: string
  email: string
  phone?: string
}

export interface UserCreateRequest {
  username: string
  nickname: string
  password: string
  email: string
  phone?: string
  role: string
}

export interface UserListResponse {
  total: number
  page: number
  page_size: number
  items: UserResponse[]
}

export interface UserLogResponse {
  id: number
  user_id: number | null
  username: string | null
  action: string
  resource: string | null
  method: string | null
  ip_address: string | null
  status_code: number | null
  created_at: string
}

export interface UserLogListResponse {
  total: number
  page: number
  page_size: number
  items: UserLogResponse[]
}

export interface LogStatisticsResponse {
  total_requests: number
  unique_users: number
  by_action: Record<string, number>
  by_user: Array<{ user_id: number | null; username: string; count: number }>
}

export const strategyApi = {
  stockFilter: (params: StockFilterRequest) =>
    apiClient.post<StockFilterResponse>('/api/v1/strategy/filter', params),

  pctFilter: (params: PctFilterRequest) =>
    apiClient.post<PctFilterResponse>('/api/v1/strategy/pct-filter', params),

  syncStocks: () =>
    apiClient.post<SyncStatusResponse>('/api/v1/strategy/sync-stocks'),

  syncDaily: (tradeDate: string) =>
    apiClient.post<SyncStatusResponse>(`/api/v1/strategy/sync-daily/${tradeDate}`),
}

export const authApi = {
  register: (data: UserRegisterRequest) =>
    apiClient.post<UserResponse>('/api/v1/auth/register', data),

  login: (data: UserLoginRequest) =>
    apiClient.post<TokenResponse>('/api/v1/auth/login', data),

  logout: () =>
    apiClient.post('/api/v1/auth/logout'),

  getMe: () =>
    apiClient.get<UserResponse>('/api/v1/auth/me'),

  changePassword: (data: PasswordChangeRequest) =>
    apiClient.put('/api/v1/auth/password', data),

  updateProfile: (data: ProfileUpdateRequest) =>
    apiClient.put<UserResponse>('/api/v1/auth/profile', data),
}

export const adminApi = {
  getUsers: (params?: { page?: number; page_size?: number; role?: string; is_active?: boolean }) =>
    apiClient.get<UserListResponse>('/api/v1/admin/users', { params }),

  createUser: (data: UserCreateRequest) =>
    apiClient.post<UserResponse>('/api/v1/admin/users', data),

  updateUserStatus: (userId: number, isActive: boolean) =>
    apiClient.put<UserResponse>(`/api/v1/admin/users/${userId}`, { is_active: isActive }),

  resetUserPassword: (userId: number, newPassword: string) =>
    apiClient.put(`/api/v1/admin/users/${userId}/reset-password`, { new_password: newPassword }),

  deleteUser: (userId: number) =>
    apiClient.delete(`/api/v1/admin/users/${userId}`),

  getLogs: (params?: { page?: number; page_size?: number; user_id?: number; action?: string; start_date?: string; end_date?: string }) =>
    apiClient.get<UserLogListResponse>('/api/v1/admin/logs', { params }),

  getLogStatistics: (params?: { start_date?: string; end_date?: string }) =>
    apiClient.get<LogStatisticsResponse>('/api/v1/admin/logs/statistics', { params }),
}
