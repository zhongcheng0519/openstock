<template>
  <div class="min-h-screen bg-gray-50">
    <AppNavbar />

    <main class="max-w-[1200px] mx-auto px-6 py-8">
      <PageHeader title="条件选股" subtitle="使用多种策略筛选符合投资条件的股票" />

      <el-tabs v-model="activeTab" class="strategy-tabs">
        <el-tab-pane label="组合策略" name="combo">
          <ComboStrategyPanel />
        </el-tab-pane>
        <el-tab-pane label="首板策略" name="first-limit">
          <FirstLimitPanel />
        </el-tab-pane>
      </el-tabs>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import AppNavbar from '@/components/AppNavbar.vue'
import PageHeader from '@/components/PageHeader.vue'
import ComboStrategyPanel from '@/components/ComboStrategyPanel.vue'
import FirstLimitPanel from '@/components/FirstLimitPanel.vue'

const activeTab = ref('combo')
</script>

<style scoped>
.strategy-tabs :deep(.el-tabs__header) {
  margin-bottom: 1.5rem;
}

.strategy-tabs :deep(.el-tabs__item) {
  font-size: 0.9375rem;
  font-weight: 500;
}

.strategy-tabs :deep(.el-tabs__item.is-active) {
  color: var(--primary);
}

.strategy-tabs :deep(.el-tabs__active-bar) {
  background-color: var(--primary);
}
</style>
