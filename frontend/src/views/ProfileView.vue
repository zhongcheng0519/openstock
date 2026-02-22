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
    <nav class="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-[100]">
      <div class="max-w-[1400px] mx-auto px-6">
        <div class="flex items-center justify-between h-16">
          <router-link to="/" class="flex items-center gap-3 text-gray-900 no-underline">
            <div class="w-9 h-9 bg-gradient-to-br from-red-600 to-red-400 rounded-lg flex items-center justify-center shadow-sm">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
              </svg>
            </div>
            <span class="text-xl font-bold">股票分析系统</span>
          </router-link>
          
          <div class="flex items-center gap-2">
            <router-link 
              to="/" 
              class="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 hover:text-gray-900 rounded-lg transition-all no-underline"
            >
              <svg class="w-[18px] h-[18px]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"></path>
              </svg>
              股票筛选
            </router-link>
            <router-link 
              to="/profile" 
              class="flex items-center gap-2 px-4 py-2 text-sm font-medium bg-red-50 text-red-600 rounded-lg no-underline"
            >
              <svg class="w-[18px] h-[18px]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
              </svg>
              个人中心
            </router-link>
            <template v-if="authStore.isAdmin">
              <router-link 
                to="/users" 
                class="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 hover:text-gray-900 rounded-lg transition-all no-underline"
              >
                <svg class="w-[18px] h-[18px]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path>
                </svg>
                用户管理
              </router-link>
              <router-link 
                to="/logs" 
                class="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 hover:text-gray-900 rounded-lg transition-all no-underline"
              >
                <svg class="w-[18px] h-[18px]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
                操作日志
              </router-link>
            </template>
            
            <div class="flex items-center gap-4 ml-4 pl-4 border-l border-gray-200">
              <div class="flex items-center gap-2">
                <div class="w-8 h-8 bg-gradient-to-br from-red-600 to-red-400 rounded-full flex items-center justify-center text-white font-semibold text-sm shadow-sm">
                  {{ authStore.userInitial }}
                </div>
                <span class="text-sm font-medium text-gray-900">{{ authStore.user?.nickname }}</span>
              </div>
              <button 
                @click="handleLogout" 
                class="flex items-center gap-1.5 px-3.5 py-2 text-sm font-medium text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 hover:border-gray-400 hover:shadow-sm transition-all bg-transparent cursor-pointer"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
                </svg>
                退出
              </button>
            </div>
          </div>
        </div>
      </div>
    </nav>
    
    <main class="max-w-[1200px] mx-auto px-6 py-8">
      <div class="mb-10">
        <h1 class="text-[1.875rem] font-bold text-gray-900 mb-2">个人中心</h1>
        <p class="text-base text-gray-600 mt-2">管理您的个人信息和账号设置</p>
      </div>
      
      <div class="grid gap-8" style="grid-template-columns: 280px 1fr;">
        <div class="flex flex-col gap-4">
          <div class="bg-white rounded-xl shadow p-8 text-center">
            <div class="w-20 h-20 bg-gradient-to-br from-red-600 to-red-400 rounded-full inline-flex items-center justify-center text-white font-bold text-[2rem] mb-5 shadow-md">
              {{ authStore.userInitial }}
            </div>
            <div class="text-xl font-semibold text-gray-900 mb-1">{{ authStore.user?.nickname }}</div>
            <div class="text-sm text-gray-500 mb-5">@{{ authStore.user?.username }}</div>
            <span 
              class="inline-flex px-[0.875rem] py-1.5 text-[0.8125rem] font-medium rounded-full"
              :class="authStore.isAdmin ? 'bg-red-50 text-red-600' : 'bg-gray-100 text-gray-600'"
            >
              {{ authStore.isAdmin ? '管理员' : '普通用户' }}
            </span>
          </div>
        </div>
        
        <div class="flex flex-col gap-6">
          <!-- 基本信息 -->
          <div class="bg-white rounded-xl shadow p-8">
            <h2 class="text-lg font-semibold text-gray-900 mb-6 pb-3 border-b-2 border-gray-200">基本信息</h2>
            
            <form @submit.prevent="handleUpdateProfile">
              <div class="grid grid-cols-2 gap-5">
                <div>
                  <label class="block text-sm font-medium text-gray-700">
                    昵称 <span class="text-red-500">*</span>
                  </label>
                  <input
                    v-model="profileForm.nickname"
                    type="text"
                    class="w-full px-[0.875rem] py-2.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition-all placeholder:text-gray-400"
                    placeholder="请输入昵称"
                    required
                  />
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700">
                    邮箱 <span class="text-red-500">*</span>
                  </label>
                  <input
                    v-model="profileForm.email"
                    type="email"
                    class="w-full px-[0.875rem] py-2.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition-all placeholder:text-gray-400"
                    placeholder="example@domain.com"
                    required
                  />
                </div>
              </div>
              
              <div class="mt-5">
                <label class="block text-sm font-medium text-gray-700">手机号</label>
                <input
                  v-model="profileForm.phone"
                  type="tel"
                  class="w-full px-[0.875rem] py-2.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition-all placeholder:text-gray-400"
                  placeholder="11位手机号（选填）"
                  maxlength="11"
                />
              </div>
              
              <div v-if="profileError" class="mt-5 p-3 bg-red-50 border border-red-200 rounded-lg">
                <p class="text-sm text-red-600">{{ profileError }}</p>
              </div>
              
              <div v-if="profileSuccess" class="mt-5 p-3 bg-green-50 border border-green-200 rounded-lg">
                <p class="text-sm text-green-600">{{ profileSuccess }}</p>
              </div>
              
              <button
                type="submit"
                :disabled="profileLoading"
                class="mt-6 inline-flex items-center gap-2 px-5 py-2.5 bg-red-600 hover:bg-red-700 hover:shadow-md hover:-translate-y-0.5 text-white text-sm font-medium rounded-lg transition-all disabled:opacity-50 disabled:hover:translate-y-0 border-0 cursor-pointer"
              >
                <svg v-if="!profileLoading" class="w-[18px] h-[18px]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                <svg v-else class="animate-spin w-[18px] h-[18px]" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                保存修改
              </button>
            </form>
          </div>
          
          <!-- 修改密码 -->
          <div class="bg-white rounded-xl shadow p-8">
            <h2 class="text-lg font-semibold text-gray-900 mb-6 pb-3 border-b-2 border-gray-200">修改密码</h2>
            
            <form @submit.prevent="handleChangePassword">
              <div>
                <label class="block text-sm font-medium text-gray-700">
                  当前密码 <span class="text-red-500">*</span>
                </label>
                <input
                  v-model="passwordForm.oldPassword"
                  type="password"
                  class="w-full px-[0.875rem] py-2.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition-all placeholder:text-gray-400"
                  placeholder="请输入当前密码"
                  autocomplete="current-password"
                  required
                />
              </div>
              
              <div class="grid grid-cols-2 gap-5 mt-5">
                <div>
                  <label class="block text-sm font-medium text-gray-700">
                    新密码 <span class="text-red-500">*</span>
                  </label>
                  <input
                    v-model="passwordForm.newPassword"
                    type="password"
                    class="w-full px-[0.875rem] py-2.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition-all placeholder:text-gray-400"
                    placeholder="至少8位"
                    autocomplete="new-password"
                    required
                  />
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700">
                    确认新密码 <span class="text-red-500">*</span>
                  </label>
                  <input
                    v-model="passwordForm.confirmPassword"
                    type="password"
                    class="w-full px-[0.875rem] py-2.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition-all placeholder:text-gray-400"
                    placeholder="再次输入新密码"
                    autocomplete="new-password"
                    required
                  />
                </div>
              </div>
              
              <div v-if="passwordError" class="mt-5 p-3 bg-red-50 border border-red-200 rounded-lg">
                <p class="text-sm text-red-600">{{ passwordError }}</p>
              </div>
              
              <div v-if="passwordSuccess" class="mt-5 p-3 bg-green-50 border border-green-200 rounded-lg">
                <p class="text-sm text-green-600">{{ passwordSuccess }}</p>
              </div>
              
              <button
                type="submit"
                :disabled="passwordLoading"
                class="mt-6 inline-flex items-center gap-2 px-5 py-2.5 bg-red-600 hover:bg-red-700 hover:shadow-md hover:-translate-y-0.5 text-white text-sm font-medium rounded-lg transition-all disabled:opacity-50 disabled:hover:translate-y-0 border-0 cursor-pointer"
              >
                <svg v-if="!passwordLoading" class="w-[18px] h-[18px]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"></path>
                </svg>
                <svg v-else class="animate-spin w-[18px] h-[18px]" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                修改密码
              </button>
            </form>
          </div>
          
          <!-- 账号信息 -->
          <div class="bg-white rounded-xl shadow p-8">
            <h2 class="text-lg font-semibold text-gray-900 mb-6 pb-3 border-b-2 border-gray-200">账号信息</h2>
            
            <div class="grid gap-0">
              <div class="flex justify-between py-4 border-b border-gray-200">
                <span class="text-sm text-gray-500">用户名</span>
                <span class="text-sm font-medium text-gray-900">{{ authStore.user?.username }}</span>
              </div>
              <div class="flex justify-between py-4 border-b border-gray-200">
                <span class="text-sm text-gray-500">角色</span>
                <span class="text-sm font-medium text-gray-900">{{ authStore.isAdmin ? '管理员' : '普通用户' }}</span>
              </div>
              <div class="flex justify-between py-4 border-b border-gray-200">
                <span class="text-sm text-gray-500">账号状态</span>
                <span class="inline-flex px-2.5 py-1 text-xs font-medium bg-green-100 text-green-700 rounded-full">正常</span>
              </div>
              <div class="flex justify-between py-4">
                <span class="text-sm text-gray-500">注册时间</span>
                <span class="text-sm font-medium text-gray-900">{{ authStore.user?.created_at?.split('T')[0] || '2024-01-01' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>
