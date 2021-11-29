<template>
    <div>
        <div v-if="refresh">
            <div v-if="isActive">
                <slot/>
            </div>
        </div>
        <div v-else>
            <div v-show="isActive">
                <slot/>
            </div>
        </div>
    </div>
</template>

<script>
import {ref, inject, computed, onBeforeMount, getCurrentInstance} from 'vue';

export default {
    name: 'Tab',
    setup(){
        const index = ref(0);
        const tabs = inject('TabsManager');
        const isActive = computed(()=> {
            return tabs.selectedIndex===index.value;
        });
        const refresh = ref(true);

        onBeforeMount(()=>{
            refresh.value = tabs.refresh;
            index.value = getCurrentInstance().vnode.key;
        })

        return {
            index, isActive, refresh
        }
    }
}
</script>