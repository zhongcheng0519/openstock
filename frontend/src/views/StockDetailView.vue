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
            </div>
          </div>
        </div>

        <div class="detail-card mb-6">
          <h3 class="detail-card-title">资金流向</h3>
          <div class="detail-grid">
            <DetailItem
              label="净流入额"
              :value="`${formatAmount(detail.net_mf_amount)}万`"
              size-class="text-lg"
              :color-class="getStockColor(detail.net_mf_amount)"
            />
            <DetailItem
              label="净流入量"
              :value="`${formatVol(detail.net_mf_vol)}手`"
              :color-class="getStockColor(detail.net_mf_vol)"
            />
          </div>
        </div>

        <div class="detail-card">
          <h3 class="detail-card-title">单笔成交明细</h3>
          <div class="moneyflow-grid">
            <MoneyflowSection
              title="小单 (≤10000股)"
              :buy-vol="detail.buy_sm_vol"
              :buy-amount="detail.buy_sm_amount"
              :sell-vol="detail.sell_sm_vol"
              :sell-amount="detail.sell_sm_amount"
            />
            <MoneyflowSection
              title="中单 (10001-50000股)"
              :buy-vol="detail.buy_md_vol"
              :buy-amount="detail.buy_md_amount"
              :sell-vol="detail.sell_md_vol"
              :sell-amount="detail.sell_md_amount"
            />
            <MoneyflowSection
              title="大单 (50001-100000股)"
              :buy-vol="detail.buy_lg_vol"
              :buy-amount="detail.buy_lg_amount"
              :sell-vol="detail.sell_lg_vol"
              :sell-amount="detail.sell_lg_amount"
            />
            <MoneyflowSection
              title="特大单 (>100000股)"
              :buy-vol="detail.buy_elg_vol"
              :buy-amount="detail.buy_elg_amount"
              :sell-vol="detail.sell_elg_vol"
              :sell-amount="detail.sell_elg_amount"
            />
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
import { strategyApi, type StockDetailResponse } from '@/api/client'
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
import MoneyflowSection from '@/components/MoneyflowSection.vue'

const route = useRoute()
const router = useRouter()

const tsCode = computed(() => route.params.ts_code as string)
const tradeDate = computed(() => route.query.trade_date as string | undefined)

const loading = ref(false)
const detail = ref<StockDetailResponse | null>(null)
const error = ref('')

const stockName = computed(() => detail.value?.name || '')

onMounted(async () => {
  if (!tsCode.value) {
    error.value = '股票代码不能为空'
    return
  }

  loading.value = true
  try {
    const response = await strategyApi.getStockDetail(tsCode.value, tradeDate.value)
    detail.value = response.data
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : '获取股票详情失败'
    error.value = message
    ElMessage.error(message)
  } finally {
    loading.value = false
  }
})

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
