import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { authApi, type UserResponse } from '@/api/client'

const TOKEN_KEY = 'access_token'
const USER_KEY = 'user_info'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem(TOKEN_KEY))
  const user = ref<UserResponse | null>(null)
  
  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const userInitial = computed(() => user.value?.nickname?.charAt(0).toUpperCase() || 'U')
  
  function loadUserFromStorage() {
    const storedUser = localStorage.getItem(USER_KEY)
    if (storedUser) {
      try {
        user.value = JSON.parse(storedUser)
      } catch {
        user.value = null
      }
    }
  }
  
  function setToken(newToken: string) {
    token.value = newToken
    localStorage.setItem(TOKEN_KEY, newToken)
  }
  
  function setUser(newUser: UserResponse) {
    user.value = newUser
    localStorage.setItem(USER_KEY, JSON.stringify(newUser))
  }
  
  function clearAuth() {
    token.value = null
    user.value = null
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  }
  
  async function login(username: string, password: string) {
    const response = await authApi.login({ username, password })
    setToken(response.data.access_token)
    setUser(response.data.user)
    return response.data
  }
  
  async function register(data: {
    username: string
    nickname: string
    password: string
    email: string
    phone?: string
  }) {
    const response = await authApi.register(data)
    return response.data
  }
  
  async function logout() {
    try {
      await authApi.logout()
    } catch {
      // ignore
    }
    clearAuth()
  }
  
  async function fetchCurrentUser() {
    if (!token.value) return null
    try {
      const response = await authApi.getMe()
      setUser(response.data)
      return response.data
    } catch {
      clearAuth()
      return null
    }
  }
  
  async function updateProfile(data: {
    nickname: string
    email: string
    phone?: string
  }) {
    const response = await authApi.updateProfile(data)
    setUser(response.data)
    return response.data
  }
  
  async function changePassword(oldPassword: string, newPassword: string) {
    await authApi.changePassword({ old_password: oldPassword, new_password: newPassword })
  }
  
  loadUserFromStorage()
  
  return {
    token,
    user,
    isLoggedIn,
    isAdmin,
    userInitial,
    setToken,
    setUser,
    clearAuth,
    login,
    register,
    logout,
    fetchCurrentUser,
    updateProfile,
    changePassword,
  }
})
