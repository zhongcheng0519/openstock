<script setup lang="ts">
defineProps<{
  title: string
  buyVol: number | null
  buyAmount: number | null
  sellVol: number | null
  sellAmount: number | null
}>()

const formatVol = (val: number | null) => {
  if (val === null || val === undefined) return '-'
  return val.toFixed(0)
}

const formatAmount = (val: number | null) => {
  if (val === null || val === undefined) return '-'
  return val.toFixed(2)
}
</script>

<template>
  <div class="moneyflow-section">
    <h4 class="moneyflow-section-title">{{ title }}</h4>
    <div class="moneyflow-row">
      <div class="moneyflow-item buy">
        <span class="moneyflow-label">买入量</span>
        <span class="moneyflow-value">{{ formatVol(buyVol) }}手</span>
      </div>
      <div class="moneyflow-item buy">
        <span class="moneyflow-label">买入额</span>
        <span class="moneyflow-value">{{ formatAmount(buyAmount) }}万</span>
      </div>
      <div class="moneyflow-item sell">
        <span class="moneyflow-label">卖出量</span>
        <span class="moneyflow-value">{{ formatVol(sellVol) }}手</span>
      </div>
      <div class="moneyflow-item sell">
        <span class="moneyflow-label">卖出额</span>
        <span class="moneyflow-value">{{ formatAmount(sellAmount) }}万</span>
      </div>
    </div>
  </div>
</template>
