<script setup lang="ts">
interface Props {
  show: boolean
  title: string
  width?: string
}

defineProps<Props>()

const emit = defineEmits<{
  'update:show': [value: boolean]
  close: []
}>()

function handleClose() {
  emit('update:show', false)
  emit('close')
}
</script>

<template>
  <div v-if="show" class="modal-overlay" @click.self="handleClose">
    <div class="modal" :style="{ width: width || '600px' }">
      <div class="modal-header">
        <h3 class="modal-title">{{ title }}</h3>
        <button @click="handleClose" class="modal-close" style="background: none; border: none; color: var(--gray-400); cursor: pointer; padding: 0;">
          <svg style="width: 24px; height: 24px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>
      <div class="modal-body">
        <slot></slot>
      </div>
      <div v-if="$slots.footer" class="modal-footer">
        <slot name="footer"></slot>
      </div>
    </div>
  </div>
</template>
