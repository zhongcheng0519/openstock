<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const profileForm = ref({
  nickname: '',
  email: '',
  phone: ''
})

const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const profileLoading = ref(false)
const passwordLoading = ref(false)
const profileError = ref('')
const passwordError = ref('')
const profileSuccess = ref('')
const passwordSuccess = ref('')

onMounted(() => {
  if (authStore.user) {
    profileForm.value = {
      nickname: authStore.user.nickname,
      email: authStore.user.email || '',
      phone: authStore.user.phone || ''
    }
  }
})

async function handleUpdateProfile() {
  profileError.value = ''
  profileSuccess.value = ''
  
  if (!profileForm.value.nickname.trim()) {
    profileError.value = '请输入昵称'
    return
  }
  if (!profileForm.value.email.trim()) {
    profileError.value = '请输入邮箱地址'
    return
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(profileForm.value.email)) {
    profileError.value = '请输入正确的邮箱地址'
    return
  }
  if (profileForm.value.phone && !/^\d{11}$/.test(profileForm.value.phone)) {
    profileError.value = '手机号必须为11位数字'
    return
  }
  
  profileLoading.value = true
  
  try {
    await authStore.updateProfile({
      nickname: profileForm.value.nickname.trim(),
      email: profileForm.value.email.trim(),
      phone: profileForm.value.phone || undefined
    })
    profileSuccess.value = '信息保存成功！'
  } catch (error) {
    profileError.value = error instanceof Error ? error.message : '保存失败'
  } finally {
    profileLoading.value = false
  }
}

async function handleChangePassword() {
  passwordError.value = ''
  passwordSuccess.value = ''
  
  if (!passwordForm.value.oldPassword) {
    passwordError.value = '请输入当前密码'
    return
  }
  if (passwordForm.value.newPassword.length < 8) {
    passwordError.value = '新密码至少8位'
    return
  }
  if (!/[a-zA-Z]/.test(passwordForm.value.newPassword) || !/\d/.test(passwordForm.value.newPassword)) {
    passwordError.value = '新密码需包含字母和数字'
    return
  }
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    passwordError.value = '两次输入的密码不一致'
    return
  }
  
  passwordLoading.value = true
  
  try {
    await authStore.changePassword(passwordForm.value.oldPassword, passwordForm.value.newPassword)
    passwordSuccess.value = '密码修改成功！请重新登录'
    setTimeout(() => {
      authStore.logout()
      router.push('/login')
    }, 1500)
  } catch (error) {
    passwordError.value = error instanceof Error ? error.message : '修改失败'
  } finally {
    passwordLoading.value = false
  }
}

