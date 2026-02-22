<script setup lang="ts">
interface Props {
  modelValue: string
  label: string
  type?: string
  placeholder?: string
  required?: boolean
  maxlength?: string
  autocomplete?: string
}

defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>

<template>
  <div class="form-input-wrapper">
    <label class="form-label">
      {{ label }} <span v-if="required" class="text-red-500">*</span>
    </label>
    <input
      :value="modelValue"
      @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
      :type="type || 'text'"
      :placeholder="placeholder"
      :required="required"
      :maxlength="maxlength"
      :autocomplete="autocomplete"
      class="w-full px-[0.875rem] py-2.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition-all placeholder:text-gray-400"
    />
  </div>
</template>

<style scoped>
.form-input-wrapper {
  margin-bottom: 1.25rem;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}
</style>
