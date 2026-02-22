<script setup lang="ts">
interface Props {
  loading?: boolean
  empty?: boolean
  emptyText?: string
}

defineProps<Props>()
</script>

<template>
  <div class="table-container">
    <table class="table">
      <thead>
        <slot name="header"></slot>
      </thead>
      <tbody>
        <slot></slot>
      </tbody>
    </table>
    
    <div v-if="loading" class="p-8 text-center text-gray-500">
      Loading...
    </div>
    
    <div v-if="!loading && empty" class="p-8 text-center text-gray-500">
      {{ emptyText || 'No data available' }}
    </div>
  </div>
</template>
