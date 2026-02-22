<script setup lang="ts">
interface Props {
  variant?: 'primary' | 'secondary' | 'danger'
  type?: 'button' | 'submit' | 'reset'
  disabled?: boolean
  loading?: boolean
  icon?: string
}

const props = defineProps<Props>()
</script>

<template>
  <button
    :type="type || 'button'"
    :disabled="disabled || loading"
    class="btn"
    :class="{
      'btn-primary': variant === 'primary' || !variant,
      'btn-secondary': variant === 'secondary',
      'btn-danger': variant === 'danger'
    }"
  >
    <svg v-if="loading" class="animate-spin w-[18px] h-[18px]" fill="none" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
    <svg v-else-if="icon" style="width: 18px; height: 18px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="icon"></path>
    </svg>
    <slot></slot>
  </button>
</template>
