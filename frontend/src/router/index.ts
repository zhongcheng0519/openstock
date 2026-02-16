import { createRouter, createWebHistory } from 'vue-router'
import StockFilterView from '../views/StockFilterView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import ProfileView from '../views/ProfileView.vue'
import UsersView from '../views/UsersView.vue'
import LogsView from '../views/LogsView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'stock-filter',
      component: StockFilterView,
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { guest: true }
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
      meta: { guest: true }
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView,
      meta: { requiresAuth: true }
    },
    {
      path: '/users',
      name: 'users',
      component: UsersView,
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/logs',
      name: 'logs',
      component: LogsView,
      meta: { requiresAuth: true, requiresAdmin: true }
    },
  ],
})

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('access_token')
  const userStr = localStorage.getItem('user_info')
  let isAdmin = false
  
  if (userStr) {
    try {
      const user = JSON.parse(userStr)
      isAdmin = user.role === 'admin'
    } catch {
      // ignore
    }
  }
  
  if (to.meta.requiresAuth && !token) {
    next({ name: 'login' })
  } else if (to.meta.requiresAdmin && !isAdmin) {
    next({ name: 'stock-filter' })
  } else if (to.meta.guest && token) {
    next({ name: 'stock-filter' })
  } else {
    next()
  }
})

export default router
