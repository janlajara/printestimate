<template>
    <div>
        <div v-if="state.refresh">
            <div v-if="state.isActive">
                <slot/>
            </div>
        </div>
        <div v-else>
            <div :class="state.isActive? '': 'invisible absolute'">
                <slot/>
            </div>
        </div>
    </div>
</template>

<script>
import {reactive, inject, computed} from 'vue';

export default {
    name: 'Tab',
    props: {
        title: {type: String, default: ''}
    },
    setup(props){
        const state = reactive({
            title: props.title,
            tabs: inject('TabsManager'),
            isActive: computed(()=> {
                return state.tabs.selectedTab===props.title;
            }),
            refresh: computed(()=>{
                return state.tabs.refresh
            })
        });

        return {
            state
        }
    }
}
</script>