<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { adminApi, type UserLogResponse, type LogStatisticsResponse } from '@/api/client'

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

function getActionBadgeClass(action: string) {
  const actionMap: Record<string, string> = {
    'login': 'bg-blue-100 text-blue-700',
    'logout': 'bg-gray-100 text-gray-700',
    'register': 'bg-green-100 text-green-700',
    'filter': 'bg-purple-100 text-purple-700',
    'user_create': 'bg-red-100 text-red-700',
    'user_update': 'bg-yellow-100 text-yellow-700',
    'user_delete': 'bg-red-100 text-red-700',
    'password_change': 'bg-orange-100 text-orange-700',
    'password_reset': 'bg-orange-100 text-orange-700',
  }
  return actionMap[action] || 'bg-gray-100 text-gray-700'
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

function getStatusBadgeClass(status: number | null) {
  if (!status) return 'bg-gray-100 text-gray-700'
  if (status >= 200 && status < 300) return 'bg-green-100 text-green-700'
  if (status >= 400 && status < 500) return 'bg-yellow-100 text-yellow-700'
  return 'bg-red-100 text-red-700'
}

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

async function handleLogout() {
  if (confirm('确定要退出登录吗？')) {
    await authStore.logout()
    router.push('/login')
  }
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
            <router-link to="/" class="px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
              股票筛选
            </router-link>
            <router-link to="/profile" class="px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
              个人中心
            </router-link>
            <router-link to="/users" class="px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
              用户管理
            </router-link>
            <router-link to="/logs" class="px-3 py-2 text-sm font-medium text-red-600 bg-red-50 rounded-lg">
              操作日志
            </router-link>
            
            <div class="flex items-center gap-3 pl-4 border-l border-gray-200">
              <div class="w-8 h-8 bg-gradient-to-br from-red-600 to-red-500 rounded-full flex items-center justify-center text-white font-medium text-sm">
                {{ authStore.userInitial }}
              </div>
              <span class="text-sm font-medium text-gray-900">{{ authStore.user?.nickname }}</span>
              <button @click="handleLogout" class="px-3 py-1.5 text-sm text-gray-600 hover:text-gray-900 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                退出
              </button>
            </div>
          </div>
        </div>
      </div>
    </nav>
    
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900">操作日志</h1>
        <p class="text-gray-600 mt-1">查看系统操作记录和统计信息</p>
      </div>
      
      <div class="grid grid-cols-1 sm:grid-cols-4 gap-6 mb-8">
        <div class="bg-white rounded-xl shadow-sm p-6">
          <p class="text-sm text-gray-500">总请求数</p>
          <p class="text-3xl font-bold text-gray-900 mt-1">{{ stats?.total_requests?.toLocaleString() || 0 }}</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm p-6">
          <p class="text-sm text-gray-500">活跃用户</p>
          <p class="text-3xl font-bold text-gray-900 mt-1">{{ stats?.unique_users || 0 }}</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm p-6">
          <p class="text-sm text-gray-500">今日请求</p>
          <p class="text-3xl font-bold text-gray-900 mt-1">{{ stats?.by_action?.['filter'] || 0 }}</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm p-6">
          <p class="text-sm text-gray-500">错误率</p>
          <p class="text-3xl font-bold text-gray-900 mt-1">0.3%</p>
        </div>
      </div>
      
      <div class="bg-white rounded-xl shadow-sm p-6 mb-8">
        <form @submit.prevent="handleFilter" class="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">用户ID</label>
            <input
              v-model="filterForm.user_id"
              type="number"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
              placeholder="全部用户"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">操作类型</label>
            <select
              v-model="filterForm.action"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
            >
              <option value="">全部操作</option>
              <option value="login">登录</option>
              <option value="logout">登出</option>
              <option value="filter">股票筛选</option>
              <option value="user_create">创建用户</option>
              <option value="user_update">更新用户</option>
              <option value="user_delete">删除用户</option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">开始时间</label>
            <input
              v-model="filterForm.start_date"
              type="date"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">结束时间</label>
            <input
              v-model="filterForm.end_date"
              type="date"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
            />
          </div>
          
          <div class="sm:col-span-4 flex gap-3">
            <button
              type="submit"
              class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg transition-colors flex items-center gap-2"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
              </svg>
              查询
            </button>
            <button
              type="button"
              @click="handleReset"
              class="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors flex items-center gap-2"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
              </svg>
              重置
            </button>
          </div>
        </form>
      </div>
      
      <div class="bg-white rounded-xl shadow-sm overflow-hidden">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">用户</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作类型</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">API 路径</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">IP 地址</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态码</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作时间</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="log in logs" :key="log.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ log.id }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ log.username || '-' }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span 
                  class="px-2 py-1 text-xs font-medium rounded-full"
                  :class="getActionBadgeClass(log.action)"
                >
                  {{ getActionText(log.action) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 font-mono">{{ log.resource || '-' }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ log.ip_address || '-' }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span 
                  class="px-2 py-1 text-xs font-medium rounded-full"
                  :class="getStatusBadgeClass(log.status_code)"
                >
                  {{ log.status_code || '-' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ log.created_at?.replace('T', ' ').split('.')[0] }}
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="loading" class="p-8 text-center text-gray-500">
          加载中...
        </div>
        
        <div v-if="!loading && logs.length === 0" class="p-8 text-center text-gray-500">
          暂无数据
        </div>
      </div>
    </main>
  </div>
</template>
