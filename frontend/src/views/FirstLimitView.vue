<template>
  <div class="min-h-screen bg-gray-50">
    <AppNavbar />

    <!-- 主内容区 -->
    <main class="max-w-[1200px] mx-auto px-6 py-8">
      <PageHeader title="首板选股" subtitle="筛选指定时间范围内首次出现涨停的股票" />
      
      <!-- 筛选条件卡片 -->
      <div class="filter-card">
        <form @submit.prevent="handleFilter">
          <div class="filter-grid">
            <div class="form-group">
              <label class="label label-required">起始时间</label>
              <el-date-picker
                v-model="filterForm.start_date"
                type="date"
                placeholder="选择日期"
                format="YYYY-MM-DD"
                value-format="YYYYMMDD"
                class="w-full"
              />
            </div>
            <div class="form-group">
              <label class="label label-required">终止时间</label>
              <el-date-picker
                v-model="filterForm.end_date"
                type="date"
                placeholder="选择日期"
                format="YYYY-MM-DD"
                value-format="YYYYMMDD"
                class="w-full"
              />
            </div>
            <div class="form-group">
              <label class="label">出现过x次涨停</label>
              <el-input-number
                v-model="filterForm.limit_count"
                :min="1"
                :max="10"
                :step="1"
                class="w-full"
              />
            </div>
          </div>
          
          <div class="filter-actions">
            <ActionButton
              type="submit"
              variant="primary"
              :loading="loading"
              icon="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            >
              {{ loading ? '筛选中...' : '开始筛选' }}
            </ActionButton>
            <ActionButton
              type="button"
              variant="secondary"
              icon="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              @click="resetForm"
            >
              重置
            </ActionButton>
          </div>
        </form>
      </div>

      <!-- 结果展示 -->
      <div v-if="results.length > 0">
        <div class="result-header">
          <div class="result-count">
            找到 <strong>{{ results.length }}</strong> 只股票
          </div>
          <ActionButton
            type="button"
            variant="secondary"
            icon="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            @click="handleExport"
          >
            导出 Excel
          </ActionButton>
        </div>

        <DataTable :loading="false" :empty="false">
          <template #header>
            <tr>
              <th>股票代码</th>
              <th>股票名称</th>
              <th>首次涨停日期</th>
              <th>收盘价</th>
              <th>涨跌幅</th>
              <th>流通市值</th>
              <th>市盈率</th>
              <th>换手率</th>
            </tr>
          </template>
            <tr v-for="item in results" :key="item.ts_code">
              <td>
                <router-link
                  :to="{ name: 'stock-detail', params: { ts_code: item.ts_code }, query: { trade_date: formatDate(item.trade_date) } }"
                  class="stock-code-link"
                >
                  {{ item.ts_code }}
                </router-link>
              </td>
              <td><span class="stock-name">{{ item.name }}</span></td>
              <td><span class="text-gray-700">{{ formatDate(item.first_limit_date) }}</span></td>
            <td><span :class="getPctColor(item.pct_chg)">{{ formatNumber(item.close) }}</span></td>
            <td><span :class="getPctColor(item.pct_chg)">{{ formatPct(item.pct_chg) }}</span></td>
            <td>{{ formatMV(item.circ_mv) }}亿</td>
            <td>{{ formatNumber(item.pe) }}</td>
            <td>{{ formatNumber(item.turnover_rate) }}%</td>
          </tr>
        </DataTable>
      </div>

      <!-- 空状态 -->
      <EmptyState
        v-else-if="searched"
        title="暂无筛选结果"
        description="请设置筛选条件并点击开始筛选按钮"
      />
    </main>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import * as XLSX from 'xlsx'
import { strategyApi, type FirstLimitStock } from '@/api/client'
import AppNavbar from '@/components/AppNavbar.vue'
import PageHeader from '@/components/PageHeader.vue'
import ActionButton from '@/components/ActionButton.vue'
import DataTable from '@/components/DataTable.vue'
import EmptyState from '@/components/EmptyState.vue'

const loading = ref(false)
const searched = ref(false)
const results = ref<FirstLimitStock[]>([])

const getDefaultStartDate = () => {
  const now = new Date()
  return `${now.getFullYear()}0101`
}

const getDefaultEndDate = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  return `${year}${month}${day}`
}

const filterForm = reactive({
  start_date: getDefaultStartDate(),
  end_date: getDefaultEndDate(),
  limit_count: 1,
})

onMounted(async () => {
  try {
    const response = await strategyApi.getLatestTradeDate()
    filterForm.end_date = response.data.trade_date
    filterForm.start_date = `${response.data.trade_date.substring(0, 4)}0101`
  } catch (error) {
    console.error('获取最新交易日失败:', error)
  }
})

const handleFilter = async () => {
  if (!filterForm.start_date) {
    ElMessage.warning('请选择起始时间')
    return
  }
  if (!filterForm.end_date) {
    ElMessage.warning('请选择终止时间')
    return
  }
  if (filterForm.start_date > filterForm.end_date) {
    ElMessage.warning('起始时间不能晚于终止时间')
    return
  }

  loading.value = true
  searched.value = true

  try {
    const response = await strategyApi.firstLimitFilter({
      start_date: filterForm.start_date,
      end_date: filterForm.end_date,
      limit_count: filterForm.limit_count,
    })
    results.value = response.data.data
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
  return 'text-black'
}

const formatMV = (val: number | null) => {
  if (val === null || val === undefined) return '-'
  return (val / 10000).toFixed(2)
}

const formatDate = (val: string | null) => {
  if (!val) return '-'
  // Backend returns ISO date format YYYY-MM-DD from Pydantic
  if (typeof val === 'string' && val.includes('-')) return val.substring(0, 10)
  // Handle YYYYMMDD format
  if (typeof val === 'string' && val.length >= 8) {
    return `${val.substring(0, 4)}-${val.substring(4, 6)}-${val.substring(6, 8)}`
  }
  return String(val)
}

const resetForm = () => {
  const now = new Date()
  filterForm.start_date = `${now.getFullYear()}0101`
  filterForm.end_date = getDefaultEndDate()
  filterForm.limit_count = 1
  results.value = []
  searched.value = false
}

const handleExport = () => {
  if (results.value.length === 0) {
    ElMessage.warning('没有数据可导出')
    return
  }

  const exportData = results.value.map((item) => ({
    '股票代码': item.ts_code,
    '股票名称': item.name,
    '首次涨停日期': formatDate(item.first_limit_date),
    '收盘价': item.close,
    '涨跌幅': item.pct_chg,
    '流通市值(亿)': item.circ_mv ? (item.circ_mv / 10000).toFixed(2) : '-',
    '市盈率': item.pe,
    '换手率(%)': item.turnover_rate,
  }))

  const ws = XLSX.utils.json_to_sheet(exportData)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '首板选股')

  const fileName = `首板选股_${filterForm.start_date}_${filterForm.end_date}.xlsx`
  XLSX.writeFile(wb, fileName)
  ElMessage.success('导出成功')
}
</script>
