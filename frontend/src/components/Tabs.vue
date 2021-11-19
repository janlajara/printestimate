<template>
    <div>
        <ul class="border-gray-300 border-b mt-2 mb-6 hidden sm:flex">
            <li v-for="(tab, index) in tabs" :key="index"
                @click="selectTab(index)"
                class="tab cursor-pointer" 
                :class="index === selectedIndex? 
                    'text-primary border-primary font-bold border-b-4' : ''">
                {{tab.props.title}}
            </li>
        </ul>

        <div class="border-primary border-b-4 sm:hidden my-4">
            <select v-model="selectedIndex" 
                class="w-full border-gray-300 border-b-0 pl-0">
                <option v-for="(tab, index) in tabs" :key="index" :value="index">
                    {{tab.props.title}}
                </option>
            </select>
        </div>
        <slot/>
    </div>
</template>

<script>
import {reactive, toRefs, onBeforeMount, onMounted, provide, watch} from 'vue'

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
            selectedIndex: 0,
            tabs: [],
            count: 0
        })

        const selectTab = (index) => {
            state.selectedIndex = index
        }

        const getTabs = () => {
            const slot_content = slots.default(); 
            let tabs = slot_content.filter(child => child.type.name==='Tab');
            if (tabs.length == 0 && slot_content[0] != null) {
                tabs = slot_content[0].children.filter( child => child.type.name==='Tab');
            }
            state.tabs = tabs;
        }

        provide('TabsManager', state)
        onBeforeMount(()=> {
            if (slots.default) {
                getTabs();
            }
        });
        onMounted(()=> selectTab(0));
        watch(()=> slots.default(), ()=> {
            getTabs();
            if (state.tabs.length > 0) state.selectedIndex = 0;
            state.tabs.count = 0;
        });


        return {
            ...toRefs(state), selectTab
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