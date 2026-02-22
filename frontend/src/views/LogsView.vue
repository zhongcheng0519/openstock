<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { adminApi, type UserLogResponse, type LogStatisticsResponse } from '@/api/client'
import AppNavbar from '@/components/AppNavbar.vue'
import PageHeader from '@/components/PageHeader.vue'
import StatsCard from '@/components/StatsCard.vue'
import FormField from '@/components/FormField.vue'
import FormSelect from '@/components/FormSelect.vue'
import ActionButton from '@/components/ActionButton.vue'
import DataTable from '@/components/DataTable.vue'
import Badge from '@/components/Badge.vue'

const router = useRouter()
const authStore = useAuthStore()

const logs = ref<UserLogResponse[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(50)
const loading = ref(false)

const stats = ref<LogStatisticsResponse | null>(null)

const filterForm = ref({
  user_id: '',
  action: '',
  start_date: '',
  end_date: ''
})

function getActionBadgeClass(action: string): 'success' | 'danger' | 'warning' | 'info' | 'gray' {
  const actionMap: Record<string, 'success' | 'danger' | 'warning' | 'info' | 'gray'> = {
    'login': 'info',
    'logout': 'gray',
    'register': 'success',
    'filter': 'success',
    'user_create': 'danger',
    'user_update': 'danger',
    'user_delete': 'danger',
    'password_change': 'warning',
    'password_reset': 'warning',
  }
  return actionMap[action] || 'gray'
}

function getActionText(action: string) {
  const actionMap: Record<string, string> = {
    'login': '登录',
    'logout': '登出',
    'register': '注册',
    'filter': '股票筛选',
    'user_create': '创建用户',
    'user_update': '更新用户',
    'user_delete': '删除用户',
    'password_change': '修改密码',
    'password_reset': '重置密码',
    'list_users': '查看用户列表',
    'list_logs': '查看日志',
    'log_statistics': '日志统计',
    'profile_update': '更新资料',
  }
  return actionMap[action] || action
}

function getStatusBadgeClass(status: number | null): 'success' | 'danger' | 'warning' | 'gray' {
  if (!status) return 'gray'
  if (status >= 200 && status < 300) return 'success'
  if (status >= 400 && status < 500) return 'warning'
  return 'danger'
}

const actionOptions = [
  { value: '', label: '全部操作' },
  { value: 'login', label: '登录' },
  { value: 'logout', label: '登出' },
  { value: 'filter', label: '股票筛选' },
  { value: 'user_create', label: '创建用户' },
  { value: 'user_update', label: '更新用户' },
  { value: 'user_delete', label: '删除用户' },
]

async function loadLogs() {
  loading.value = true
  try {
    const params: Record<string, unknown> = { page: page.value, page_size: pageSize.value }
    if (filterForm.value.user_id) params.user_id = parseInt(filterForm.value.user_id)
    if (filterForm.value.action) params.action = filterForm.value.action
    if (filterForm.value.start_date) params.start_date = filterForm.value.start_date
    if (filterForm.value.end_date) params.end_date = filterForm.value.end_date
    
    const response = await adminApi.getLogs(params)
    logs.value = response.data.items
    total.value = response.data.total
  } catch (error) {
    console.error('Failed to load logs:', error)
  } finally {
    loading.value = false
  }
}

async function loadStats() {
  try {
    const response = await adminApi.getLogStatistics()
    stats.value = response.data
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

function handleFilter() {
  page.value = 1
  loadLogs()
}

function handleReset() {
  filterForm.value = { user_id: '', action: '', start_date: '', end_date: '' }
  page.value = 1
  loadLogs()
}

onMounted(() => {
  if (!authStore.isAdmin) {
    router.push('/')
    return
  }
  loadLogs()
  loadStats()
})
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <AppNavbar />
    
    <main class="max-w-[1200px] mx-auto px-6 py-8">
      <PageHeader title="操作日志" subtitle="查看系统操作记录和统计信息" />
      
      <!-- 统计卡片 -->
      <div class="stats-grid">
        <StatsCard label="总请求数" :value="stats?.total_requests?.toLocaleString() || 0" />
        <StatsCard label="今日请求" :value="stats?.by_action?.['filter'] || 0" />
        <StatsCard label="活跃用户" :value="stats?.unique_users || 0" />
        <StatsCard label="错误率" value="0.3%" />
      </div>
      
      <!-- 筛选表单 -->
      <div class="filter-card">
        <form @submit.prevent="handleFilter" class="filter-grid">
          <FormField
            v-model="filterForm.user_id"
            label="用户ID"
            type="number"
            placeholder="全部用户"
          />
          
          <FormSelect
            v-model="filterForm.action"
            label="操作类型"
            :options="actionOptions"
          />
          
          <FormField
            v-model="filterForm.start_date"
            label="开始时间"
            type="date"
          />
          
          <FormField
            v-model="filterForm.end_date"
            label="结束时间"
            type="date"
          />
          
          <div class="filter-actions">
            <ActionButton
              type="submit"
              variant="primary"
              icon="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            >
              查询
            </ActionButton>
            <ActionButton
              type="button"
              variant="secondary"
              icon="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              @click="handleReset"
            >
              重置
            </ActionButton>
          </div>
        </form>
      </div>
      
      <!-- 日志表格 -->
      <DataTable :loading="loading" :empty="logs.length === 0" empty-text="暂无数据">
        <template #header>
          <tr>
            <th>ID</th>
            <th>用户</th>
            <th>操作类型</th>
            <th>API 路径</th>
            <th>IP 地址</th>
            <th>状态码</th>
            <th>操作时间</th>
          </tr>
        </template>
        <tr v-for="log in logs" :key="log.id">
          <td>{{ log.id }}</td>
          <td><strong>{{ log.username || '-' }}</strong></td>
          <td>
            <Badge :variant="getActionBadgeClass(log.action)" :text="getActionText(log.action)" />
          </td>
          <td><code class="log-code">{{ log.resource || '-' }}</code></td>
          <td>{{ log.ip_address || '-' }}</td>
          <td>
            <Badge :variant="getStatusBadgeClass(log.status_code)" :text="String(log.status_code || '-')" />
          </td>
          <td>{{ log.created_at?.replace('T', ' ').split('.')[0] }}</td>
        </tr>
      </DataTable>
    </main>
  </div>
</template>
