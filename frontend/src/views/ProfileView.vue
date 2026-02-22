<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AppNavbar from '@/components/AppNavbar.vue'
import PageHeader from '@/components/PageHeader.vue'
import UserProfileCard from '@/components/UserProfileCard.vue'
import FormInput from '@/components/FormInput.vue'
import AlertMessage from '@/components/AlertMessage.vue'
import SubmitButton from '@/components/SubmitButton.vue'
import InfoRow from '@/components/InfoRow.vue'

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
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <AppNavbar />
    
    <main class="max-w-[1200px] mx-auto px-6 py-8">
      <PageHeader title="个人中心" subtitle="管理您的个人信息和账号设置" />
      
      <div class="grid gap-8" style="grid-template-columns: 280px 1fr;">
        <div class="flex flex-col gap-4">
          <UserProfileCard
            :initial="authStore.userInitial"
            :nickname="authStore.user?.nickname || ''"
            :username="authStore.user?.username || ''"
            :is-admin="authStore.isAdmin"
          />
        </div>
        
        <div class="flex flex-col gap-6">
          <!-- 基本信息 -->
          <div class="bg-white rounded-xl shadow p-8">
            <h2 class="text-lg font-semibold text-gray-900 mb-6 pb-3 border-b-2 border-gray-200">基本信息</h2>
            
            <form @submit.prevent="handleUpdateProfile">
              <div class="grid grid-cols-2 gap-5">
                <FormInput
                  v-model="profileForm.nickname"
                  label="昵称"
                  placeholder="请输入昵称"
                  :required="true"
                />
                
                <FormInput
                  v-model="profileForm.email"
                  label="邮箱"
                  type="email"
                  placeholder="example@domain.com"
                  :required="true"
                />
              </div>
              
              <FormInput
                v-model="profileForm.phone"
                label="手机号"
                type="tel"
                placeholder="11位手机号（选填）"
                maxlength="11"
              />
              
              <AlertMessage type="error" :message="profileError" />
              <AlertMessage type="success" :message="profileSuccess" />
              
              <SubmitButton
                :loading="profileLoading"
                text="保存修改"
                icon="save"
              />
            </form>
          </div>
          
          <!-- 修改密码 -->
          <div class="bg-white rounded-xl shadow p-8">
            <h2 class="text-lg font-semibold text-gray-900 mb-6 pb-3 border-b-2 border-gray-200">修改密码</h2>
            
            <form @submit.prevent="handleChangePassword">
              <FormInput
                v-model="passwordForm.oldPassword"
                label="当前密码"
                type="password"
                placeholder="请输入当前密码"
                autocomplete="current-password"
                :required="true"
              />
              
              <div class="grid grid-cols-2 gap-5 mt-5">
                <FormInput
                  v-model="passwordForm.newPassword"
                  label="新密码"
                  type="password"
                  placeholder="至少8位"
                  autocomplete="new-password"
                  :required="true"
                />
                
                <FormInput
                  v-model="passwordForm.confirmPassword"
                  label="确认新密码"
                  type="password"
                  placeholder="再次输入新密码"
                  autocomplete="new-password"
                  :required="true"
                />
              </div>
              
              <AlertMessage type="error" :message="passwordError" />
              <AlertMessage type="success" :message="passwordSuccess" />
              
              <SubmitButton
                :loading="passwordLoading"
                text="修改密码"
                icon="password"
              />
            </form>
          </div>
          
          <!-- 账号信息 -->
          <div class="bg-white rounded-xl shadow p-8">
            <h2 class="text-lg font-semibold text-gray-900 mb-6 pb-3 border-b-2 border-gray-200">账号信息</h2>
            
            <div class="grid gap-0">
              <InfoRow
                label="用户名"
                :value="authStore.user?.username || ''"
              />
              <InfoRow
                label="角色"
                :value="authStore.isAdmin ? '管理员' : '普通用户'"
              />
              <InfoRow
                label="账号状态"
                value="正常"
                :badge="true"
              />
              <InfoRow
                label="注册时间"
                :value="authStore.user?.created_at?.split('T')[0] || '2024-01-01'"
                :is-last="true"
              />
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>
