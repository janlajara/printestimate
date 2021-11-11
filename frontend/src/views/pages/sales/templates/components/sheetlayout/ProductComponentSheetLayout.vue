<template>
    <CutListLayout/>
</template>

<script>
import CutListLayout from '@/views/commons/CutListLayout.vue';

import {reactive, watchEffect} from 'vue';
import {SheetFedPressMachineApi} from '@/utils/apis.js';

export default {
    components: {
        CutListLayout
    },
    props: {
        machineId: Number,
        materialLayout: Object,
        itemLayout: Object
    },
    setup(props) {
        const state = reactive({
            machineId: props.machineId,
            materialLayout: props.materialLayout,
            itemLayout: props.itemLayout
        });
    
        const getSheetLayout = async (machineId, input) => {
            if (input) {
                const response = await SheetFedPressMachineApi.getSheetLayout(
                    machineId, input);
                if (response) console.log(response);
            }
        };

        watchEffect(async ()=> {
            if (state.materialLayout && state.itemLayout) {
                const input = {
                    material_layout: {
                        width: state.materialLayout.width,
                        length: state.materialLayout.length,
                        uom: state.materialLayout.uom
                    },
                    item_layout: {
                        width: state.itemLayout.width,
                        length: state.itemLayout.length,
                        uom: state.itemLayout.uom
                    },
                    bleed: false,
                    rotate: true
                };
                console.log(input);
                if (state.machineId) await getSheetLayout(state.machineId, input);
            }
        });

        return {
            state
        }
    }
}
</script>