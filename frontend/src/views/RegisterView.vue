<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  username: '',
  nickname: '',
  password: '',
  confirmPassword: '',
  email: '',
  phone: ''
})

const loading = ref(false)
const errorMessage = ref('')

const passwordStrength = computed(() => {
  const pwd = form.value.password
  if (!pwd) return null
  
  let strength = 0
  if (pwd.length >= 8) strength++
  if (/[a-z]/.test(pwd) && /[A-Z]/.test(pwd)) strength++
  if (/\d/.test(pwd)) strength++
  if (/[^a-zA-Z0-9]/.test(pwd)) strength++
  
  if (strength <= 1) return { level: 'weak', text: '弱', color: 'bg-red-500' }
  if (strength <= 2) return { level: 'medium', text: '中', color: 'bg-yellow-500' }
  return { level: 'strong', text: '强', color: 'bg-green-500' }
})

function validateForm() {
  if (!form.value.username.trim()) {
    errorMessage.value = '请输入用户名'
    return false
  }
  if (!/^[a-zA-Z0-9_]+$/.test(form.value.username)) {
    errorMessage.value = '用户名只能包含字母、数字、下划线'
    return false
  }
  if (!form.value.nickname.trim()) {
    errorMessage.value = '请输入昵称'
    return false
  }
  if (!form.value.password) {
    errorMessage.value = '请输入密码'
    return false
  }
  if (form.value.password.length < 8) {
    errorMessage.value = '密码至少8位'
    return false
  }
  if (!/[a-zA-Z]/.test(form.value.password) || !/\d/.test(form.value.password)) {
    errorMessage.value = '密码需包含字母和数字'
    return false
  }
  if (form.value.password !== form.value.confirmPassword) {
    errorMessage.value = '两次输入的密码不一致'
    return false
  }
  if (!form.value.email.trim()) {
    errorMessage.value = '请输入邮箱地址'
    return false
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.value.email)) {
    errorMessage.value = '请输入正确的邮箱地址'
    return false
  }
  if (form.value.phone && !/^\d{11}$/.test(form.value.phone)) {
    errorMessage.value = '手机号必须为11位数字'
    return false
  }
  return true
}

async function handleRegister() {
  if (!validateForm()) return
  
  loading.value = true
  errorMessage.value = ''
  
  try {
    await authStore.register({
      username: form.value.username.trim(),
      nickname: form.value.nickname.trim(),
      password: form.value.password,
      email: form.value.email.trim(),
      phone: form.value.phone || undefined
    })
    
    alert('注册成功！请登录')
    router.push('/login')
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '注册失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="register-page">
    <div class="register-container">
      <div class="register-card">
        <div class="register-header">
          <div class="badge-init">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
            </svg>
            系统初始化
          </div>
          <h1 class="register-title">创建管理员账号</h1>
          <p class="register-subtitle">欢迎使用股票分析系统！请创建第一个管理员账号以开始使用</p>
        </div>
        
        <form @submit.prevent="handleRegister" class="form-grid">
          <div class="form-grid form-grid-2">
            <div class="form-group">
              <label class="label label-required">
                用户名
              </label>
              <input
                v-model="form.username"
                type="text"
                class="input"
                placeholder="用于登录"
              />
              <p class="text-xs text-gray-500 mt-1">仅支持字母、数字、下划线</p>
            </div>
            
            <div class="form-group">
              <label class="label label-required">
                昵称
              </label>
              <input
                v-model="form.nickname"
                type="text"
                class="input"
                placeholder="用于显示"
              />
            </div>
          </div>
          
          <div class="form-grid form-grid-2">
            <div class="form-group">
              <label class="label label-required">
                密码
              </label>
              <input
                v-model="form.password"
                type="password"
                class="input"
                placeholder="至少8位"
                autocomplete="new-password"
              />
              <div v-if="passwordStrength" class="password-strength" :class="'strength-' + passwordStrength.level">
                <div class="strength-bar">
                  <div class="strength-fill"></div>
                </div>
                <span class="text-xs" :class="{
                  'text-red-500': passwordStrength.level === 'weak',
                  'text-yellow-500': passwordStrength.level === 'medium',
                  'text-green-500': passwordStrength.level === 'strong'
                }">{{ passwordStrength.text }}</span>
              </div>
            </div>
            
            <div class="form-group">
              <label class="label label-required">
                确认密码
              </label>
              <input
                v-model="form.confirmPassword"
                type="password"
                class="input"
                placeholder="再次输入密码"
                autocomplete="new-password"
              />
            </div>
          </div>
          
          <div class="form-grid form-grid-2">
            <div class="form-group">
              <label class="label label-required">
                邮箱
              </label>
              <input
                v-model="form.email"
                type="email"
                class="input"
                placeholder="example@domain.com"
              />
            </div>
            
            <div class="form-group">
              <label class="label">
                手机号
              </label>
              <input
                v-model="form.phone"
                type="tel"
                class="input"
                placeholder="11位手机号（选填）"
                maxlength="11"
              />
            </div>
          </div>
          
          <div class="info-box">
            <div class="info-box-title">
              <svg fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path>
              </svg>
              重要提示
            </div>
            <ul class="list-disc ml-7 space-y-1">
              <li>这是系统第一个用户，将自动获得<strong>管理员权限</strong></li>
              <li>管理员可以管理其他用户、查看操作日志</li>
              <li>密码需包含字母和数字，长度至少8位</li>
              <li>请妥善保管账号信息，遗失后需联系技术支持</li>
            </ul>
          </div>
          
          <div v-if="errorMessage" class="error-message">
            <p>{{ errorMessage }}</p>
          </div>
          
          <button
            type="submit"
            :disabled="loading"
            class="btn btn-primary btn-lg w-full"
          >
            <svg v-if="loading" class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            {{ loading ? '创建中...' : '创建管理员账号' }}
          </button>
        </form>
        
        <div class="login-link">
          <p>
            已有账号？
            <router-link to="/login" class="text-red-600 hover:text-red-700 font-medium">
              立即登录
            </router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
