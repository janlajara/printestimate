<template>
    <Page :title="`Estimate : ${state.data.estimateCode}`">
        <hr class="my-4"/>
        <div class="flex gap-4">
            <Button color="secondary" icon="arrow_back"
                @click="()=>$router.go(-1)">Go Back</Button>
            <Button class="my-auto" icon="edit"
                @click="state.components.editModal.open"/>
            <Button icon="delete" 
                @click="state.components.deleteDialog.open"/>
            <DeleteRecordDialog 
                heading="Delete Quote"
                :is-open="state.components.deleteDialog.isOpen"
                :execute="state.components.deleteDialog.delete"
                :on-after-execute="()=>$router.go(-1)"
                @toggle="state.components.deleteDialog.toggle">
                <div>
                    Are you sure you want to delete 
                    <span class="font-bold">
                        {{state.data.estimateCode}}</span>?
                </div>
            </DeleteRecordDialog>
        </div>
        <Section>
            <DescriptionList class="md:grid-cols-3">
                <DescriptionItem  
                    name="Template" :loader="state.isProcessing" 
                    :value="`[${state.data.templateCode}] ${state.data.templateName}`"/>
                <DescriptionItem :loader="state.isProcecssing"
                    name="Description" :value="state.data.templateDescription"/>
            </DescriptionList>
        </Section>
        <Section>
            <div class="w-full">
                <!-- Table Header -->
                <div class="border-b grid grid-cols-2">
                    <div class="font-bold text-lg text-left">
                        Cost Estimation</div>
                    <div :class="`grid grid-cols-${state.meta.quantitiesColumnLength}`">
                        <div v-for="(quantity, key) in state.data.quantities" :key="key"
                            class="flex justify-center">
                            <span class="font-bold">{{quantity}}</span>
                        </div>
                    </div>
                </div>

                <!-- Table Rows for Bill of Materials -->
                <EstimateBillOfMaterials 
                    :quantities="state.data.quantities"
                    :bill-of-materials="state.data.billOfMaterials"/>

                <!-- Table Rows for Services -->
                <EstimateServices 
                    :quantities="state.data.quantities"
                    :services="state.data.services"/>

            </div>
        </Section>
    </Page>
    
</template>
<script>
import Page from '@/components/Page.vue';
import Button from '@/components/Button.vue';
import Section from '@/components/Section.vue';
import DeleteRecordDialog from '@/components/DeleteRecordDialog.vue';
import DescriptionList from '@/components/DescriptionList.vue';
import DescriptionItem from '@/components/DescriptionItem.vue';
import EstimateBillOfMaterials from './EstimateBillOfMaterials.vue';
import EstimateServices from './EstimateServices.vue';

import {reactive, computed, onBeforeMount} from 'vue';

