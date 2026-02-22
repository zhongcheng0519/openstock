<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  password: string
}

const props = defineProps<Props>()

const strength = computed(() => {
  const pwd = props.password
  if (!pwd) return null
  
  let score = 0
  if (pwd.length >= 8) score++
  if (/[a-z]/.test(pwd) && /[A-Z]/.test(pwd)) score++
  if (/\d/.test(pwd)) score++
  if (/[^a-zA-Z0-9]/.test(pwd)) score++
  
  if (score <= 1) return { level: 'weak', text: 'Weak', color: 'text-red-500' }
  if (score <= 2) return { level: 'medium', text: 'Medium', color: 'text-yellow-500' }
  return { level: 'strong', text: 'Strong', color: 'text-green-500' }
})
</script>

<template>
  <div v-if="strength" class="password-strength" :class="'strength-' + strength.level">
    <div class="strength-bar">
      <div class="strength-fill"></div>
    </div>
    <span class="text-xs" :class="strength.color">{{ strength.text }}</span>
  </div>
</template>
