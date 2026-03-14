<template>
  <div class="min-h-screen bg-gray-50">
    <AppNavbar />

    <main class="max-w-[1200px] mx-auto px-6 py-8">
      <PageHeader
        :title="stockName || '股票详情'"
        :subtitle="`股票代码: ${tsCode}`"
      >
        <template #actions>
          <ActionButton
            v-if="isFavorited"
            type="button"
            variant="secondary"
            icon="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"
            @click="handleRemoveFavorite"
            :loading="favoriteLoading"
          >
            已加自选
          </ActionButton>
          <ActionButton
            v-else
            type="button"
            variant="primary"
            icon="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"
            @click="handleAddFavorite"
            :loading="favoriteLoading"
          >
            加自选
          </ActionButton>
          <ActionButton
            type="button"
            variant="secondary"
            icon="M10 19l-7-7m0 0l7-7m-7 7h18"
            @click="goBack"
          >
            返回列表
          </ActionButton>
        </template>
      </PageHeader>

      <div v-if="loading" class="flex justify-center py-12">
        <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      </div>

      <div v-else-if="detail">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div class="detail-card">
            <h3 class="detail-card-title">基本信息</h3>
            <div class="detail-grid">
              <DetailItem label="股票代码" :value="detail.ts_code" />
              <DetailItem label="股票名称" :value="detail.name || '-'" size-class="font-medium" />
              <DetailItem label="地域" :value="detail.area || '-'" />
              <DetailItem label="所属行业" :value="detail.industry || '-'" />
              <DetailItem label="交易日期" :value="detail.trade_date || '-'" />
            </div>
          </div>

          <div class="detail-card">
            <h3 class="detail-card-title">行情概览</h3>
            <div class="detail-grid">
              <DetailItem
                label="收盘价"
                :value="formatNumber(detail.close)"
                size-class="text-lg"
                :color-class="getStockColor(detail.pct_chg)"
              />
              <DetailItem
                label="涨跌幅"
                :value="formatPct(detail.pct_chg)"
                size-class="text-lg"
                :color-class="getStockColor(detail.pct_chg)"
              />
              <DetailItem label="流通市值" :value="`${formatMV(detail.circ_mv)}亿`" />
              <DetailItem label="市盈率" :value="formatNumber(detail.pe)" />
              <DetailItem label="换手率" :value="`${formatNumber(detail.turnover_rate)}%`" />
              <DetailItem
                label="成交量"
                :value="`${formatVol(detail.vol)}手`"
                :color-class="getStockColor(detail.pct_chg)"
              />
              <DetailItem label="内盘(主动卖)" :value="`${formatVol(detail.selling)}手`" />
              <DetailItem label="外盘(主动买)" :value="`${formatVol(detail.buying)}手`" />
            </div>
          </div>
        </div>

        <div class="detail-card">
          <h3 class="detail-card-title">历史行情 & 资金流向</h3>
          <div v-if="historyLoading" class="flex justify-center py-8">
            <el-icon class="is-loading" :size="24"><Loading /></el-icon>
          </div>
          <div v-else class="overflow-x-auto">
            <el-table
              :data="historyData"
              stripe
              size="small"
              :header-cell-style="{ whiteSpace: 'nowrap' }"
              :cell-style="{ whiteSpace: 'nowrap' }"
              table-layout="auto"
            >
              <el-table-column prop="trade_date" label="日期" width="100" fixed />
              <el-table-column label="开盘" width="80" align="right">
                <template #default="{ row }">{{ formatNumber(row.open) }}</template>
              </el-table-column>
              <el-table-column label="收盘" width="80" align="right">
                <template #default="{ row }">
                  <span :class="getStockColor(row.pct_chg)">{{ formatNumber(row.close) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="最高" width="80" align="right">
                <template #default="{ row }">{{ formatNumber(row.high) }}</template>
              </el-table-column>
              <el-table-column label="最低" width="80" align="right">
                <template #default="{ row }">{{ formatNumber(row.low) }}</template>
              </el-table-column>
              <el-table-column label="涨跌幅" width="85" align="right">
                <template #default="{ row }">
                  <span :class="getStockColor(row.pct_chg)">{{ formatPct(row.pct_chg) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="成交量(手)" width="105" align="right">
                <template #default="{ row }">{{ formatVol(row.vol) }}</template>
              </el-table-column>
              <el-table-column label="净流入额(万)" width="115" align="right">
                <template #default="{ row }">
                  <span :class="getStockColor(row.net_mf_amount)">{{ formatAmount(row.net_mf_amount) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="净流入量(手)" width="115" align="right">
                <template #default="{ row }">
                  <span :class="getStockColor(row.net_mf_vol)">{{ formatVol(row.net_mf_vol) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="小单买入(万)" width="115" align="right">
                <template #default="{ row }">{{ formatNumber(row.buy_sm_amount) }}</template>
              </el-table-column>
              <el-table-column label="小单卖出(万)" width="115" align="right">
                <template #default="{ row }">{{ formatNumber(row.sell_sm_amount) }}</template>
              </el-table-column>
              <el-table-column label="中单买入(万)" width="115" align="right">
                <template #default="{ row }">{{ formatNumber(row.buy_md_amount) }}</template>
              </el-table-column>
              <el-table-column label="中单卖出(万)" width="115" align="right">
                <template #default="{ row }">{{ formatNumber(row.sell_md_amount) }}</template>
              </el-table-column>
              <el-table-column label="大单买入(万)" width="115" align="right">
                <template #default="{ row }">{{ formatNumber(row.buy_lg_amount) }}</template>
              </el-table-column>
              <el-table-column label="大单卖出(万)" width="115" align="right">
                <template #default="{ row }">{{ formatNumber(row.sell_lg_amount) }}</template>
              </el-table-column>
              <el-table-column label="特大单买入(万)" width="130" align="right">
                <template #default="{ row }">{{ formatNumber(row.buy_elg_amount) }}</template>
              </el-table-column>
              <el-table-column label="特大单卖出(万)" width="130" align="right">
                <template #default="{ row }">{{ formatNumber(row.sell_elg_amount) }}</template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </div>

      <EmptyState
        v-else-if="!loading && error"
        title="加载失败"
        :description="error"
      />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { strategyApi, type StockDetailResponse, type StockHistoryItem } from '@/api/client'
import {
  getStockColor,
  formatStockNumber,
  formatStockPct,
  formatStockMV,
  formatStockVol,
  formatStockAmount,
} from '@/utils/stock'
import AppNavbar from '@/components/AppNavbar.vue'
import PageHeader from '@/components/PageHeader.vue'
import ActionButton from '@/components/ActionButton.vue'
import EmptyState from '@/components/EmptyState.vue'
import DetailItem from '@/components/DetailItem.vue'

const route = useRoute()
const router = useRouter()

const tsCode = computed(() => route.params.ts_code as string)
const tradeDate = computed(() => route.query.trade_date as string | undefined)

const loading = ref(false)
const detail = ref<StockDetailResponse | null>(null)
const error = ref('')
const isFavorited = ref(false)
const favoriteLoading = ref(false)
const historyLoading = ref(false)
const historyData = ref<StockHistoryItem[]>([])

const stockName = computed(() => detail.value?.name || '')

const loadStockData = async () => {
  if (!tsCode.value) {
    error.value = '股票代码不能为空'
    return
  }

  loading.value = true
  error.value = ''
  detail.value = null
  historyData.value = []
  try {
    const response = await strategyApi.getStockDetail(tsCode.value, tradeDate.value)
    detail.value = response.data
    await checkFavoriteStatus()
    fetchHistory()
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : '获取股票详情失败'
    error.value = message
    ElMessage.error(message)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadStockData()
})

const fetchHistory = async () => {
  historyLoading.value = true
  try {
    const response = await strategyApi.getStockHistory(tsCode.value)
    historyData.value = response.data.data
  } catch (err: unknown) {
    console.error('获取历史数据失败:', err)
  } finally {
    historyLoading.value = false
  }
}

const checkFavoriteStatus = async () => {
  try {
    const response = await strategyApi.checkFavoriteStatus(tsCode.value)
    isFavorited.value = response.data.is_favorited
  } catch (error) {
    console.error('检查自选股状态失败:', error)
  }
}

const handleAddFavorite = async () => {
  favoriteLoading.value = true
  try {
    await strategyApi.addFavorite(tsCode.value)
    ElMessage.success('添加成功')
    isFavorited.value = true
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : '添加失败'
    ElMessage.error(message)
  } finally {
    favoriteLoading.value = false
  }
}

const handleRemoveFavorite = async () => {
  favoriteLoading.value = true
  try {
    await strategyApi.removeFavorite(tsCode.value)
    ElMessage.success('删除成功')
    isFavorited.value = false
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : '删除失败'
    ElMessage.error(message)
  } finally {
    favoriteLoading.value = false
  }
}

const goBack = () => {
  router.push({ name: 'stock-filter' })
}

const formatNumber = (val: number | null) => formatStockNumber(val)
const formatPct = (val: number | null) => formatStockPct(val)
const formatMV = (val: number | null) => formatStockMV(val)
const formatVol = (val: number | null) => formatStockVol(val)
const formatAmount = (val: number | null) => formatStockAmount(val)
</script>

<style scoped>
</style>
