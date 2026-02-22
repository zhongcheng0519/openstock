<script setup lang="ts">
interface Props {
  initial: string
  nickname: string
  username: string
  isAdmin: boolean
}

defineProps<Props>()
</script>

<template>
  <div class="bg-white rounded-xl shadow p-8 text-center">
    <div class="w-20 h-20 bg-gradient-to-br from-red-600 to-red-400 rounded-full inline-flex items-center justify-center text-white font-bold text-[2rem] mb-5 shadow-md">
      {{ initial }}
    </div>
    <div class="text-xl font-semibold text-gray-900 mb-1">{{ nickname }}</div>
    <div class="text-sm text-gray-500 mb-5">@{{ username }}</div>
    <span 
      class="inline-flex px-[0.875rem] py-1.5 text-[0.8125rem] font-medium rounded-full"
      :class="isAdmin ? 'bg-red-50 text-red-600' : 'bg-gray-100 text-gray-600'"
    >
      {{ isAdmin ? '管理员' : '普通用户' }}
    </span>
  </div>
</template>
