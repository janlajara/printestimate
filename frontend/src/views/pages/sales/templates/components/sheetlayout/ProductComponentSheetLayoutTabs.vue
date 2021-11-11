<template>
    <div class="mt-4 grid w-full">
        <div class="flex justify-end">
            <Button icon="dashboard" :action="state.hideToggle">
                {{state.isHidden? 'Show': 'Hide' }} Layout</Button>
        </div>
        <div :class="[state.isHidden? 'hidden' : '', '']">
            <Tabs :refresh="false">
                <Tab v-for="(item_layout, key) in state.data.itemLayouts" :key="key"
                        :title="`Material #`+(key+1)">
                    <ProductComponentSheetLayout
                        :machine-id="state.data.machineId"
                        :item-layout="item_layout"
                        :material-layout="state.data.materialLayout"/>
                </Tab>
            </Tabs>
        </div>
    </div>
</template>
<script>
import Tabs from '@/components/Tabs.vue';
import Tab from '@/components/Tab.vue';
import Button from '@/components/Button.vue';
import ProductComponentSheetLayout from './ProductComponentSheetLayout.vue';

import {reactive} from 'vue';

export default {
    components: {
        Tabs, Tab, Button, ProductComponentSheetLayout
    },
    props: {
        machineId: Number,
        materialLayout: Object,
        itemLayouts: Array
    },
    setup(props) {
        const state = reactive({
            isHidden: true,
            data: {
                machineId: props.machineId,
                materialLayout: props.materialLayout,
                itemLayouts: props.itemLayouts
            },
            hideToggle: ()=> {
                state.isHidden = !state.isHidden;
            },
        });
        return {
            state
        }
    }
}
</script>