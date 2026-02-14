<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 头部 -->
    <header class="bg-white shadow-sm border-b">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <el-icon class="text-blue-600 text-2xl"><TrendCharts /></el-icon>
            <h1 class="text-xl font-bold text-gray-900">股票分析系统</h1>
          </div>
          <div class="flex items-center gap-4">
            <el-button
              type="primary"
              :loading="syncingStocks"
              @click="handleSyncStocks"
            >
              <el-icon class="mr-1"><Refresh /></el-icon>
              同步股票列表
            </el-button>
          </div>
        </div>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <!-- 筛选条件卡片 -->
      <div class="bg-white rounded-lg shadow p-6 mb-6">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">涨跌幅筛选</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
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
            <el-table-column prop="pct_chg" label="涨跌幅" width="120" sortable>
              <template #default="{ row }">
                <span :class="getPctColor(row.pct_chg)">
                  {{ formatPct(row.pct_chg) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="change" label="涨跌额" width="100">
              <template #default="{ row }">
                <span :class="getPctColor(row.change)">
                  {{ formatNumber(row.change) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="open" label="开盘价" width="100">
              <template #default="{ row }">
                {{ formatNumber(row.open) }}
              </template>
            </el-table-column>
            <el-table-column prop="high" label="最高价" width="100">
              <template #default="{ row }">
                {{ formatNumber(row.high) }}
              </template>
            </el-table-column>
            <el-table-column prop="low" label="最低价" width="100">
              <template #default="{ row }">
                {{ formatNumber(row.low) }}
              </template>
            </el-table-column>
            <el-table-column prop="vol" label="成交量(手)" width="150">
              <template #default="{ row }">
                {{ formatVolume(row.vol) }}
              </template>
            </el-table-column>
            <el-table-column prop="amount" label="成交额(千元)" width="150">
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
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { strategyApi, type DailyQuote } from '@/api/client'

const loading = ref(false)
const syncingStocks = ref(false)
const searched = ref(false)
const results = ref<DailyQuote[]>([])
const currentTradeDate = ref('')
const expandedItems = ref<string[]>([])

const filterForm = reactive({
  trade_date: '',
  min_pct: -2,
  max_pct: 5,
})

const handleFilter = async () => {
  if (!filterForm.trade_date) {
    ElMessage.warning('请选择交易日期')
    return
  }

  loading.value = true
  searched.value = true

  try {
    const response = await strategyApi.pctFilter({
      trade_date: filterForm.trade_date,
      min_pct: filterForm.min_pct,
      max_pct: filterForm.max_pct,
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

const formatVolume = (val: number | null) => {
  if (val === null || val === undefined) return '-'
  if (val >= 10000) {
    return (val / 10000).toFixed(2) + '万'
  }
  return val.toFixed(0)
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}
</script>
