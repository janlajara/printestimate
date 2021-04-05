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
        path: 'inventory/stocks',
        name: 'inventory-stocks',
        component: ()=>import('../views/pages/inventory/stock/ItemList.vue'),
        meta: {label: 'Stocks', group: 'Inventory'}
      },
      {
        path: 'inventory/stocks/:id',
        name: 'inventory-stock-detail',
        props: true,
        component: ()=>import('../views/pages/inventory/stock/ItemDetail.vue'),
      },
      {
        path: 'inventory/stockrequests',
        name: 'inventory-stockrequests',
        component: ()=>import('../views/pages/inventory/stockrequest/StockRequestGroupList.vue'),
        meta: {label: 'Stock Requests', group: 'Inventory'}
      },
      {
        path: 'inventory/stockrequests/:id',
        name: 'inventory-stockrequest-detail',
        props: true,
        component: ()=>import('../views/pages/inventory/stockrequest/StockRequestGroupDetail.vue'),
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
