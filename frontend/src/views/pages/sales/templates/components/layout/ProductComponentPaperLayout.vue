<template>
    <div>
        <CutListLayout :loader="state.isLoading"
            @load="value => state.data.stats = value"
            :layouts="state.data.sheetLayouts"/>
        <DescriptionList :class="`md:grid-cols-${state.meta.hasRunsheet? 3: 2}`">
            <DescriptionItem :name="`Total outs (${state.stats.childsheetSize})`" 
                :value="`${state.stats.childsheetPerParent} sheets / material`"/>
            <DescriptionItem v-if="state.meta.hasRunsheet"
                :name="`Runsheet (${state.stats.runsheetSize})`" 
                :value="`${state.stats.runsheetPerParent} sheets / material`"/>
            <DescriptionItem name="Wastage" 
                :value="`${formatNumber(state.stats.totalWasteage, 2, true)} %`"
                :class="(state.stats.totalWasteage > 20)? 'text-red-500 font-bold' : ''"/>
        </DescriptionList>
    </div>
</template>

<script>
import CutListLayout from '@/views/commons/sheetfedpress/CutListLayout.vue';
import DescriptionList from '@/components/DescriptionList.vue';
import DescriptionItem from '@/components/DescriptionItem.vue';

import convert from 'convert';
import {reactive, computed, watchEffect} from 'vue';
import {SheetFedPressMachineApi, RollFedPressMachineApi, ChildSheetApi} from '@/utils/apis.js';
import {formatNumber} from '@/utils/format.js';

export default {
    components: {
        CutListLayout, DescriptionList, DescriptionItem
    },
    props: {
        machine: Object,
        finalMaterialLayout: Object,
        rawMaterialLayout: Object,
    },
    setup(props) {
        const state = reactive({
            isLoading: false,
            data: {
                sheetLayouts: [],
                error: null,
                stats: null,
                layoutInputParams: {
                    sheetFedPress: {
                        rotate: true,
                        bleed: false
                    },
                    rollFedPress: {
                        orderQuantity: 50,
                        spoilageRate: 0,
                        applyBreakpoint: true
                    }
                }
            },
            meta: {
                hasRunsheet: computed(()=> 
                    state.data.sheetLayouts && state.data.sheetLayouts.length == 2)
            },
            stats: computed(()=> {
                let stats = {
                    runsheetSize: '',
                    runsheetPerParent: 0,
                    childsheetSize: '',
                    childsheetPerRunsheet: 0,
                    childsheetPerParent: 0,
                    totalUsage: 0, 
                    totalWasteage: 0,
                    totalCutCount: 0
                }
                if (state.data.stats && Object.keys(state.data.stats).length > 0) 
                    stats = state.data.stats;
                return stats;
            })
        });
    
        const getSheetLayouts = async (input, machine=null) => {
            if (input && inputIsValid(input)) {
                if (machine) {
                    let response = [];
                    state.isLoading = true;

                    if (machine.resourcetype == 'SheetFedPressMachine') {
                        response = await SheetFedPressMachineApi.getSheetLayout(
                            machine.id, input);
                    } else if (machine.resourcetype == 'RollFedPressMachine') {
                        response = await RollFedPressMachineApi.getSheetLayout(
                            machine.id, input);
                    }

                    state.isLoading = false;
                    if (response) return response || [];
                } else {
                    const response = await ChildSheetApi.getSheetLayout(input);
                    if (response) return [response] || [];
                }
            }
        };

        const inputIsValid = (input) => {
            let isValid = false;
            if (input) {
                const itemLayout = input.item_layout;
                const itemLayoutIsValid = 
                    itemLayout.width && itemLayout.length &&
                    itemLayout.width > 0 && 
                    itemLayout.length > 0 && 
                    itemLayout.uom != null;
                const materialLayout = input.material_layout;
                const materialLayoutIsValid = 
                    materialLayout.width && materialLayout.length &&
                    materialLayout.uom != null &&
                    convert(itemLayout.width, itemLayout.uom).to(materialLayout.uom) 
                        >= Number(materialLayout.width) > 0 &&
                    convert(itemLayout.length, itemLayout.uom).to(materialLayout.uom)  
                        >= Number(materialLayout.length) > 0;
                isValid = materialLayoutIsValid && itemLayoutIsValid;
            }
            return isValid;
        }

        const addMachineSpecificInputParams = (machine, input) => {
            let params = null;
            const machineType = machine? machine.resourcetype : null;
            if (machineType == 'SheetFedPressMachine') {
                params = state.data.layoutInputParams.sheetFedPress;
                input['bleed'] = params.bleed;
                input['rotate'] = params.rotate;
            } else if (machineType == 'RollFedPressMachine') {
                params = state.data.layoutInputParams.rollFedPress;
                input['order_quantity'] = params.orderQuantity;
                input['spoilage_rate'] = params.spoilageRate;
                input['apply_breakpoint'] = params.applyBreakpoint;
            } else {
                input['bleed'] = false;
                input['rotate'] = true;
            }
        }

        watchEffect(async ()=> {
            if (props.finalMaterialLayout && props.rawMaterialLayout) {
                const input = {
                    material_layout: {
                        width: props.finalMaterialLayout.width,
                        length: props.finalMaterialLayout.length,
                        uom: props.finalMaterialLayout.uom
                    },
                    item_layout: {
                        width: props.rawMaterialLayout.width,
                        length: props.rawMaterialLayout.length,
                        uom: props.rawMaterialLayout.uom
                    }
                };
                addMachineSpecificInputParams(props.machine, input)
                if (!inputIsValid(input)) return;
                state.data.sheetLayouts = await getSheetLayouts(input, props.machine);
            }
        });


        return {
            state, formatNumber
        }
    }
}
</script>