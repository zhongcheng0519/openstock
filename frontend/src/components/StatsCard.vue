<script setup lang="ts">
interface Props {
  label: string
  value: string | number
}

defineProps<Props>()
</script>

<template>
  <div class="stat-card">
    <div class="stat-label">{{ label }}</div>
    <div class="stat-value">{{ value }}</div>
  </div>
</template>
