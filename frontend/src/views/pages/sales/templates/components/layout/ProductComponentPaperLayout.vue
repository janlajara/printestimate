<template>
    <div>
        <CutListLayout :loader="state.isLoading"
            @load="value => state.data.stats = value"
            :layout-type="state.data.sheetLayout.machineType"
            :layouts="state.data.sheetLayout.layouts"/>
        <DescriptionList class="md:grid-cols-3">
            <DescriptionItem :name="`Total outs (${state.stats.childsheetSize})`" 
                :value="state.stats.childsheetCountLabel"/>
            <DescriptionItem v-if="
                [layout_types.SHEET_FED_PRESS_MACHINE,
                 layout_types.ROLL_FED_PRESS_MACHINE]
                    .includes(state.stats.layoutType)"
                :name="`Runsheet (${state.stats.runsheetSize})`" 
                :value="state.stats.runsheetCountLabel"/>
            <DescriptionItem name="Wastage" 
                :value="`${formatNumber(state.stats.totalWasteage, 2, true)} %`"
                :class="(state.stats.totalWasteage > 20)? 'text-red-500 font-bold' : ''"/>
        </DescriptionList>
        <template v-if="state.stats.layoutType == layout_types.ROLL_FED_PRESS_MACHINE">
            <hr/>
            <div class="grid md:grid-cols-3 md:gap-6">
                <InputText name="Sample Order Quantity"  placeholder="Order Quantity" required
                    type="number" :value="state.data.layoutInputParams.rollFedPress.orderQuantity" 
                    :min="1"
                    @input="value => {
                        state.data.layoutInputParams.rollFedPress.orderQuantity = value;
                    }"/>
                <InputCheckbox label="Apply breakpoint?" 
                    :value="state.data.layoutInputParams.rollFedPress.applyBreakpoint"
                    @input="value => state.data.layoutInputParams.rollFedPress.applyBreakpoint = value"/>
            </div>
        </template>
    </div>
</template>

<script>
import CutListLayout, {layout_types} from '@/views/commons/layout/CutListLayout.vue';
import DescriptionList from '@/components/DescriptionList.vue';
import DescriptionItem from '@/components/DescriptionItem.vue';
import InputText from '@/components/InputText.vue';
import InputCheckbox from '@/components/InputCheckbox.vue';

import convert from 'convert';
import {reactive, computed, watchEffect} from 'vue';
import {SheetFedPressMachineApi, RollFedPressMachineApi, ChildSheetApi} from '@/utils/apis.js';
import {formatNumber} from '@/utils/format.js';

export default {
    components: {
        CutListLayout, DescriptionList, DescriptionItem, InputText, InputCheckbox
    },
    props: {
        copyQuantity: Number,
        machine: Object,
        finalMaterialLayout: Object,
        rawMaterialLayout: Object,
    },
    setup(props) {
        const state = reactive({
            isLoading: false,
            data: {
                sheetLayout: {
                    machineType: null,
                    layouts: []
                },
                error: null,
                stats: null,
                layoutInputParams: {
                    sheetFedPress: {
                        rotate: true,
                        bleed: false
                    },
                    rollFedPress: {
                        orderQuantity: 50 * props.copyQuantity,
                        spoilageRate: 0,
                        applyBreakpoint: true
                    }
                }
            },
            stats: computed(()=> {
                let stats = {
                    layoutType: null,
                    runsheetSize: '',
                    runsheetCountLabel: 0,
                    childsheetSize: '',
                    childsheetCountLabel: 0,
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
                    if (response) return response || [];
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
                input['order_quantity'] = params.orderQuantity * props.copyQuantity;
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
                const layoutObj = await getSheetLayouts(input, props.machine);
                state.data.sheetLayout = {
                    machineType: layoutObj.machine_type,
                    layouts: layoutObj.layouts
                }
            }
        });


        return {
            state, formatNumber, layout_types
        }
    }
}
</script>