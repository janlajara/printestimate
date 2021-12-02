<template>
    <div class="mt-4 grid w-full">
        <div>
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
import ProductComponentSheetLayout from './ProductComponentSheetLayout.vue';

import {reactive, computed} from 'vue';

export default {
    components: {
        Tabs, Tab, ProductComponentSheetLayout, 
    },
    props: {
        machineId: Number,
        materialLayout: Object,
        itemLayouts: Array
    },
    setup(props) {
        const state = reactive({
            data: {
                machineId: computed(()=>props.machineId),
                materialLayout: computed(()=>props.materialLayout),
                itemLayouts: computed(()=>props.itemLayouts)
            }
        });
        return {
            state
        }
    }
}
</script>