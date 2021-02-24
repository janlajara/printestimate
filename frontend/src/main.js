import 'tailwindcss/tailwind.css'
import './assets/index.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

import Toast from 'vue-toastification'
import 'vue-toastification/dist/index.css'
import './assets/toasts.css'

createApp(App)
    .use(router)
    .use(Toast, {
        hideProgressBar: true,
        position: 'bottom-right'
    })
    .mount('#app')