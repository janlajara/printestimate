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
    .directive('number', {
        beforeMount(el) { 
            el.inputEvent = function(event) {
                if (event.isCustom) return;
                const value = event.target.value;
                if (value != null) {
                    let replaced = value.replace(/[^\d]/g, '');
                    if (replaced != '') {
                        replaced = parseFloat(replaced)
                        if (el.min != null && replaced < parseFloat(el.min)) replaced = el.min;
                        else if (el.max != null && replaced > parseFloat(el.max)) replaced = el.max;
                    }
                    event.target.value = replaced; 
                    const ev = new CustomEvent('input', {
                        isCustom: true,
                        target: {value: replaced}});
                    el.dispatchEvent(ev);
                }
            }
            document.body.addEventListener('input', el.inputEvent);
        },
        unmounted(el) {
            document.body.removeEventListener('input', el.inputEvent);
        }
    })
    .provide('currency', {
        name: 'Philippine Peso',
        abbreviation: 'PHP',
        symbol: '₱'
    })
    .mount('#app')