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
  vol_ratio?: number | null
  mf_top_n?: number
}

export interface FilterCondition {
  field: string
  operator: string
  value: number
}

export interface StockFilterBackendRequest {
  trade_date: string
  conditions: FilterCondition[]
  vol_ratio: number | null
  mf_top_n: number
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

export interface LatestTradeDateResponse {
  trade_date: string
  exchange: string
}

export interface FavoriteStock {
  id: number
  user_id: number
  ts_code: string
  stock_name: string | null
  created_at: string
}

export interface FavoriteStockListResponse {
  total: number
  items: FavoriteStock[]
}

export interface AddFavoriteRequest {
  ts_code: string
}

export interface FavoriteStatusResponse {
  is_favorited: boolean
}

export interface StockSearchItem {
  ts_code: string
  name: string
}

export interface StockDetailResponse {
  ts_code: string
  symbol: string
  name: string
  area: string | null
  industry: string | null
  trade_date: string | null
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
  buy_sm_vol: number | null
  buy_sm_amount: number | null
  sell_sm_vol: number | null
  sell_sm_amount: number | null
  buy_md_vol: number | null
  buy_md_amount: number | null
  sell_md_vol: number | null
  sell_md_amount: number | null
  buy_lg_vol: number | null
  buy_lg_amount: number | null
  sell_lg_vol: number | null
  sell_lg_amount: number | null
  buy_elg_vol: number | null
  buy_elg_amount: number | null
  sell_elg_vol: number | null
  sell_elg_amount: number | null
}

export const strategyApi = {
  stockFilter: (params: StockFilterRequest) => {
    const conditions: FilterCondition[] = []
    
    if (params.min_pct !== undefined && params.min_pct !== null) {
      conditions.push({ field: 'pct_chg', operator: 'gte', value: params.min_pct })
    }
    if (params.max_pct !== undefined && params.max_pct !== null) {
      conditions.push({ field: 'pct_chg', operator: 'lte', value: params.max_pct })
    }
    if (params.min_circ_mv !== undefined && params.min_circ_mv !== null) {
      conditions.push({ field: 'circ_mv', operator: 'gte', value: params.min_circ_mv })
    }
    if (params.max_circ_mv !== undefined && params.max_circ_mv !== null) {
      conditions.push({ field: 'circ_mv', operator: 'lte', value: params.max_circ_mv })
    }
    if (params.min_pe !== undefined && params.min_pe !== null) {
      conditions.push({ field: 'pe', operator: 'gte', value: params.min_pe })
    }
    if (params.max_pe !== undefined && params.max_pe !== null) {
      conditions.push({ field: 'pe', operator: 'lte', value: params.max_pe })
    }
    if (params.min_turnover_rate !== undefined && params.min_turnover_rate !== null) {
      conditions.push({ field: 'turnover_rate', operator: 'gte', value: params.min_turnover_rate })
    }
    if (params.max_turnover_rate !== undefined && params.max_turnover_rate !== null) {
      conditions.push({ field: 'turnover_rate', operator: 'lte', value: params.max_turnover_rate })
    }
    if (params.min_net_mf_amount !== undefined && params.min_net_mf_amount !== null) {
      conditions.push({ field: 'net_mf_amount', operator: 'gte', value: params.min_net_mf_amount })
    }

    const vol_ratio = params.vol_ratio !== undefined && params.vol_ratio !== null ? params.vol_ratio : null

    const backendRequest: StockFilterBackendRequest = {
      trade_date: params.trade_date,
      conditions,
      vol_ratio,
      mf_top_n: params.mf_top_n || 30
    }
    
    return apiClient.post<StockFilterResponse>('/api/v1/strategy/filter', backendRequest)
  },

  syncStocks: () =>
    apiClient.post<SyncStatusResponse>('/api/v1/strategy/sync-stocks'),

  syncDaily: (tradeDate: string) =>
    apiClient.post<SyncStatusResponse>(`/api/v1/strategy/sync-daily/${tradeDate}`),

  getLatestTradeDate: (exchange: string = 'SSE') =>
    apiClient.get<LatestTradeDateResponse>('/api/v1/strategy/trade-calendar/latest', { params: { exchange } }),

  getStockDetail: (tsCode: string, tradeDate?: string) => {
    const params = tradeDate ? { trade_date: tradeDate } : {}
    return apiClient.get<StockDetailResponse>(`/api/v1/strategy/stock/${tsCode}`, { params })
  },

  getFavorites: () =>
    apiClient.get<FavoriteStockListResponse>('/api/v1/strategy/favorites'),

  addFavorite: (tsCode: string) =>
    apiClient.post<FavoriteStock>('/api/v1/strategy/favorites', { ts_code: tsCode }),

  removeFavorite: (tsCode: string) =>
    apiClient.delete(`/api/v1/strategy/favorites/${tsCode}`),

  checkFavoriteStatus: (tsCode: string) =>
    apiClient.get<FavoriteStatusResponse>(`/api/v1/strategy/favorites/${tsCode}/status`),

  searchStocks: (query: string, limit: number = 20) =>
    apiClient.get<StockSearchItem[]>('/api/v1/strategy/stocks/search', { 
      params: { q: query, limit } 
    }),
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
