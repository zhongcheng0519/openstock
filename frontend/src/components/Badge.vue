<script setup lang="ts">
interface Props {
  variant?: 'success' | 'danger' | 'warning' | 'info' | 'gray'
  text: string
}

defineProps<Props>()
</script>

<template>
  <span 
    class="badge"
    :class="{
      'badge-success': variant === 'success',
      'badge-danger': variant === 'danger',
      'badge-warning': variant === 'warning',
      'badge-info': variant === 'info',
      'badge-gray': variant === 'gray' || !variant
    }"
  >
    {{ text }}
  </span>
</template>
