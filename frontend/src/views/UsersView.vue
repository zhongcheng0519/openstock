<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { adminApi, type UserResponse } from '@/api/client'

const router = useRouter()
const authStore = useAuthStore()

const users = ref<UserResponse[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const loading = ref(false)

const showCreateModal = ref(false)
const createForm = ref({
  username: '',
  nickname: '',
  email: '',
  phone: '',
  password: '',
  role: 'user'
})
const createLoading = ref(false)
const createError = ref('')

const stats = computed(() => {
  const totalUsers = users.value.length
  const activeUsers = users.value.filter(u => u.is_active).length
  const adminUsers = users.value.filter(u => u.role === 'admin').length
  return { totalUsers, activeUsers, adminUsers }
})

async function loadUsers() {
  loading.value = true
  try {
    const response = await adminApi.getUsers({ page: page.value, page_size: pageSize.value })
    users.value = response.data.items
    total.value = response.data.total
  } catch (error) {
    console.error('Failed to load users:', error)
  } finally {
    loading.value = false
  }
}

async function handleCreateUser() {
  createError.value = ''
  
  if (!createForm.value.username.trim()) {
    createError.value = '请输入用户名'
    return
  }
  if (!createForm.value.nickname.trim()) {
    createError.value = '请输入昵称'
    return
  }
  if (!createForm.value.password || createForm.value.password.length < 8) {
    createError.value = '密码至少8位'
    return
  }
  if (!createForm.value.email.trim()) {
    createError.value = '请输入邮箱'
    return
  }
  
  createLoading.value = true
  
  try {
    await adminApi.createUser({
      username: createForm.value.username.trim(),
      nickname: createForm.value.nickname.trim(),
      password: createForm.value.password,
      email: createForm.value.email.trim(),
      phone: createForm.value.phone || undefined,
      role: createForm.value.role
    })
    
    showCreateModal.value = false
    createForm.value = { username: '', nickname: '', email: '', phone: '', password: '', role: 'user' }
    loadUsers()
  } catch (error) {
    createError.value = error instanceof Error ? error.message : '创建失败'
  } finally {
    createLoading.value = false
  }
}

async function handleToggleStatus(user: UserResponse) {
  const action = user.is_active ? '禁用' : '启用'
  if (!confirm(`确定要${action}用户 ${user.username} 吗？`)) return
  
  try {
    await adminApi.updateUserStatus(user.id, !user.is_active)
    loadUsers()
  } catch (error) {
    alert(error instanceof Error ? error.message : '操作失败')
  }
}

async function handleResetPassword(user: UserResponse) {
  const newPassword = 'Password123'
  if (!confirm(`确定要重置用户 ${user.username} 的密码吗？\n新密码将设置为：${newPassword}`)) return
  
  try {
    await adminApi.resetUserPassword(user.id, newPassword)
    alert(`用户 ${user.username} 的密码已重置为：${newPassword}`)
  } catch (error) {
    alert(error instanceof Error ? error.message : '重置失败')
  }
}

async function handleDeleteUser(user: UserResponse) {
  if (!confirm(`确定要删除用户 ${user.username} 吗？此操作不可恢复！`)) return
  
  try {
    await adminApi.deleteUser(user.id)
    loadUsers()
  } catch (error) {
    alert(error instanceof Error ? error.message : '删除失败')
  }
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
  loadUsers()
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
          <router-link to="/users" class="navbar-link active">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path>
            </svg>
            用户管理
          </router-link>
          <router-link to="/logs" class="navbar-link">
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
        <div class="page-title-group">
          <h1 class="page-title">用户管理</h1>
          <p class="page-subtitle">管理系统用户账号和权限</p>
        </div>
        <button
          @click="showCreateModal = true"
          class="btn btn-primary"
        >
          <svg style="width: 18px; height: 18px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
          </svg>
          创建用户
        </button>
      </div>
      
      <!-- 统计卡片 -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">总用户数</div>
          <div class="stat-value">{{ total }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">活跃用户</div>
          <div class="stat-value">{{ stats.activeUsers }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">管理员</div>
          <div class="stat-value">{{ stats.adminUsers }}</div>
        </div>
      </div>
      
      <!-- 用户表格 -->
      <div class="table-container">
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>用户名</th>
              <th>昵称</th>
              <th>邮箱</th>
              <th>角色</th>
              <th>状态</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id">
              <td>{{ user.id }}</td>
              <td><strong>{{ user.username }}</strong></td>
              <td>{{ user.nickname }}</td>
              <td>{{ user.email }}</td>
              <td>
                <span 
                  class="badge"
                  :class="user.role === 'admin' ? 'badge-danger' : 'badge-info'"
                >
                  {{ user.role === 'admin' ? '管理员' : '普通用户' }}
                </span>
              </td>
              <td>
                <span 
                  class="badge"
                  :class="user.is_active ? 'badge-success' : 'badge-gray'"
                >
                  {{ user.is_active ? '正常' : '已禁用' }}
                </span>
              </td>
              <td>{{ user.created_at?.split('T')[0] }}</td>
              <td>
                <div class="table-actions">
                  <button
                    @click="handleResetPassword(user)"
                    class="action-btn action-btn-primary"
                  >
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"></path>
                    </svg>
                    重置
                  </button>
                  <button
                    @click="handleToggleStatus(user)"
                    class="action-btn action-btn-secondary"
                  >
                    {{ user.is_active ? '禁用' : '启用' }}
                  </button>
                  <button
                    v-if="user.id !== authStore.user?.id"
                    @click="handleDeleteUser(user)"
                    class="action-btn action-btn-danger"
                  >
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                    </svg>
                    删除
                  </button>
                  <span v-else class="text-xs text-gray-400">当前用户</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>
    
    <!-- 创建用户弹窗 -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal" style="width: 600px;">
        <div class="modal-header">
          <h3 class="modal-title">创建新用户</h3>
          <button @click="showCreateModal = false" class="modal-close" style="background: none; border: none; color: var(--gray-400); cursor: pointer; padding: 0;">
            <svg style="width: 24px; height: 24px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleCreateUser">
            <div class="form-grid form-grid-2">
              <div class="form-group">
                <label class="label label-required">用户名</label>
                <input v-model="createForm.username" type="text" class="input" placeholder="用于登录" />
              </div>
              <div class="form-group">
                <label class="label label-required">昵称</label>
                <input v-model="createForm.nickname" type="text" class="input" placeholder="用于显示" />
              </div>
            </div>
            
            <div class="form-grid form-grid-2" style="margin-top: 1rem;">
              <div class="form-group">
                <label class="label label-required">邮箱</label>
                <input v-model="createForm.email" type="email" class="input" placeholder="example@domain.com" />
              </div>
              <div class="form-group">
                <label class="label">手机号</label>
                <input v-model="createForm.phone" type="tel" class="input" placeholder="选填" maxlength="11" />
              </div>
            </div>
            
            <div class="form-grid form-grid-2" style="margin-top: 1rem;">
              <div class="form-group">
                <label class="label label-required">初始密码</label>
                <input v-model="createForm.password" type="password" class="input" placeholder="至少8位" />
              </div>
              <div class="form-group">
                <label class="label label-required">角色</label>
                <select v-model="createForm.role" class="input">
                  <option value="user">普通用户</option>
                  <option value="admin">管理员</option>
                </select>
              </div>
            </div>
            
            <div v-if="createError" class="error-message" style="margin-top: 1rem;">
              <p>{{ createError }}</p>
            </div>
          </form>
        </div>
        
        <div class="modal-footer">
          <button @click="showCreateModal = false" class="btn btn-secondary">
            取消
          </button>
          <button
            @click="handleCreateUser"
            :disabled="createLoading"
            class="btn btn-primary"
          >
            {{ createLoading ? '创建中...' : '创建用户' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
