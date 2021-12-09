<template>
    <div>
        <CutListLayout :layouts="state.data.sheetLayouts"/>
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
import {SheetFedPressMachineApi, ChildSheetApi} from '@/utils/apis.js';
import {formatNumber} from '@/utils/format.js';

export default {
    components: {
        CutListLayout, DescriptionList, DescriptionItem
    },
    props: {
        machineId: Number,
        materialLayout: Object,
        itemLayout: Object,
    },
    setup(props) {
        const state = reactive({
            data: {
                sheetLayouts: [],
                error: null
            },
            meta: {
                hasRunsheet: computed(()=> state.data.sheetLayouts.length == 2)
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
                if (state.data.sheetLayouts != null ) {
                    if (state.data.sheetLayouts.length == 2) {
                        const parentToRunsheet = state.data.sheetLayouts[0];
                        const runsheetToChildsheet = state.data.sheetLayouts[1];

                        stats.runsheetSize = `${parentToRunsheet.rect.width} x ` +
                            `${parentToRunsheet.rect.length} ${parentToRunsheet.rect.uom}`;
                        stats.runsheetPerParent = parentToRunsheet.count;
                        stats.childsheetSize = `${runsheetToChildsheet.rect.width} x ` +
                            `${runsheetToChildsheet.rect.length} ${runsheetToChildsheet.rect.uom}`;
                        stats.childsheetPerRunsheet = runsheetToChildsheet.count;
                        stats.childsheetPerParent = parentToRunsheet.count * runsheetToChildsheet.count;

                        const parentUom = parentToRunsheet.bin.uom;
                        const childUom = runsheetToChildsheet.rect.uom;
                        const parentArea = convert(parentToRunsheet.bin.width, parentUom).to(childUom) * 
                            convert(parentToRunsheet.bin.length, parentUom).to(childUom);
                        const totalUsedArea = runsheetToChildsheet.rect.width * 
                            runsheetToChildsheet.rect.length * stats.childsheetPerParent;
                        stats.totalUsage = totalUsedArea/parentArea  * 100;
                        stats.totalWasteage =  100 - stats.totalUsage;
                        stats.totalCutCount = parentToRunsheet.cut_count + runsheetToChildsheet.cut_count;
                    } else if (state.data.sheetLayouts.length == 1) {
                        const parentToCutsheet = state.data.sheetLayouts[0];
                        stats.childsheetSize = `${parentToCutsheet.rect.width} x ` +
                            `${parentToCutsheet.rect.length} ${parentToCutsheet.rect.uom}`;
                        stats.childsheetPerParent = parentToCutsheet.count;

                        const parentUom = parentToCutsheet.bin.uom;
                        const childUom = parentToCutsheet.rect.uom;
                        const parentArea = convert(parentToCutsheet.bin.width, parentUom).to(childUom) * 
                            convert(parentToCutsheet.bin.length, parentUom).to(childUom);
                        const totalUsedArea = parentToCutsheet.rect.width * 
                            parentToCutsheet.rect.length * stats.childsheetPerParent;
                        stats.totalUsage = totalUsedArea/parentArea  * 100;
                        stats.totalWasteage =  100 - stats.totalUsage;
                        stats.totalCutCount = parentToCutsheet.cut_count;
                    }
                }
                return stats;
            })
        });
    
        const getSheetLayouts = async (input, machineId=null) => {
            if (input && inputIsValid(input)) {
                if (machineId) {
                    const response = await SheetFedPressMachineApi.getSheetLayout(
                        machineId, input);
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
                if (!inputIsValid(input)) return;
                state.data.sheetLayouts = await getSheetLayouts(input, props.machineId);
            }
        });

        return {
            state, formatNumber
        }
    }
}
</script>