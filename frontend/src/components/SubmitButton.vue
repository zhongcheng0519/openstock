<script setup lang="ts">
interface Props {
  loading: boolean
  text: string
  icon?: 'save' | 'password'
}

defineProps<Props>()
</script>

<template>
  <button
    type="submit"
    :disabled="loading"
    class="mt-6 inline-flex items-center gap-2 px-5 py-2.5 bg-red-600 hover:bg-red-700 hover:shadow-md hover:-translate-y-0.5 text-white text-sm font-medium rounded-lg transition-all disabled:opacity-50 disabled:hover:translate-y-0 border-0 cursor-pointer"
  >
    <!-- Save Icon -->
    <svg v-if="!loading && icon === 'save'" class="w-[18px] h-[18px]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
    </svg>
    
    <!-- Password Icon -->
    <svg v-if="!loading && icon === 'password'" class="w-[18px] h-[18px]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"></path>
    </svg>
    
    <!-- Loading Spinner -->
    <svg v-if="loading" class="animate-spin w-[18px] h-[18px]" fill="none" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
    
    {{ text }}
  </button>
</template>
