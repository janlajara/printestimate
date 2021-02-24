<template>
    <div v-show="isActive">
        <slot/>
    </div>
</template>

<script>
import {ref, inject, watch, onBeforeMount} from 'vue' 

export default {
    name: 'Tab',
    setup(){
        const index = ref(0)
        const tabs = inject('TabsManager')
        const isActive = ref(false)

        onBeforeMount(()=>{
            index.value = tabs.count++
            isActive.value = tabs.selectedIndex===index.value
        })

        watch(()=> tabs.selectedIndex,
            ()=> {
                isActive.value = tabs.selectedIndex===index.value
            }
        )

        return {
            index, isActive
        }
    }
}
</script>