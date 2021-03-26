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
    .directive('click-outside', {
        beforeMount(el, binding) {
            el.clickOutsideEvent = function(event) {
                if (!(el === event.target || el.contains(event.target))) {
                binding.value(event, el);
                }
            };
            document.body.addEventListener('click', el.clickOutsideEvent);
        },
        unmounted(el) {
            document.body.removeEventListener('click', el.clickOutsideEvent);
        }
    })
    .provide('currency', {
        name: 'Philippine Peso',
        abbreviation: 'PHP',
        symbol: '₱'
    })
    .mount('#app')