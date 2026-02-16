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
            <router-link to="/users" class="px-3 py-2 text-sm font-medium text-red-600 bg-red-50 rounded-lg">
              用户管理
            </router-link>
            <router-link to="/logs" class="px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
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
      <div class="flex justify-between items-center mb-8">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">用户管理</h1>
          <p class="text-gray-600 mt-1">管理系统用户账号和权限</p>
        </div>
        <button
          @click="showCreateModal = true"
          class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg transition-colors flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
          </svg>
          创建用户
        </button>
      </div>
      
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-8">
        <div class="bg-white rounded-xl shadow-sm p-6">
          <p class="text-sm text-gray-500">总用户数</p>
          <p class="text-3xl font-bold text-gray-900 mt-1">{{ total }}</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm p-6">
          <p class="text-sm text-gray-500">活跃用户</p>
          <p class="text-3xl font-bold text-gray-900 mt-1">{{ stats.activeUsers }}</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm p-6">
          <p class="text-sm text-gray-500">管理员</p>
          <p class="text-3xl font-bold text-gray-900 mt-1">{{ stats.adminUsers }}</p>
        </div>
      </div>
      
      <div class="bg-white rounded-xl shadow-sm overflow-hidden">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">用户名</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">昵称</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">邮箱</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">角色</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">创建时间</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="user in users" :key="user.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ user.id }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ user.username }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ user.nickname }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ user.email }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span 
                  class="px-2 py-1 text-xs font-medium rounded-full"
                  :class="user.role === 'admin' ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'"
                >
                  {{ user.role === 'admin' ? '管理员' : '普通用户' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span 
                  class="px-2 py-1 text-xs font-medium rounded-full"
                  :class="user.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'"
                >
                  {{ user.is_active ? '正常' : '已禁用' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ user.created_at?.split('T')[0] }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <div class="flex items-center gap-2">
                  <button
                    @click="handleResetPassword(user)"
                    class="px-2 py-1 text-xs bg-red-50 text-red-600 hover:bg-red-100 rounded transition-colors"
                  >
                    重置密码
                  </button>
                  <button
                    @click="handleToggleStatus(user)"
                    class="px-2 py-1 text-xs bg-gray-100 text-gray-600 hover:bg-gray-200 rounded transition-colors"
                  >
                    {{ user.is_active ? '禁用' : '启用' }}
                  </button>
                  <button
                    v-if="user.id !== authStore.user?.id"
                    @click="handleDeleteUser(user)"
                    class="px-2 py-1 text-xs bg-red-50 text-red-600 hover:bg-red-100 rounded transition-colors"
                  >
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
    
    <div v-if="showCreateModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-lg mx-4">
        <div class="flex items-center justify-between p-6 border-b border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900">创建新用户</h3>
          <button @click="showCreateModal = false" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        
        <form @submit.prevent="handleCreateUser" class="p-6 space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">用户名 <span class="text-red-500">*</span></label>
              <input v-model="createForm.username" type="text" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500" placeholder="用于登录" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">昵称 <span class="text-red-500">*</span></label>
              <input v-model="createForm.nickname" type="text" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500" placeholder="用于显示" />
            </div>
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">邮箱 <span class="text-red-500">*</span></label>
              <input v-model="createForm.email" type="email" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500" placeholder="example@domain.com" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">手机号</label>
              <input v-model="createForm.phone" type="tel" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500" placeholder="选填" maxlength="11" />
            </div>
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">初始密码 <span class="text-red-500">*</span></label>
              <input v-model="createForm.password" type="password" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500" placeholder="至少8位" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">角色 <span class="text-red-500">*</span></label>
              <select v-model="createForm.role" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500">
                <option value="user">普通用户</option>
                <option value="admin">管理员</option>
              </select>
            </div>
          </div>
          
          <div v-if="createError" class="p-3 bg-red-50 border border-red-200 rounded-lg">
            <p class="text-sm text-red-600">{{ createError }}</p>
          </div>
        </form>
        
        <div class="flex justify-end gap-3 p-6 border-t border-gray-200">
          <button @click="showCreateModal = false" class="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
            取消
          </button>
          <button
            @click="handleCreateUser"
            :disabled="createLoading"
            class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg transition-colors disabled:opacity-50"
          >
            {{ createLoading ? '创建中...' : '创建用户' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
