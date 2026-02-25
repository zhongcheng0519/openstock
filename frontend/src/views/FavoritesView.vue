<template>
  <div class="min-h-screen bg-gray-50">
    <AppNavbar />

    <main class="max-w-[1200px] mx-auto px-6 py-8">
      <PageHeader title="自选股" subtitle="管理您的自选股票" />

      <div class="mb-6">
        <el-autocomplete
          v-model="searchQuery"
          :fetch-suggestions="querySearch"
          placeholder="输入股票代码或名称搜索添加"
          :trigger-on-focus="false"
          clearable
          class="w-full max-w-md"
          @select="handleSelectStock"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
          <template #default="{ item }">
            <div class="flex justify-between items-center">
              <span>{{ item.ts_code }}</span>
              <span class="text-gray-500">{{ item.name }}</span>
            </div>
          </template>
        </el-autocomplete>
      </div>

      <div v-if="loading" class="flex justify-center py-12">
        <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      </div>

      <div v-else-if="favorites.length > 0">
        <div class="result-header">
          <div class="result-count">
            共 <strong>{{ favorites.length }}</strong> 只自选股
          </div>
        </div>

        <DataTable :loading="false" :empty="false">
          <template #header>
            <tr>
              <th>股票代码</th>
              <th>股票名称</th>
              <th>添加时间</th>
              <th>操作</th>
            </tr>
          </template>
          <tr v-for="item in favorites" :key="item.ts_code">
            <td>
              <router-link
                :to="{ name: 'stock-detail', params: { ts_code: item.ts_code }, query: { trade_date: currentTradeDate } }"
                class="stock-code-link"
              >
                {{ item.ts_code }}
              </router-link>
            </td>
            <td><span class="stock-name">{{ item.stock_name || '-' }}</span></td>
            <td>{{ formatDate(item.created_at) }}</td>
            <td>
              <button
                @click="handleRemove(item.ts_code)"
                class="text-red-600 hover:text-red-800 text-sm"
              >
                删除
              </button>
            </td>
          </tr>
        </DataTable>
      </div>

      <EmptyState
        v-else
        title="暂无自选股"
        description="从股票筛选页面添加自选股"
      />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Loading, Search } from '@element-plus/icons-vue'
import { strategyApi, type FavoriteStock, type StockSearchItem } from '@/api/client'
import AppNavbar from '@/components/AppNavbar.vue'
import PageHeader from '@/components/PageHeader.vue'
import DataTable from '@/components/DataTable.vue'
import EmptyState from '@/components/EmptyState.vue'

const loading = ref(false)
const favorites = ref<FavoriteStock[]>([])
const currentTradeDate = ref('')
const searchQuery = ref('')

onMounted(async () => {
  await fetchLatestTradeDate()
  await fetchFavorites()
})

const fetchLatestTradeDate = async () => {
  try {
    const response = await strategyApi.getLatestTradeDate()
    currentTradeDate.value = response.data.trade_date
  } catch (error) {
    console.error('获取最新交易日失败:', error)
  }
}

const fetchFavorites = async () => {
  loading.value = true
  try {
    const response = await strategyApi.getFavorites()
    favorites.value = response.data.items
  } catch (error: unknown) {
    const err = error as Error
    ElMessage.error(err.message || '获取自选股失败')
  } finally {
    loading.value = false
  }
}

const handleRemove = async (tsCode: string) => {
  try {
    await ElMessageBox.confirm('确定要从自选股中删除该股票吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    await strategyApi.removeFavorite(tsCode)
    ElMessage.success('删除成功')
    await fetchFavorites()
  } catch (error) {
    if (error !== 'cancel') {
      const err = error as Error
      ElMessage.error(err.message || '删除失败')
    }
  }
}

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

const querySearch = async (queryString: string, cb: (results: StockSearchItem[]) => void) => {
  if (!queryString) {
    cb([])
    return
  }
  try {
    const response = await strategyApi.searchStocks(queryString)
    cb(response.data)
  } catch {
    cb([])
  }
}

const handleSelectStock = async (item: StockSearchItem) => {
  try {
    await strategyApi.addFavorite(item.ts_code)
    ElMessage.success(`已添加 ${item.name} 到自选股`)
    searchQuery.value = ''
    await fetchFavorites()
  } catch (error: unknown) {
    const err = error as Error
    ElMessage.error(err.message || '添加自选股失败')
  }
}
</script>
