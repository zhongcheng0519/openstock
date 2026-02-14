import { createRouter, createWebHistory } from 'vue-router'
import StockFilterView from '../views/StockFilterView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'stock-filter',
      component: StockFilterView,
    },
  ],
})

export default router
