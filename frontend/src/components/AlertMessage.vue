<script setup lang="ts">
interface Props {
  type: 'error' | 'success'
  message: string
}

defineProps<Props>()
</script>

<template>
  <div 
    v-if="message"
    class="mt-5 p-3 border rounded-lg"
    :class="type === 'error' ? 'bg-red-50 border-red-200' : 'bg-green-50 border-green-200'"
  >
    <p 
      class="text-sm"
      :class="type === 'error' ? 'text-red-600' : 'text-green-600'"
    >
      {{ message }}
    </p>
  </div>
</template>
