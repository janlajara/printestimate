import { createRouter, createWebHashHistory } from 'vue-router'
import Admin from '@/views/Admin.vue'

const routes = [
  {
    path: '/',
    name: 'Admin',
    component: Admin,
    children: [
      {
        path: '/',
        name: 'home',
        component: ()=>import('../views/pages/Home.vue')
      },
      {
        path: 'inventory/',
        name: 'inventory-dashboard',
        component: ()=>import('../components/Placeholder.vue'),
        meta: {label: 'Dashboard', group: 'Inventory'}
      },
      {
        path: 'inventory/stock',
        name: 'inventory-stock',
        component: ()=>import('../views/pages/inventory/Stock.vue'),
        meta: {label: 'Stock', group: 'Inventory'}
      },
      {
        path: 'admin/inventory',
        name: 'admin-inventory',
        component: ()=>import('../views/admin/inventory/Inventory.vue')
      },
      {
        path: 'admin/estimation',
        name: 'admin-estimation',
        component: ()=>import('../views/admin/Estimation.vue')
      },
    ]
  },
  {
    path: '/pages/login',
    name: 'Login',
    component: ()=>import('../views/pages/Login.vue'),
    meta: {group: 'Pages'}
  },
  {
    path: '/pages/404',
    name: 'Not Found',
    component: ()=>import('../views/pages/NotFound.vue'),
    meta: {group: 'Pages'}
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router
