<template>
    <div v-show="state.isActive">
        <slot/>
    </div>
</template>

<script>
import {reactive, inject, onBeforeMount, watch} from 'vue';

export default {
    name: 'Step',
    setup() {
        const state = reactive({
            index: 0,
            isActive: false
        });
        const stepsManager = inject('StepsManager');

        onBeforeMount(()=> {
            state.index = stepsManager.count++;
            state.isActive = stepsManager.selectedStep===state.index;
        });
        watch(()=>stepsManager.selectedStep, ()=> {
            state.isActive = stepsManager.selectedStep===state.index;
        });

        return {
            state
        }
    }
}
</script>