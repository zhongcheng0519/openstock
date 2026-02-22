<script setup lang="ts">
interface Props {
  label: string
  value: string
  badge?: boolean
  isLast?: boolean
}

defineProps<Props>()
</script>

<template>
  <div 
    class="flex justify-between py-4"
    :class="{ 'border-b border-gray-200': !isLast }"
  >
    <span class="text-sm text-gray-500">{{ label }}</span>
    <span 
      v-if="!badge"
      class="text-sm font-medium text-gray-900"
    >
      {{ value }}
    </span>
    <span 
      v-else
      class="inline-flex px-2.5 py-1 text-xs font-medium bg-green-100 text-green-700 rounded-full"
    >
      {{ value }}
    </span>
  </div>
</template>
