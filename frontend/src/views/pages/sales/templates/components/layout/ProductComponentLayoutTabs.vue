<template>
    <div class="mt-4 grid w-full">
        <div v-if="state.data.rawMaterialLayouts != null && state.data.finalMaterialLayout != null">
            <Tabs :refresh="false">
                <Tab v-for="(rawMaterialLayout, key) in state.data.rawMaterialLayouts" :key="key"
                        :title="rawMaterialLayout.label">
                    <ProductComponentPaperLayout
                        :copy-quantity="$props.copyQuantity"
                        :machine="state.data.machine"
                        :raw-material-layout="rawMaterialLayout"
                        :final-material-layout="state.data.finalMaterialLayout"/>
                </Tab>
            </Tabs>
        </div>
    </div>
</template>
<script>
import Tabs from '@/components/Tabs.vue';
import Tab from '@/components/Tab.vue';
import ProductComponentPaperLayout from './ProductComponentPaperLayout.vue';

import {reactive, computed} from 'vue';

export default {
    components: {
        Tabs, Tab, ProductComponentPaperLayout, 
    },
    props: {
        machine: Object,
        finalMaterialLayout: Object,
        rawMaterialLayouts: Array,
        copyQuantity: Number
    },
    setup(props) {
        const state = reactive({
            data: {
                machine: computed(()=>props.machine),
                finalMaterialLayout: computed(()=>props.finalMaterialLayout),
                rawMaterialLayouts: computed(()=>props.rawMaterialLayouts)
            }
        });
        return {
            state
        }
    }
}
</script>