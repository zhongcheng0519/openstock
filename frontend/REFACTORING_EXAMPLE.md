# Component Refactoring Example: LoginView

## Before Refactoring (125 lines)

```vue
<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { APP_CONFIG } from '@/config/app'

// ... logic code ...
</script>

<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-card">
        <!-- Logo section ... -->
        
        <form @submit.prevent="handleLogin" class="login-form">
          <!-- Username Input - 15 lines -->
          <div class="form-group">
            <label class="label label-required">
              用户名
            </label>
            <div class="input-wrapper">
              <svg class="input-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
              </svg>
              <input
                v-model="username"
                type="text"
                class="input input-with-icon"
                placeholder="请输入用户名"
                autocomplete="username"
              />
            </div>
          </div>
          
          <!-- Password Input - 15 lines -->
          <div class="form-group">
            <label class="label label-required">
              密码
            </label>
            <div class="input-wrapper">
              <svg class="input-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
              </svg>
              <input
                v-model="password"
                type="password"
                class="input input-with-icon"
                placeholder="请输入密码"
                autocomplete="current-password"
              />
            </div>
          </div>
          
          <!-- Error Message - 3 lines -->
          <div v-if="errorMessage" class="error-message">
            <p>{{ errorMessage }}</p>
          </div>
          
          <!-- Submit Button - 18 lines -->
          <button
            type="submit"
            :disabled="loading"
            class="btn btn-primary btn-lg w-full"
          >
            <svg v-if="loading" class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"></path>
            </svg>
            {{ loading ? '登录中...' : '登录' }}
          </button>
        </form>
        
        <!-- ... -->
      </div>
    </div>
  </div>
</template>
```

**Issues:**
- 51 lines of repetitive form input markup
- Duplicate SVG icons
- Inline error message styling
- Complex button with loading state logic

## After Refactoring (90 lines)

```vue
<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { APP_CONFIG } from '@/config/app'
import FormField from '@/components/FormField.vue'
import AlertMessage from '@/components/AlertMessage.vue'

// ... same logic code ...
</script>

<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-card">
        <!-- Logo section ... -->
        
        <form @submit.prevent="handleLogin" class="login-form">
          <!-- Username Input - 1 component! -->
          <FormField
            v-model="username"
            label="用户名"
            type="text"
            placeholder="请输入用户名"
            autocomplete="username"
            icon="user"
            required
          />
          
          <!-- Password Input - 1 component! -->
          <FormField
            v-model="password"
            label="密码"
            type="password"
            placeholder="请输入密码"
            autocomplete="current-password"
            icon="password"
            required
          />
          
          <!-- Error Message - 1 component! -->
          <AlertMessage v-if="errorMessage" type="error" :message="errorMessage" />
          
          <!-- Submit Button - Still inline, but could be componentized further -->
          <button
            type="submit"
            :disabled="loading"
            class="btn btn-primary btn-lg w-full"
          >
            <!-- ... same button content ... -->
          </button>
        </form>
        
        <!-- ... -->
      </div>
    </div>
  </div>
</template>
```

**Improvements:**
- ✅ 35 lines reduced (28% reduction)
- ✅ Form inputs now use reusable `FormField` component
- ✅ Error message uses `AlertMessage` component
- ✅ Icon logic abstracted into component
- ✅ Consistent styling across all forms
- ✅ Easier to maintain and test
- ✅ Better type safety with TypeScript props

## Component Code Example: FormField.vue

```vue
<script setup lang="ts">
interface Props {
  modelValue?: string | number | null
  label?: string
  type?: string
  placeholder?: string
  required?: boolean
  icon?: 'user' | 'password' | 'email' | 'phone'
  // ... other props
}

defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>

<template>
  <div class="form-group">
    <label v-if="label" class="label" :class="{ 'label-required': required }">
      {{ label }}
    </label>
    <div v-if="icon" class="input-wrapper">
      <svg class="input-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="icons[icon]"></path>
      </svg>
      <input
        :value="modelValue"
        @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
        :type="type || 'text'"
        :placeholder="placeholder"
        class="input input-with-icon"
      />
    </div>
    <!-- Non-icon input variant -->
  </div>
</template>
```

**Benefits:**
- ✅ Single source of truth for form inputs
- ✅ Reusable across all forms (LoginView, RegisterView, UsersView, etc.)
- ✅ Icon paths stored in component, not duplicated
- ✅ Consistent v-model binding
- ✅ Type-safe props

## Real-World Usage Across Views

### LoginView (2 inputs)
```vue
<FormField v-model="username" label="用户名" icon="user" required />
<FormField v-model="password" label="密码" type="password" icon="password" required />
```

### RegisterView (6 inputs)
```vue
<FormField v-model="form.username" label="用户名" required />
<FormField v-model="form.nickname" label="昵称" required />
<FormField v-model="form.password" label="密码" type="password" required />
<FormField v-model="form.confirmPassword" label="确认密码" type="password" required />
<FormField v-model="form.email" label="邮箱" type="email" required />
<FormField v-model="form.phone" label="手机号" type="tel" :maxlength="11" />
```

### UsersView Modal (4 inputs)
```vue
<FormField v-model="createForm.username" label="用户名" required />
<FormField v-model="createForm.nickname" label="昵称" required />
<FormField v-model="createForm.email" label="邮箱" type="email" required />
<FormField v-model="createForm.phone" label="手机号" type="tel" :maxlength="11" />
```

### LogsView Filters (4 inputs)
```vue
<FormField v-model="filterForm.user_id" label="用户ID" type="number" />
<FormField v-model="filterForm.start_date" label="开始时间" type="date" />
<FormField v-model="filterForm.end_date" label="结束时间" type="date" />
```

**Total Reuse:** Same component used 20+ times across the app, saving hundreds of lines!

## Key Takeaways

1. **DRY Principle**: Don't Repeat Yourself - one component, many uses
2. **Single Responsibility**: Each component does one thing well
3. **Composability**: Small, focused components that work together
4. **Maintainability**: Fix once, fix everywhere
5. **Type Safety**: TypeScript ensures correct usage
6. **Consistency**: Same look and behavior throughout the app
