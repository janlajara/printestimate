<template>
    <div>
        <CutListLayout :layouts="state.data.sheetLayouts"/>
        <DescriptionList class="md:grid-cols-3">
            <DescriptionItem :name="`Total outs (${state.stats.childsheetSize})`" 
                :value="`${state.stats.childsheetPerParent} sheets / material`"/>
            <DescriptionItem :name="`Runsheet (${state.stats.runsheetSize})`" 
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

import {reactive, computed, watchEffect} from 'vue';
import {SheetFedPressMachineApi} from '@/utils/apis.js';
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

                    const parentArea = parentToRunsheet.bin.width * parentToRunsheet.bin.length;
                    const totalUsedArea = runsheetToChildsheet.rect.width * 
                        runsheetToChildsheet.rect.length * stats.childsheetPerParent;
                    stats.totalUsage = totalUsedArea/parentArea  * 100;
                    stats.totalWasteage =  100 - stats.totalUsage;
                    stats.totalCutCount = parentToRunsheet.cut_count + runsheetToChildsheet.cut_count;
                }
                return stats;
            })
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
                const itemLayout = input.item_layout;
                const itemLayoutIsValid = itemLayout.width > 0 && 
                    itemLayout.length > 0 && itemLayout.uom != null;

                const materialLayout = input.material_layout;
                const materialLayoutIsValid = 
                    itemLayout.width >= materialLayout.width > 0 &&
                    itemLayout.length >= materialLayout.length > 0 && 
                    materialLayout.uom != null;

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
                if (props.machineId) {
                    state.data.sheetLayouts = await getSheetLayouts(
                        props.machineId, input);
                }
            }
        });

        return {
            state, formatNumber
        }
    }
}
</script>