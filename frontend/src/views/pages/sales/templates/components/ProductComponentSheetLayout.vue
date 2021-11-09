<template>
    <div class="mt-4 grid w-full">
        <div class="flex justify-end">
            <Button icon="dashboard" :action="state.hideToggle">
                {{state.isHidden? 'Show': 'Hide' }} Layout</Button>
        </div>
        <div :class="[state.isHidden? 'hidden' : '', '']">
            <CutListLayout/>
        </div>
    </div>
</template>

<script>
import Button from '@/components/Button.vue';
import CutListLayout from '@/views/commons/CutListLayout.vue';

import {reactive, watch, watchEffect} from 'vue';
import {SheetFedPressMachineApi} from '@/utils/apis.js';

export default {
    components: {
        Button, CutListLayout
    },
    props: {
        materialLayout: Object,
        itemLayout: Object
    },
    setup(props) {
        const state = reactive({
            isHidden: true,
            hideToggle: ()=> {
                state.isHidden = !state.isHidden;
            },
            materialLayout: null,
            itemLayout: null
        });
    
        const getSheetLayout = (input) => {
            if (input) {
                const response = SheetFedPressMachineApi.getSheetLayout(input);
                if (response) console.log(response);
            }
        };

        watch(()=>props.materialLayout, ()=> {
            state.materialLayout = props.materialLayout;
        });
        watch(()=>props.itemLayout, ()=> {
            state.itemLayout = props.itemLayout;
        });
        watchEffect(()=> {
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
                getSheetLayout(input);
            }
        });

        return {
            state
        }
    }
}
</script>