async function handleLogout() {
  if (confirm('确定要退出登录吗？')) {
    await authStore.logout()
    router.push('/login')
  }
}
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
            <router-link to="/profile" class="px-3 py-2 text-sm font-medium text-red-600 bg-red-50 rounded-lg">
              个人中心
            </router-link>
            <template v-if="authStore.isAdmin">
              <router-link to="/users" class="px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
                用户管理
              </router-link>
              <router-link to="/logs" class="px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
                操作日志
              </router-link>
            </template>
            
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
    
    <main class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900">个人中心</h1>
        <p class="text-gray-600 mt-1">管理您的个人信息和账号设置</p>
      </div>
      
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div class="lg:col-span-1">
          <div class="bg-white rounded-xl shadow-sm p-6 text-center">
            <div class="w-20 h-20 bg-gradient-to-br from-red-600 to-red-500 rounded-full flex items-center justify-center text-white font-bold text-3xl mx-auto mb-4">
              {{ authStore.userInitial }}
            </div>
            <h2 class="text-lg font-semibold text-gray-900">{{ authStore.user?.nickname }}</h2>
            <p class="text-sm text-gray-500">@{{ authStore.user?.username }}</p>
            <span 
              class="inline-block mt-3 px-3 py-1 text-sm font-medium rounded-full"
              :class="authStore.isAdmin ? 'bg-red-100 text-red-600' : 'bg-gray-100 text-gray-600'"
            >
              {{ authStore.isAdmin ? '管理员' : '普通用户' }}
            </span>
          </div>
        </div>
        
        <div class="lg:col-span-2 space-y-6">
          <div class="bg-white rounded-xl shadow-sm p-6">
            <h3 class="text-lg font-semibold text-gray-900 pb-4 border-b border-gray-200">基本信息</h3>
            
            <form @submit.prevent="handleUpdateProfile" class="mt-6 space-y-4">
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    昵称 <span class="text-red-500">*</span>
                  </label>
                  <input
                    v-model="profileForm.nickname"
                    type="text"
                    class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
                    placeholder="请输入昵称"
                  />
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    邮箱 <span class="text-red-500">*</span>
                  </label>
                  <input
                    v-model="profileForm.email"
                    type="email"
                    class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
                    placeholder="example@domain.com"
                  />
                </div>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">手机号</label>
                <input
                  v-model="profileForm.phone"
                  type="tel"
                  class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
                  placeholder="11位手机号（选填）"
                  maxlength="11"
                />
              </div>
              
              <div v-if="profileError" class="p-3 bg-red-50 border border-red-200 rounded-lg">
                <p class="text-sm text-red-600">{{ profileError }}</p>
              </div>
              
              <div v-if="profileSuccess" class="p-3 bg-green-50 border border-green-200 rounded-lg">
                <p class="text-sm text-green-600">{{ profileSuccess }}</p>
              </div>
              
              <button
                type="submit"
                :disabled="profileLoading"
                class="px-6 py-2.5 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg transition-colors flex items-center gap-2 disabled:opacity-50"
              >
                <svg v-if="profileLoading" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                保存修改
              </button>
            </form>
          </div>
          
          <div class="bg-white rounded-xl shadow-sm p-6">
            <h3 class="text-lg font-semibold text-gray-900 pb-4 border-b border-gray-200">修改密码</h3>
            
            <form @submit.prevent="handleChangePassword" class="mt-6 space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  当前密码 <span class="text-red-500">*</span>
                </label>
                <input
                  v-model="passwordForm.oldPassword"
                  type="password"
                  class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
                  placeholder="请输入当前密码"
                  autocomplete="current-password"
                />
              </div>
              
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    新密码 <span class="text-red-500">*</span>
                  </label>
                  <input
                    v-model="passwordForm.newPassword"
                    type="password"
                    class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
                    placeholder="至少8位"
                    autocomplete="new-password"
                  />
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    确认新密码 <span class="text-red-500">*</span>
                  </label>
                  <input
                    v-model="passwordForm.confirmPassword"
                    type="password"
                    class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
                    placeholder="再次输入新密码"
                    autocomplete="new-password"
                  />
                </div>
              </div>
              
              <div v-if="passwordError" class="p-3 bg-red-50 border border-red-200 rounded-lg">
                <p class="text-sm text-red-600">{{ passwordError }}</p>
              </div>
              
              <div v-if="passwordSuccess" class="p-3 bg-green-50 border border-green-200 rounded-lg">
                <p class="text-sm text-green-600">{{ passwordSuccess }}</p>
              </div>
              
              <button
                type="submit"
                :disabled="passwordLoading"
                class="px-6 py-2.5 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg transition-colors flex items-center gap-2 disabled:opacity-50"
              >
                <svg v-if="passwordLoading" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                修改密码
              </button>
            </form>
          </div>
          
          <div class="bg-white rounded-xl shadow-sm p-6">
            <h3 class="text-lg font-semibold text-gray-900 pb-4 border-b border-gray-200">账号信息</h3>
            
            <div class="mt-6 space-y-4">
              <div class="flex justify-between py-2 border-b border-gray-100">
                <span class="text-sm text-gray-500">用户名</span>
                <span class="text-sm font-medium text-gray-900">{{ authStore.user?.username }}</span>
              </div>
              <div class="flex justify-between py-2 border-b border-gray-100">
                <span class="text-sm text-gray-500">角色</span>
                <span class="text-sm font-medium text-gray-900">{{ authStore.isAdmin ? '管理员' : '普通用户' }}</span>
              </div>
              <div class="flex justify-between py-2 border-b border-gray-100">
                <span class="text-sm text-gray-500">账号状态</span>
                <span class="px-2 py-0.5 text-xs font-medium bg-green-100 text-green-700 rounded-full">正常</span>
              </div>
              <div class="flex justify-between py-2">
                <span class="text-sm text-gray-500">注册时间</span>
                <span class="text-sm font-medium text-gray-900">{{ authStore.user?.created_at?.split('T')[0] }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>
