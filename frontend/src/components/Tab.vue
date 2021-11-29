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
import {ref, inject, watch, onBeforeMount, getCurrentInstance} from 'vue';

export default {
    name: 'Tab',
    setup(){
        const index = ref(0);
        const tabs = inject('TabsManager');
        const isActive = ref(false);
        const refresh = ref(true);

        onBeforeMount(()=>{
            isActive.value = tabs.selectedIndex===index.value;
            refresh.value = tabs.refresh;
            index.value = getCurrentInstance().vnode.key;
        })

        watch(()=> tabs.selectedIndex,
            ()=> {
                isActive.value = tabs.selectedIndex===index.value;
            }
        )

        return {
            index, isActive, refresh
        }
    }
}
</script>