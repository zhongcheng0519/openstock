import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const message = error.response.data?.detail || '请求失败'
      return Promise.reject(new Error(message))
    }
    return Promise.reject(error)
  }
)

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

export const strategyApi = {
  // 涨跌幅筛选
  pctFilter: (params: PctFilterRequest) =>
    apiClient.post<PctFilterResponse>('/api/v1/strategy/pct-filter', params),

  // 同步股票基础信息
  syncStocks: () =>
    apiClient.post<SyncStatusResponse>('/api/v1/strategy/sync-stocks'),

  // 同步日线行情
  syncDaily: (tradeDate: string) =>
    apiClient.post<SyncStatusResponse>(`/api/v1/strategy/sync-daily/${tradeDate}`),
}
