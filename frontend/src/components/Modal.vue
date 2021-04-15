<template>
    <teleport to="body">
        <transition name="slide-fade">
            <div class="fixed overflow-y-auto inset-0 bg-gray-900 bg-opacity-30" 
                v-if="$props.isOpen">
                <div class="flex overflow-y-auto items-center justify-center min-h-screen">
                    <div class="modal">
                        <header class="modal-header">
                            <h1 class="flex-grow">{{$props.heading}}</h1>
                            <button>
                                <Icon id="close" @click="close"/>
                            </button>
                        </header>
                        <div class="modal-body pb-6 pb-12" 
                            :style="styleHeight" >
                            <slot/>
                        </div>
                        <footer class="modal-footer border-gray-300 border-t justify-end flex-wrap">
                            <Button v-for="(button, index) in $props.buttons" 
                                :key="index" :type="button.type" 
                                :color="button.color" :disabled="button.disabled"
                                :icon="button.icon" :action="button.action" 
                                class="modal-button">
                                {{button.text}}
                            </Button>
                            <Button color="secondary" 
                                icon="close" 
                                class="modal-button"
                                :action="close">
                                Close
                            </Button>
                        </footer>
                    </div>
                </div>
            </div>
        </transition>
    </teleport>
</template>

<script>
import {reactive, toRefs, watch, onMounted, onUnmounted, nextTick} from 'vue' 
import Icon from '@/components/Icon.vue'
import Button from '@/components/Button.vue'

export default {
    components: {
        Icon, Button
    },
    emits: ['toggle'],
    props: {
        isOpen: Boolean,
        heading: {
            type: String,
            required: true
        },
        buttons: {
            type: Array,
            required: false
        }
    }, 
    setup(props, {emit}) {
        const modal = reactive({
            ref: {}, styleHeight: null, 
        });
        const resize = () => {
            let h = window.innerHeight * 0.8;
            if (modal.ref && modal.ref.clientHeight > h) {
                modal.styleHeight = {height: h + 'px'};
            } else {
                modal.styleHeight = null;
            }
        }
        onMounted(()=> {
            window.addEventListener('resize', resize);
        });
        onUnmounted(()=> {
            window.removeEventListener('resize', resize);
        });
        watch(()=> props.isOpen, ()=> { 
            const bodyClassList = document.querySelector('body').classList;
            if (props.isOpen) {
                bodyClassList.add('overflow-hidden');
                nextTick(()=> resize());
            } else {
                bodyClassList.remove('overflow-hidden');
            }
        });
        return {
            ...toRefs(modal),
            close: ()=> emit('toggle', false)
        };
    }
}
</script>

<style scoped>
@layer components {
    .modal {
        @apply w-11/12 sm:w-4/5 md:w-3/5;
        @apply rounded bg-white;
    }
    .modal-header {
        @apply bg-primary;
        @apply rounded-t;
    }
    .modal-body, .modal-footer, .modal-header {
       @apply w-full px-6;
    }
    .modal-footer, .modal-header {
        @apply py-4;
        @apply flex my-auto;
    }
    .modal-button {
        @apply my-1;
    }
    .modal-button:first-child {
        @apply mr-1;
    }
    .modal-button:last-child {
        @apply ml-1;
    }
    .modal-button:not(:first-child):not(:last-child) {
        @apply mx-1;
    }
    .slide-fade-enter-from,
    .slide-fade-leave-to {
        opacity: 0;
    }
    .slide-fade-enter-from .modal, 
    .slide-fade-leave-to .modal {
        transform: translateY(-40px);
    }
    .slide-fade-enter-active,
    .slide-fade-leave-active,
    .slide-fade-enter-from .modal, 
    .slide-fade-leave-to .modal {
        transition: all 0.1s ease-out;
    }
}
</style>