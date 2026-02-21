<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部导航栏 -->
    <nav class="navbar">
      <div class="navbar-content">
        <router-link to="/" class="navbar-brand">
          <div class="navbar-logo">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
            </svg>
          </div>
          <span>股票分析系统</span>
        </router-link>
        
        <div class="navbar-menu">
          <router-link to="/" class="navbar-link active">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"></path>
            </svg>
            股票筛选
          </router-link>
          <router-link to="/profile" class="navbar-link">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
            </svg>
            个人中心
          </router-link>
          <template v-if="isAdmin">
            <router-link to="/users" class="navbar-link">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path>
              </svg>
              用户管理
            </router-link>
            <router-link to="/logs" class="navbar-link">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
              操作日志
            </router-link>
          </template>
        </div>
        
        <div class="navbar-user">
          <div class="user-info">
            <div class="user-avatar">
              {{ userInitial }}
            </div>
            <span class="user-name">{{ userName }}</span>
          </div>
          <button @click="handleLogout" class="btn btn-secondary btn-sm">
            <svg style="width: 16px; height: 16px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
            </svg>
            退出
          </button>
        </div>
      </div>
    </nav>

    <!-- 主内容区 -->
    <main class="main-container">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1 class="page-title">股票筛选</h1>
        <p class="page-subtitle">根据多维度条件筛选符合投资策略的股票</p>
      </div>
      
      <!-- 筛选条件卡片 -->
      <div class="filter-card">
        <form @submit.prevent="handleFilter">
          <div class="filter-grid">
            <div class="form-group">
              <label class="label label-required">交易日期</label>
              <el-date-picker
                v-model="filterForm.trade_date"
                type="date"
                placeholder="选择日期"
                format="YYYY-MM-DD"
                value-format="YYYYMMDD"
                class="w-full"
              />
            </div>
            <div class="form-group">
              <label class="label">涨跌幅最小值 (%)</label>
              <el-input-number
                v-model="filterForm.min_pct"
                :min="-100"
                :max="100"
                :step="0.1"
                class="w-full"
              />
            </div>
            <div class="form-group">
              <label class="label">涨跌幅最大值 (%)</label>
              <el-input-number
                v-model="filterForm.max_pct"
                :min="-100"
                :max="100"
                :step="0.1"
                class="w-full"
              />
            </div>
            <div class="form-group">
              <label class="label">流通市值最小值 (亿元)</label>
              <el-input-number
                v-model="filterForm.min_circ_mv_yi"
                :min="0"
                :max="100000"
                :step="10"
                class="w-full"
              />
            </div>
            <div class="form-group">
              <label class="label">流通市值最大值 (亿元)</label>
              <el-input-number
                v-model="filterForm.max_circ_mv_yi"
                :min="0"
                :max="100000"
                :step="10"
                placeholder="不限制"
                class="w-full"
              />
            </div>
            <div class="form-group">
              <label class="label">市盈率最小值</label>
              <el-input-number
                v-model="filterForm.min_pe"
                :min="0"
                :max="1000"
                :step="1"
                class="w-full"
              />
            </div>
            <div class="form-group">
              <label class="label">市盈率最大值</label>
              <el-input-number
                v-model="filterForm.max_pe"
                :min="0"
                :max="1000"
                :step="1"
                class="w-full"
              />
            </div>
            <div class="form-group">
              <label class="label">换手率最小值 (%)</label>
              <el-input-number
                v-model="filterForm.min_turnover_rate"
                :min="0"
                :max="100"
                :step="0.5"
                class="w-full"
              />
            </div>
            <div class="form-group">
              <label class="label">净流入额最小值 (万元)</label>
              <el-input-number
                v-model="filterForm.min_net_mf_amount"
                :min="-1000000"
                :max="1000000"
                :step="1000"
                placeholder="不限制"
                class="w-full"
              />
            </div>
            <div class="form-group">
              <label class="label">结果数量</label>
              <el-select v-model="filterForm.mf_top_n" class="w-full">
                <el-option :value="10" label="前 10 只" />
                <el-option :value="20" label="前 20 只" />
                <el-option :value="30" label="前 30 只 (默认)" />
                <el-option :value="50" label="前 50 只" />
                <el-option :value="100" label="前 100 只" />
              </el-select>
            </div>
          </div>
          
          <div class="filter-actions">
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="loading"
            >
              <svg style="width: 18px; height: 18px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
              </svg>
              {{ loading ? '筛选中...' : '开始筛选' }}
            </button>
            <button
              type="button"
              class="btn btn-secondary"
              @click="resetForm"
            >
              <svg style="width: 18px; height: 18px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
              </svg>
              重置
            </button>
          </div>
        </form>
      </div>

      <!-- 结果展示 -->
      <div v-if="results.length > 0">
        <div class="result-header">
          <div class="result-count">
            找到 <strong>{{ results.length }}</strong> 只股票
          </div>
        </div>

        <div class="table-container">
          <table class="table">
            <thead>
              <tr>
                <th>股票代码</th>
                <th>股票名称</th>
                <th>收盘价</th>
                <th>涨跌幅</th>
                <th>流通市值</th>
                <th>市盈率</th>
                <th>换手率</th>
                <th>净流入额</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in results" :key="item.ts_code">
                <td><span class="stock-code">{{ item.ts_code }}</span></td>
                <td><span class="stock-name">{{ item.name }}</span></td>
                <td>{{ formatNumber(item.close) }}</td>
                <td :class="getPctColor(item.pct_chg)">{{ formatPct(item.pct_chg) }}</td>
                <td>{{ formatMV(item.circ_mv) }}亿</td>
                <td>{{ formatNumber(item.pe) }}</td>
                <td>{{ formatNumber(item.turnover_rate) }}%</td>
                <td :class="getMfColor(item.net_mf_amount)">{{ formatMfAmount(item.net_mf_amount) }}万</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else-if="searched" class="empty-state">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path>
        </svg>
        <h3 class="empty-state-title">暂无筛选结果</h3>
        <p class="empty-state-text">请设置筛选条件并点击"开始筛选"按钮</p>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { strategyApi, type DailyQuote } from '@/api/client'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const isAdmin = computed(() => authStore.isAdmin)
