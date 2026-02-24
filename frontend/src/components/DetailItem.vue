<script setup lang="ts">
defineProps<{
  label: string
  value: string
  colorClass?: string
  sizeClass?: string
}>()
</script>

<template>
  <div class="detail-item">
    <span class="detail-label">{{ label }}</span>
    <span class="detail-value" :class="[sizeClass || '', colorClass || '']">{{ value }}</span>
  </div>
</template>
