<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <router-link to="/" class="flex items-center gap-3">
              <div class="w-9 h-9 bg-gradient-to-br from-red-600 to-red-500 rounded-lg flex items-center justify-center">
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
                </svg>
              </div>
              <span class="text-xl font-bold text-gray-900">股票分析系统</span>
            </router-link>
          </div>
          
          <div class="flex items-center gap-4">
            <router-link to="/" class="px-3 py-2 text-sm font-medium text-red-600 bg-red-50 rounded-lg">
              股票筛选
            </router-link>
            <router-link to="/profile" class="px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
              个人中心
            </router-link>
            <template v-if="isAdmin">
              <router-link to="/users" class="px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
                用户管理
              </router-link>
              <router-link to="/logs" class="px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
                操作日志
              </router-link>
            </template>
            
            <div class="flex items-center gap-3 pl-4 border-l border-gray-200">
              <div class="w-8 h-8 bg-gradient-to-br from-red-600 to-red-500 rounded-full flex items-center justify-center text-white font-medium text-sm">
                {{ userInitial }}
              </div>
              <span class="text-sm font-medium text-gray-900">{{ userName }}</span>
              <button @click="handleLogout" class="px-3 py-1.5 text-sm text-gray-600 hover:text-gray-900 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                退出
              </button>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <!-- 主内容区 -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <!-- 筛选条件卡片 -->
      <div class="bg-white rounded-lg shadow p-6 mb-6">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">多条件筛选</h2>
        
        <!-- 第一行：日期和涨跌幅 -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">交易日期</label>
            <el-date-picker
              v-model="filterForm.trade_date"
              type="date"
              placeholder="选择日期"
              format="YYYY-MM-DD"
              value-format="YYYYMMDD"
              class="w-full"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">最小涨跌幅 (%)</label>
            <el-input-number
              v-model="filterForm.min_pct"
              :min="-20"
              :max="20"
              :step="0.1"
              class="w-full"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">最大涨跌幅 (%)</label>
            <el-input-number
              v-model="filterForm.max_pct"
              :min="-20"
              :max="20"
              :step="0.1"
              class="w-full"
            />
          </div>
        </div>
        
        <!-- 第二行：流通市值 -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">最小流通市值 (亿元)</label>
            <el-input-number
              v-model="filterForm.min_circ_mv_yi"
              :min="0"
              :max="100000"
              :step="10"
              class="w-full"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">最大流通市值 (亿元)</label>
            <el-input-number
              v-model="filterForm.max_circ_mv_yi"
              :min="0"
              :max="100000"
              :step="10"
              :placeholder="'不限制'"
              class="w-full"
            />
          </div>
        </div>
        
        <!-- 第三行：市盈率和换手率 -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">最小市盈率</label>
            <el-input-number
              v-model="filterForm.min_pe"
              :min="0"
              :max="1000"
              :step="1"
              class="w-full"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">最大市盈率</label>
            <el-input-number
              v-model="filterForm.max_pe"
              :min="0"
              :max="1000"
              :step="1"
              class="w-full"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">最小换手率 (%)</label>
            <el-input-number
              v-model="filterForm.min_turnover_rate"
              :min="0"
              :max="100"
              :step="0.5"
              class="w-full"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">最大换手率 (%)</label>
            <el-input-number
              v-model="filterForm.max_turnover_rate"
              :min="0"
              :max="100"
              :step="0.5"
              :placeholder="'不限制'"
              class="w-full"
            />
          </div>
        </div>
        
        <!-- 第四行：资金流向筛选 -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">最小净流入额 (万元)</label>
            <el-input-number
              v-model="filterForm.min_net_mf_amount"
              :min="-1000000"
              :max="1000000"
              :step="1000"
              :placeholder="'不限制'"
              class="w-full"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">返回数量 (按净流入额排名)</label>
            <el-select v-model="filterForm.mf_top_n" class="w-full">
              <el-option :value="10" label="前 10 只" />
              <el-option :value="20" label="前 20 只" />
              <el-option :value="30" label="前 30 只 (默认)" />
              <el-option :value="50" label="前 50 只" />
              <el-option :value="100" label="前 100 只" />
            </el-select>
          </div>
        </div>
        
        <div class="mt-4 flex justify-end">
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleFilter"
          >
            <el-icon class="mr-1"><Search /></el-icon>
            开始筛选
          </el-button>
        </div>
      </div>

      <!-- 结果展示 -->
      <div v-if="results.length > 0" class="bg-white rounded-lg shadow">
        <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h3 class="text-lg font-semibold text-gray-800">
            筛选结果
            <el-tag type="info" class="ml-2">共 {{ results.length }} 条</el-tag>
          </h3>
          <div class="text-sm text-gray-500">
            交易日期: {{ formatDate(currentTradeDate) }}
          </div>
        </div>

        <!-- 桌面端表格 -->
        <div class="hidden md:block overflow-x-auto">
          <el-table
            :data="results"
            stripe
            style="width: 100%"
            :default-sort="{ prop: 'pct_chg', order: 'descending' }"
          >
            <el-table-column prop="ts_code" label="股票代码" width="120" />
            <el-table-column prop="name" label="股票名称" width="120" />
            <el-table-column prop="close" label="收盘价" width="100">
              <template #default="{ row }">
                {{ formatNumber(row.close) }}
              </template>
            </el-table-column>
            <el-table-column prop="pct_chg" label="涨跌幅" width="100" sortable>
              <template #default="{ row }">
                <span :class="getPctColor(row.pct_chg)">
                  {{ formatPct(row.pct_chg) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="circ_mv" label="流通市值(亿)" width="120" sortable>
              <template #default="{ row }">
                {{ formatMV(row.circ_mv) }}
              </template>
            </el-table-column>
            <el-table-column prop="pe" label="市盈率" width="100" sortable>
              <template #default="{ row }">
                {{ formatNumber(row.pe) }}
              </template>
            </el-table-column>
            <el-table-column prop="turnover_rate" label="换手率(%)" width="100" sortable>
              <template #default="{ row }">
                {{ formatNumber(row.turnover_rate) }}
              </template>
            </el-table-column>
            <el-table-column prop="net_mf_amount" label="净流入额(万)" width="120" sortable>
              <template #default="{ row }">
                <span :class="getMfColor(row.net_mf_amount)">
                  {{ formatMfAmount(row.net_mf_amount) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="vol" label="成交量(手)" width="120">
              <template #default="{ row }">
                {{ formatVolume(row.vol) }}
              </template>
            </el-table-column>
            <el-table-column prop="amount" label="成交额(千元)" width="120">
              <template #default="{ row }">
                {{ formatVolume(row.amount) }}
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 移动端卡片 -->
        <div class="md:hidden divide-y divide-gray-200">
          <div
            v-for="item in results"
            :key="item.ts_code"
            class="p-4 hover:bg-gray-50"
            @click="toggleExpand(item.ts_code)"
          >
            <div class="flex items-center justify-between">
              <div>
                <div class="font-medium text-gray-900">{{ item.name }}</div>
                <div class="text-sm text-gray-500">{{ item.ts_code }}</div>
              </div>
              <div class="text-right">
                <div class="font-semibold" :class="getPctColor(item.pct_chg)">
                  {{ formatPct(item.pct_chg) }}
                </div>
                <div class="text-sm text-gray-600">
                  ¥{{ formatNumber(item.close) }}
                </div>
              </div>
            </div>
            <!-- 展开详情 -->
            <div v-if="expandedItems.includes(item.ts_code)" class="mt-3 pt-3 border-t border-gray-100">
              <div class="grid grid-cols-2 gap-2 text-sm">
                <div class="text-gray-500">流通市值: <span class="text-gray-900">{{ formatMV(item.circ_mv) }}亿</span></div>
                <div class="text-gray-500">市盈率: <span class="text-gray-900">{{ formatNumber(item.pe) }}</span></div>
                <div class="text-gray-500">换手率: <span class="text-gray-900">{{ formatNumber(item.turnover_rate) }}%</span></div>
                <div class="text-gray-500">净流入额: <span :class="getMfColor(item.net_mf_amount)">{{ formatMfAmount(item.net_mf_amount) }}万</span></div>
                <div class="text-gray-500">开盘价: <span class="text-gray-900">{{ formatNumber(item.open) }}</span></div>
                <div class="text-gray-500">最高价: <span class="text-gray-900">{{ formatNumber(item.high) }}</span></div>
                <div class="text-gray-500">最低价: <span class="text-gray-900">{{ formatNumber(item.low) }}</span></div>
                <div class="text-gray-500">昨收: <span class="text-gray-900">{{ formatNumber(item.pre_close) }}</span></div>
                <div class="text-gray-500">涨跌额: <span :class="getPctColor(item.change)">{{ formatNumber(item.change) }}</span></div>
                <div class="text-gray-500">成交量: <span class="text-gray-900">{{ formatVolume(item.vol) }}</span></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else-if="searched" class="bg-white rounded-lg shadow p-12 text-center">
        <el-icon class="text-6xl text-gray-300 mb-4"><Search /></el-icon>
        <p class="text-gray-500">暂无符合条件的数据</p>
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
const syncingStocks = ref(false)
const searched = ref(false)
const results = ref<DailyQuote[]>([])
const currentTradeDate = ref('')
const expandedItems = ref<string[]>([])

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
  } catch (error: any) {
    ElMessage.error(error.message || '筛选失败')
    results.value = []
  } finally {
    loading.value = false
  }
}

const handleSyncStocks = async () => {
  syncingStocks.value = true
  try {
    const response = await strategyApi.syncStocks()
    ElMessage.success(response.data.message)
  } catch (error: any) {
    ElMessage.error(error.message || '同步失败')
  } finally {
    syncingStocks.value = false
  }
}

const toggleExpand = (tsCode: string) => {
  const index = expandedItems.value.indexOf(tsCode)
  if (index > -1) {
    expandedItems.value.splice(index, 1)
  } else {
    expandedItems.value.push(tsCode)
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

const formatVolume = (val: number | null) => {
  if (val === null || val === undefined) return '-'
  if (val >= 10000) {
    return (val / 10000).toFixed(2) + '万'
  }
  return val.toFixed(0)
}

const formatMV = (val: number | null) => {
  if (val === null || val === undefined) return '-'
  return (val / 10000).toFixed(2)
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}
</script>
