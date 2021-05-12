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
        path: 'inventory/items',
        name: 'inventory-items',
        component: ()=>import('../views/pages/inventory/items/ItemList.vue'),
        meta: {label: 'Items', group: 'Inventory'}
      },
      {
        path: 'inventory/items/:id',
        name: 'inventory-item-detail',
        props: true,
        component: ()=>import('../views/pages/inventory/items/ItemDetail.vue'),
      },
      {
        path: 'inventory/itemrequests',
        name: 'inventory-itemrequests',
        component: ()=>import('../views/pages/inventory/itemrequests/ItemRequestGroupList.vue'),
        meta: {label: 'Item Requests', group: 'Inventory'}
      },
      {
        path: 'inventory/itemrequests/:id',
        name: 'inventory-itemrequest-detail',
        props: true,
        component: ()=>import('../views/pages/inventory/itemrequests/ItemRequestGroupDetail.vue')
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
