<template>
    <div>
        <div class="pb-8 grid justify-items-end">
            <Button color="tertiary" icon="insert_page_break"
                :always-show-text="true" :disabled="state.impositionLayout.isLoading"
                :action="state.impositionLayout.download">Materials Layout</Button>
        </div>
        <!-- Imposition Layout (hidden) -->
        <div id="impositionLayout" ref="impositionLayout" class="p-2 bg-white absolute" style="width: 900px; display:none">
            <div class="pb-4">
                <p class="flex justify-between">
                    <span class="font-bold text-xl">{{$props.templateName}}</span>
                    <span>{{$props.estimateCode}}</span>
                </p>
                <p class="text-gray-500 italic text-sm">{{$props.templateDescription}}</p>
            </div>
            <div v-for="(material, x) in $props.billOfMaterials" :key="x" class="p-4 border">
                <div class="font-bold pb-2">{{material.name}}</div>
                <EstimateDetailCostingBillOfMaterialsLayout
                    class="sm:-ml-8"
                    :machine-type="material.machineType"
                    :layouts="material.layouts"/>
                <div class="w-1/2">
                    <div class="text-xs w-3/4">
                        <div class="grid grid-cols-3 gap-1 font-bold">
                            <p>Order Quantity</p>
                            <p>Stock + Spoilage</p>
                            <p>Total</p>
                        </div>
                        <div v-for="(estimate, y) in material.estimates" :key="y" class="grid grid-cols-3 gap-1">
                            <div>{{estimate.itemQuantity}}</div>
                            <div>{{estimate.estimatedMaterialQuantity}} + {{estimate.spoilageMaterialQuantity}}</div>
                            <div>= {{estimate.estimatedMaterialQuantity+estimate.spoilageMaterialQuantity}}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import Button from '@/components/Button.vue';
import EstimateDetailCostingBillOfMaterialsLayout from '../costing/EstimateDetailCostingBillOfMaterialsLayout.vue';

import html2canvas from 'html2canvas';
import {ref, reactive} from 'vue';

export default {
    props:{
        estimateCode:String,
        templateName: String,
        templateDescription: String,
        billOfMaterials: Array
    },
    components: {
        Button, EstimateDetailCostingBillOfMaterialsLayout
    },
    setup() {
        const impositionLayout = ref(null);
        const state = reactive({
            impositionLayout: {
                isLoading: false,
                download: async ()=> {
                    if (!state.impositionLayout.isLoading) {
                        state.impositionLayout.isLoading = true;
                        const canvas = await html2canvas(impositionLayout.value, 
                            {logging: false,
                            onclone: doc => {
                                const elem = doc.getElementById('impositionLayout');
                                elem.style.display = 'block';
                            }});
                        const imgData = canvas.toDataURL('image/png');
                        const a = document.createElement('a');
                        a.href = imgData.replace("image/png", "image/octet-stream");
                        a.download = 'imposition-layout.jpg';
                        a.click();
                        state.impositionLayout.isLoading = false;
                    }
                }
            },
        });

        return {
            state, impositionLayout
        }
    },
}
</script>
