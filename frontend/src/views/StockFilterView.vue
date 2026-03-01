<template>
  <div class="min-h-screen bg-gray-50">
    <AppNavbar />

    <!-- 主内容区 -->
    <main class="max-w-[1200px] mx-auto px-6 py-8">
      <PageHeader title="股票筛选" subtitle="根据多维度条件筛选符合投资策略的股票" />
      
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
              <label class="label">成交量倍数 (倍)</label>
              <el-input-number
                v-model="filterForm.vol_ratio"
                :min="1"
                :max="20"
                :step="0.5"
                :precision="1"
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
              <th>收盘价</th>
              <th>涨跌幅</th>
              <th>流通市值</th>
              <th>市盈率</th>
              <th>换手率</th>
              <th>净流入额</th>
            </tr>
          </template>
            <tr v-for="item in results" :key="item.ts_code">
              <td>
                <router-link
                  :to="{ name: 'stock-detail', params: { ts_code: item.ts_code }, query: { trade_date: currentTradeDate } }"
                  class="stock-code-link"
                >
                  {{ item.ts_code }}
                </router-link>
              </td>
              <td><span class="stock-name">{{ item.name }}</span></td>
            <td><span :class="getPctColor(item.pct_chg)">{{ formatNumber(item.close) }}</span></td>
            <td><span :class="getPctColor(item.pct_chg)">{{ formatPct(item.pct_chg) }}</span></td>
            <td>{{ formatMV(item.circ_mv) }}亿</td>
            <td>{{ formatNumber(item.pe) }}</td>
            <td>{{ formatNumber(item.turnover_rate) }}%</td>
            <td :class="getMfColor(item.net_mf_amount)">{{ formatMfAmount(item.net_mf_amount) }}万</td>
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
import { strategyApi, type DailyQuote } from '@/api/client'
import AppNavbar from '@/components/AppNavbar.vue'
import PageHeader from '@/components/PageHeader.vue'
import ActionButton from '@/components/ActionButton.vue'
import DataTable from '@/components/DataTable.vue'
import EmptyState from '@/components/EmptyState.vue'

const loading = ref(false)
const searched = ref(false)
const results = ref<DailyQuote[]>([])
const currentTradeDate = ref('')

const filterForm = reactive({
  trade_date: '',
  min_pct: 2,
  max_pct: 5,
  min_circ_mv_yi: 50,
  max_circ_mv_yi: null as number | null,
  min_pe: 0,
  max_pe: 50,
  min_turnover_rate: 5,
  max_turnover_rate: null as number | null,
  min_net_mf_amount: null as number | null,
  vol_ratio: null as number | null,
  mf_top_n: 30,
})

onMounted(async () => {
  try {
    const response = await strategyApi.getLatestTradeDate()
    filterForm.trade_date = response.data.trade_date
  } catch (error) {
    console.error('获取最新交易日失败:', error)
  }
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
      vol_ratio: filterForm.vol_ratio,
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
  return 'text-black'
}

const getMfColor = (val: number | null) => {
  if (val === null || val === undefined) return 'text-gray-500'
  if (val > 0) return 'text-red-600'
  if (val < 0) return 'text-green-600'
  return 'text-black'
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
  filterForm.min_pct = 2
  filterForm.max_pct = 5
  filterForm.min_circ_mv_yi = 50
  filterForm.max_circ_mv_yi = null
  filterForm.min_pe = 0
  filterForm.max_pe = 50
  filterForm.min_turnover_rate = 5
  filterForm.max_turnover_rate = null
  filterForm.min_net_mf_amount = null
  filterForm.vol_ratio = null
  filterForm.mf_top_n = 30
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
    '收盘价': item.close,
    '涨跌幅': item.pct_chg,
    '流通市值(亿)': item.circ_mv ? (item.circ_mv / 10000).toFixed(2) : '-',
    '市盈率': item.pe,
    '换手率(%)': item.turnover_rate,
    '净流入额(万)': item.net_mf_amount,
  }))

  const ws = XLSX.utils.json_to_sheet(exportData)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '条件选股')

  const fileName = `条件选股_${filterForm.trade_date}.xlsx`
  XLSX.writeFile(wb, fileName)
  ElMessage.success('导出成功')
}
</script>
