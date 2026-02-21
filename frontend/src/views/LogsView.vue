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
    'login': 'badge-info',
    'logout': 'badge-gray',
    'register': 'badge-success',
    'filter': 'badge-success',
    'user_create': 'badge-danger',
    'user_update': 'badge-danger',
    'user_delete': 'badge-danger',
    'password_change': 'badge-warning',
    'password_reset': 'badge-warning',
  }
  return actionMap[action] || 'badge-gray'
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
  if (!status) return 'badge-gray'
  if (status >= 200 && status < 300) return 'badge-success'
  if (status >= 400 && status < 500) return 'badge-warning'
  return 'badge-danger'
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
    <!-- 顶部导航栏 -->
    <nav class="navbar">
      <div class="navbar-content">
        <router-link to="/" class="navbar-brand">
          <div class="navbar-logo">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
            </svg>
          </div>
          <span>股票分析系统</span>
        </router-link>
        
        <div class="navbar-menu">
          <router-link to="/" class="navbar-link">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"></path>
            </svg>
            股票筛选
          </router-link>
          <router-link to="/profile" class="navbar-link">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
            </svg>
            个人中心
          </router-link>
          <router-link to="/users" class="navbar-link">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path>
            </svg>
            用户管理
          </router-link>
          <router-link to="/logs" class="navbar-link active">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
            操作日志
          </router-link>
        </div>
        
        <div class="navbar-user">
          <div class="user-info">
            <div class="user-avatar">
              {{ authStore.userInitial }}
            </div>
            <span class="user-name">{{ authStore.user?.nickname }}</span>
          </div>
          <button @click="handleLogout" class="btn btn-secondary btn-sm">
            <svg style="width: 16px; height: 16px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
            </svg>
            退出
          </button>
        </div>
      </div>
    </nav>
    
    <main class="main-container">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1 class="page-title">操作日志</h1>
        <p class="page-subtitle">查看系统操作记录和统计信息</p>
      </div>
      
      <!-- 统计卡片 -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">总请求数</div>
          <div class="stat-value">{{ stats?.total_requests?.toLocaleString() || 0 }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">今日请求</div>
          <div class="stat-value">{{ stats?.by_action?.['filter'] || 0 }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">活跃用户</div>
          <div class="stat-value">{{ stats?.unique_users || 0 }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">错误率</div>
          <div class="stat-value">0.3%</div>
        </div>
      </div>
      
      <!-- 筛选表单 -->
      <div class="filter-card">
        <form @submit.prevent="handleFilter" class="filter-grid">
          <div class="form-group">
            <label class="label">用户ID</label>
            <input
              v-model="filterForm.user_id"
              type="number"
              class="input"
              placeholder="全部用户"
            />
          </div>
          
          <div class="form-group">
            <label class="label">操作类型</label>
            <select
              v-model="filterForm.action"
              class="input"
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
          
          <div class="form-group">
            <label class="label">开始时间</label>
            <input
              v-model="filterForm.start_date"
              type="date"
              class="input"
            />
          </div>
          
          <div class="form-group">
            <label class="label">结束时间</label>
            <input
              v-model="filterForm.end_date"
              type="date"
              class="input"
            />
          </div>
          
          <div class="filter-actions">
            <button
              type="submit"
              class="btn btn-primary"
            >
              <svg style="width: 18px; height: 18px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
              </svg>
              查询
            </button>
            <button
              type="button"
              @click="handleReset"
              class="btn btn-secondary"
            >
              <svg style="width: 18px; height: 18px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
              </svg>
              重置
            </button>
          </div>
        </form>
      </div>
      
      <!-- 日志表格 -->
      <div class="table-container">
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>用户</th>
              <th>操作类型</th>
              <th>API 路径</th>
              <th>IP 地址</th>
              <th>状态码</th>
              <th>操作时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in logs" :key="log.id">
              <td>{{ log.id }}</td>
              <td><strong>{{ log.username || '-' }}</strong></td>
              <td>
                <span 
                  class="badge"
                  :class="getActionBadgeClass(log.action)"
                >
                  {{ getActionText(log.action) }}
                </span>
              </td>
              <td><code class="log-code">{{ log.resource || '-' }}</code></td>
              <td>{{ log.ip_address || '-' }}</td>
              <td>
                <span 
                  class="badge"
                  :class="getStatusBadgeClass(log.status_code)"
                >
                  {{ log.status_code || '-' }}
                </span>
              </td>
              <td>{{ log.created_at?.replace('T', ' ').split('.')[0] }}</td>
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
