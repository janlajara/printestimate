<template>
    <div ref="wrapper">
        <div class="border-gray-300 border-b mt-2 mb-6 overflow-x-auto
                hidden sm:grid gap-6 grid-flow-col auto-cols-max"
            :style="`width:${state.wrapperWidth}px`">
            <div v-for="(tab, index) in state.tabs" :key="index"
                @click="selectTab(tab.props.title)"
                class="py-4 cursor-pointer" 
                :class="tab.props.title === state.selectedTab? 
                    'text-primary border-primary font-bold border-b-4' : ''">
                <p class="truncate" :title="tab.props.title"
                        :style="tab.props.title === state.selectedTab?
                            '': `max-width: ${state.unselectedTabWidth}px`">
                    {{tab.props.title}}</p>
            </div>
        </div>
        <div class="border-primary border-b-4 sm:hidden my-4">
            <select v-model="state.selectedTab" 
                class="w-full border-gray-300 border-b-0 pl-0">
                <option v-for="(tab, index) in state.tabs" :key="index" 
                        :value="tab.props.title">
                    {{tab.props.title}}
                </option>
            </select>
        </div>
        <slot/>
    </div>
</template>

<script>
import {ref, reactive, onMounted, provide, watch, computed} from 'vue'

export default {
    name: 'Tabs',
    props: {
        refresh: {
            type: Boolean,
            default: true
        }
    },
    setup(props, {slots}) {
        const state = reactive({
            refresh: props.refresh,
            selectedTab: null,
            tabs: [],
            count: 0,
            wrapperWidth: 0,
            unselectedTabWidth: computed(()=> state.wrapperWidth/ 2 / Math.max(state.tabs.length, 1))
        })
        const wrapper = ref(null);

        const selectTab = (id) => {
            state.selectedTab = id;
        }

        const selectFirstTab = ()=> {
            if (state.tabs.length > 0) {
                const firstTabId = state.tabs[0].props.title;
                state.selectedTab = firstTabId;
            }
        }

        const getTabs = () => {
            if (slots.default) {
                const slot_content = slots.default(); 
                let tabs = slot_content.filter(child => child.type.name==='Tab');
                if (tabs.length == 0 && slot_content[0] != null) {
                    tabs = slot_content[0].children.filter( child => child.type.name==='Tab');
                }
                state.tabs = tabs;
                state.count = tabs.length;
            }
        }

        provide('TabsManager', state)
        onMounted(()=>{
            getTabs();
            selectFirstTab();
            state.wrapperWidth = wrapper.value.clientWidth;
            
        });
        watch(()=> slots.default(), ()=>{
            getTabs();
            selectFirstTab();
        });


        return {
            state, selectTab, wrapper
        }
    }
}
</script>

<style scoped>
@layer components {
    .tab {
        @apply py-4;
    }

    .tab:not(:first-child):not(:last-child) {
        @apply mx-6;
    }

    .tab:first-child {
        @apply mr-6;
    }

    .tab:last-child {
        @apply ml-6;
    }
}
</style>