export default {
    components: {
        Page, Button, Section, DeleteRecordDialog, 
        DescriptionList, DescriptionItem, EstimateBillOfMaterials, EstimateServices
    },
    setup() {
        const state = reactive({
            isProcessing: false,
            meta: {
                quantitiesColumnLength: computed(()=> Math.max(state.data.quantities.length, 1)),
            },
            data: {
                estimateCode: 'CE-1234',
                templateCode: 'PT-9876',
                templateName: 'Carbonless Form',
                templateDescription: '8.5x11" Carbonless Form (White, Yellow, Blue)',
                quantities: [100, 200, 300],
                billOfMaterials: [],
                services: []
            },
            components: {
                editModal: {
                    open: ()=> {}
                },
                deleteDialog: {
                    isOpen: false,
                    toggle: value => state.components.deleteDialog.isOpen = value,
                    open: ()=> state.components.deleteDialog.toggle(true),
                    delete: ()=> {}
                }
            }
        });

        onBeforeMount(()=> {
            const mockBillOfMaterials = [
                {name: 'Generic Carbonless White 32x24inch', 
                rate: 30.00, 
                uom: 'sheet', 
                spoilageRate: 10, isExpanded: false,
                estimates: [
                {itemQuantity: 100, 
                    estimatedMaterialQuantity: 300,
                    spoilageMaterialQuantity: 30,
                    totalMaterialQuantity: 300},
                {itemQuantity: 200, 
                    estimatedMaterialQuantity: 600,
                    spoilageMaterialQuantity: 60,
                    totalMaterialQuantity: 600},
                {itemQuantity: 300, 
                    estimatedMaterialQuantity: 900,
                    spoilageMaterialQuantity: 90,
                    totalMaterialQuantity: 900}
                ]},
                {name: 'Carbonless Blue 32x24', 
                rate: 30.00, 
                uom: 'sheet', 
                spoilageRate: 0, isExpanded: false,
                estimates: [
                {itemQuantity: 100, 
                    estimatedMaterialQuantity: 300,
                    spoilageMaterialQuantity: 0,
                    totalMaterialQuantity: 300},
                {itemQuantity: 200, 
                    estimatedMaterialQuantity: 600,
                    spoilageMaterialQuantity: 0,
                    totalMaterialQuantity: 600},
                {itemQuantity: 300, 
                    estimatedMaterialQuantity: 900,
                    spoilageMaterialQuantity: 0,
                    totalMaterialQuantity: 900}
                ]}
            ];

            const mockServicesData = [
                {name: 'Raw-to-running cut',
                uom: 'count', 
                isExpanded: false,
                operations: [
                    {name: 'Cutting',
                    activities: [
                        {name: 'Polar Cutter Cutting',
                        expenses: [
                            {name: 'Cut fee', type: 'measure', rate: 50, 
                            estimates: [
                                {itemQuantity: 100, estimate: 4},
                                {itemQuantity: 200, estimate: 4},
                                {itemQuantity: 300, estimate: 4},
                            ]},
                            {name: 'Electricity', type: 'hour', rate: 67, 
                            estimates: [
                                {itemQuantity: 100, estimate: 8},
                                {itemQuantity: 200, estimate: 16},
                                {itemQuantity: 300, estimate: 24},
                            ]},
                            {name: 'Depreciation', type: 'hour', rate: 120, 
                            estimates: [
                                {itemQuantity: 100, estimate: 8},
                                {itemQuantity: 200, estimate: 16},
                                {itemQuantity: 300, estimate: 24},
                            ]},
                            {name: 'Usage fee', type: 'flat', rate: 400, 
                            estimates: [
                                {itemQuantity: 100, estimate: null},
                                {itemQuantity: 200, estimate: null},
                                {itemQuantity: 300, estimate: null},
                            ]},
                        ]}
                    ]}
                ]},
                {name: 'Printing',
                uom: 'sheet', 
                isExpanded: false,
                operations: [
                    {name: 'Front Print',
                    activities: [
                        {name: 'Spot Color Printing : 1st Color',
                        expenses: [
                            {name: 'Ink', type: 'measure', rate: 0.50, 
                            estimates: [
                                {itemQuantity: 100, estimate: 500},
                                {itemQuantity: 200, estimate: 750},
                                {itemQuantity: 300, estimate: 1000},
                            ]},
                            {name: 'Electricity', type: 'hour', rate: 66.67, 
                            estimates: [
                                {itemQuantity: 100, estimate: 16},
                                {itemQuantity: 200, estimate: 18},
                                {itemQuantity: 300, estimate: 20},
                            ]},
                            {name: 'Labor', type: 'hour', rate: 75, 
                            estimates: [
                                {itemQuantity: 100, estimate: 16},
                                {itemQuantity: 200, estimate: 18},
                                {itemQuantity: 300, estimate: 20},
                            ]},
                        ]},
                        {name: 'Spot Color Printing : 2nd Color',
                        expenses: [
                            {name: 'Ink', type: 'measure', rate: 0.50, 
                            estimates: [
                                {itemQuantity: 100, estimate: 500},
                                {itemQuantity: 200, estimate: 750},
                                {itemQuantity: 300, estimate: 1000},
                            ]},
                            {name: 'Electricity', type: 'hour', rate: 66.67, 
                            estimates: [
                                {itemQuantity: 100, estimate: 16},
                                {itemQuantity: 200, estimate: 18},
                                {itemQuantity: 300, estimate: 20},
                            ]},
                            {name: 'Labor', type: 'hour', rate: 75, 
                            estimates: [
                                {itemQuantity: 100, estimate: 16},
                                {itemQuantity: 200, estimate: 18},
                                {itemQuantity: 300, estimate: 20},
                            ]},
                        ]},
                    ]},
                    {name: 'Back Print',
                    activities: [
                        {name: 'Spot Color Printing : 1st Color',
                        expenses: [
                            {name: 'Ink', type: 'measure', rate: 0.50, 
                            estimates: [
                                {itemQuantity: 100, estimate: 500},
                                {itemQuantity: 200, estimate: 750},
                                {itemQuantity: 300, estimate: 1000},
                            ]},
                            {name: 'Electricity', type: 'hour', rate: 66.67, 
                            estimates: [
                                {itemQuantity: 100, estimate: 16},
                                {itemQuantity: 200, estimate: 18},
                                {itemQuantity: 300, estimate: 20},
                            ]},
                            {name: 'Labor', type: 'hour', rate: 75, 
                            estimates: [
                                {itemQuantity: 100, estimate: 16},
                                {itemQuantity: 200, estimate: 18},
                                {itemQuantity: 300, estimate: 20},
                            ]},
                        ]},
                        {name: 'Spot Color Printing : 2nd Color',
                        expenses: [
                            {name: 'Ink', type: 'measure', rate: 0.50, 
                            estimates: [
                                {itemQuantity: 100, estimate: 500},
                                {itemQuantity: 200, estimate: 750},
                                {itemQuantity: 300, estimate: 1000},
                            ]},
                            {name: 'Electricity', type: 'hour', rate: 66.67, 
                            estimates: [
                                {itemQuantity: 100, estimate: 16},
                                {itemQuantity: 200, estimate: 18},
                                {itemQuantity: 300, estimate: 20},
                            ]},
                            {name: 'Labor', type: 'hour', rate: 75, 
                            estimates: [
                                {itemQuantity: 100, estimate: 16},
                                {itemQuantity: 200, estimate: 18},
                                {itemQuantity: 300, estimate: 20},
                            ]},
                        ]},
                    ]}
                ]}
            ];
            
            state.data.billOfMaterials = mockBillOfMaterials;
            state.data.services = mockServicesData;
        });

        return {
            state
        }
    }
    
}
</script>