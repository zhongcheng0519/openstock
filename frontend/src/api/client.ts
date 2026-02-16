import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

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