const userInitial = computed(() => authStore.userInitial)
const userName = computed(() => authStore.user?.nickname || '')

const handleLogout = async () => {
  if (confirm('确定要退出登录吗？')) {
    await authStore.logout()
    router.push('/login')
  }
}

const loading = ref(false)
const searched = ref(false)
const results = ref<DailyQuote[]>([])
const currentTradeDate = ref('')

const filterForm = reactive({
  trade_date: '',
  min_pct: -100,
  max_pct: 100,
  min_circ_mv_yi: 50,
  max_circ_mv_yi: null as number | null,
  min_pe: 0,
  max_pe: 50,
  min_turnover_rate: 5,
  max_turnover_rate: null as number | null,
  min_net_mf_amount: null as number | null,
  mf_top_n: 30,
})

const handleFilter = async () => {
  if (!filterForm.trade_date) {
    ElMessage.warning('请选择交易日期')
    return
  }

  loading.value = true
  searched.value = true

  try {
    const response = await strategyApi.stockFilter({
      trade_date: filterForm.trade_date,
      min_pct: filterForm.min_pct,
      max_pct: filterForm.max_pct,
      min_circ_mv: filterForm.min_circ_mv_yi * 10000,
      max_circ_mv: filterForm.max_circ_mv_yi ? filterForm.max_circ_mv_yi * 10000 : null,
      min_pe: filterForm.min_pe,
      max_pe: filterForm.max_pe,
      min_turnover_rate: filterForm.min_turnover_rate,
      max_turnover_rate: filterForm.max_turnover_rate,
      min_net_mf_amount: filterForm.min_net_mf_amount,
      mf_top_n: filterForm.mf_top_n,
    })
    results.value = response.data.data
    currentTradeDate.value = response.data.trade_date
    ElMessage.success(`筛选完成，共找到 ${response.data.count} 条记录`)
  } catch (error) {
    const err = error as Error
    ElMessage.error(err.message || '筛选失败')
    results.value = []
  } finally {
    loading.value = false
  }
}

const formatNumber = (val: number | null) => {
  if (val === null || val === undefined) return '-'
  return val.toFixed(2)
}

const formatPct = (val: number | null) => {
  if (val === null || val === undefined) return '-'
  const prefix = val > 0 ? '+' : ''
  return `${prefix}${val.toFixed(2)}%`
}

const getPctColor = (val: number | null) => {
  if (val === null || val === undefined) return 'text-gray-500'
  if (val > 0) return 'text-red-600'
  if (val < 0) return 'text-green-600'
  return 'text-gray-600'
}

const getMfColor = (val: number | null) => {
  if (val === null || val === undefined) return 'text-gray-500'
  if (val > 0) return 'text-red-600'
  if (val < 0) return 'text-green-600'
  return 'text-gray-600'
}

const formatMfAmount = (val: number | null) => {
  if (val === null || val === undefined) return '-'
  const prefix = val > 0 ? '+' : ''
  return `${prefix}${val.toFixed(2)}`
}

const formatMV = (val: number | null) => {
  if (val === null || val === undefined) return '-'
  return (val / 10000).toFixed(2)
}

const resetForm = () => {
  filterForm.trade_date = ''
  filterForm.min_pct = -100
  filterForm.max_pct = 100
  filterForm.min_circ_mv_yi = 50
  filterForm.max_circ_mv_yi = null
  filterForm.min_pe = 0
  filterForm.max_pe = 50
  filterForm.min_turnover_rate = 5
  filterForm.max_turnover_rate = null
  filterForm.min_net_mf_amount = null
  filterForm.mf_top_n = 30
  results.value = []
  searched.value = false
}
</script>
