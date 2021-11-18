<template>
    <CutListLayout :layouts="state.data.sheetLayouts"/>
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
            data: {
                sheetLayouts: []
            }
        });
    
        const getSheetLayouts = async (machineId, input) => {
            if (input && inputIsValid(input)) {
                const response = await SheetFedPressMachineApi.getSheetLayout(
                    machineId, input);
                if (response) return response || [];
            }
        };

        const inputIsValid = (input) => {
            let isValid = false;
            if (input) {
                const materialLayout = input.material_layout;
                const materialLayoutIsValid = materialLayout.width > 0 &&
                    materialLayout.length > 0 && materialLayout.uom != null;

                const itemLayout = input.item_layout;
                const itemLayoutIsValid = itemLayout.width > 0 && 
                    itemLayout.length > 0 && itemLayout.uom != null;

                isValid = materialLayoutIsValid && itemLayoutIsValid;
            }
            return isValid;
        }

        watchEffect(async ()=> {
            if (props.materialLayout && props.itemLayout) {
                const input = {
                    material_layout: {
                        width: props.materialLayout.width,
                        length: props.materialLayout.length,
                        uom: props.materialLayout.uom
                    },
                    item_layout: {
                        width: props.itemLayout.width,
                        length: props.itemLayout.length,
                        uom: props.itemLayout.uom
                    },
                    bleed: false,
                    rotate: true
                };
                if (props.machineId) {
                    state.data.sheetLayouts = await getSheetLayouts(
                        props.machineId, input);
                }
            }
        });

        return {
            state
        }
    }
}
</script>