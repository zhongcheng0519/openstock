<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { adminApi, type UserResponse } from '@/api/client'
import AppNavbar from '@/components/AppNavbar.vue'
import PageHeader from '@/components/PageHeader.vue'
import StatsCard from '@/components/StatsCard.vue'
import DataTable from '@/components/DataTable.vue'
import Badge from '@/components/Badge.vue'
import Modal from '@/components/Modal.vue'
import FormField from '@/components/FormField.vue'
import FormSelect from '@/components/FormSelect.vue'
import ActionButton from '@/components/ActionButton.vue'
import AlertMessage from '@/components/AlertMessage.vue'

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

const roleOptions = [
  { value: 'user', label: '普通用户' },
  { value: 'admin', label: '管理员' },
]

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
    <AppNavbar />
    
    <main class="max-w-[1200px] mx-auto px-6 py-8">
      <PageHeader title="用户管理" subtitle="管理系统用户账号和权限">
        <template #actions>
          <ActionButton
            variant="primary"
            icon="M12 4v16m8-8H4"
            @click="showCreateModal = true"
          >
            创建用户
          </ActionButton>
        </template>
      </PageHeader>
      
      <!-- 统计卡片 -->
      <div class="stats-grid">
        <StatsCard label="总用户数" :value="total" />
        <StatsCard label="活跃用户" :value="stats.activeUsers" />
        <StatsCard label="管理员" :value="stats.adminUsers" />
      </div>
      
      <!-- 用户表格 -->
      <DataTable :loading="loading" :empty="users.length === 0">
        <template #header>
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
        </template>
        <tr v-for="user in users" :key="user.id">
          <td>{{ user.id }}</td>
          <td><strong>{{ user.username }}</strong></td>
          <td>{{ user.nickname }}</td>
          <td>{{ user.email }}</td>
          <td>
            <Badge
              :variant="user.role === 'admin' ? 'danger' : 'info'"
              :text="user.role === 'admin' ? '管理员' : '普通用户'"
            />
          </td>
          <td>
            <Badge
              :variant="user.is_active ? 'success' : 'gray'"
              :text="user.is_active ? '正常' : '已禁用'"
            />
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
      </DataTable>
    </main>
    
    <!-- 创建用户弹窗 -->
    <Modal :show="showCreateModal" title="创建新用户" @close="showCreateModal = false">
      <form @submit.prevent="handleCreateUser">
        <div class="form-grid form-grid-2">
          <FormField
            v-model="createForm.username"
            label="用户名"
            type="text"
            placeholder="用于登录"
            required
          />
          <FormField
            v-model="createForm.nickname"
            label="昵称"
            type="text"
            placeholder="用于显示"
            required
          />
        </div>
        
        <div class="form-grid form-grid-2" style="margin-top: 1rem;">
          <FormField
            v-model="createForm.email"
            label="邮箱"
            type="email"
            placeholder="example@domain.com"
            required
          />
          <FormField
            v-model="createForm.phone"
            label="手机号"
            type="tel"
            placeholder="选填"
            :maxlength="11"
          />
        </div>
        
        <div class="form-grid form-grid-2" style="margin-top: 1rem;">
          <FormField
            v-model="createForm.password"
            label="初始密码"
            type="password"
            placeholder="至少8位"
            required
          />
          <FormSelect
            v-model="createForm.role"
            label="角色"
            :options="roleOptions"
            required
          />
        </div>
        
        <AlertMessage v-if="createError" type="error" :message="createError" />
      </form>
      
      <template #footer>
        <ActionButton variant="secondary" @click="showCreateModal = false">
          取消
        </ActionButton>
        <ActionButton
          variant="primary"
          :loading="createLoading"
          @click="handleCreateUser"
        >
          {{ createLoading ? '创建中...' : '创建用户' }}
        </ActionButton>
      </template>
    </Modal>
  </div>
</template>
