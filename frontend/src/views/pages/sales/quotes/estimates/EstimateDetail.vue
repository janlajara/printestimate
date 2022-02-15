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
                <DescriptionItem :loader="state.isProcessing"
                    name="Description" :value="state.data.templateDescription"/>
            </DescriptionList>
        </Section>
        <Section heading="Cost Estimation">
            <div class="w-full">
                <!-- Table Header -->
                <div class="border-b grid grid-cols-2">
                    <div class="font-bold text-lg text-left"></div>
                    <div class="flex relative">
                        <div class="absolute">
                            <span class="material-icons text-sm cursor-pointer"
                                :class="state.components.paginator.offset == 0? 
                                    'hidden': ''"
                                @click="state.components.paginator.left">chevron_left</span>
                        </div>
                        <div :class="`w-full grid grid-cols-${state.meta.quantitiesColumnLength}`">
                            <div v-for="(quantity, key) in 
                                    state.components.paginator.paginate(state.data.quantities)" :key="key"
                                class="flex justify-center">
                                <span class="font-bold">{{quantity}}</span>
                            </div>
                        </div>
                        <div class="absolute right-0">
                            <span class="material-icons text-sm cursor-pointer"
                                :class="state.components.paginator.offset == state.components.paginator.limit? 
                                    'hidden': ''"
                                @click="state.components.paginator.right">chevron_right</span>
                        </div>
                    </div>
                </div>

                <!-- Table Rows for Bill of Materials -->
                <EstimateDetailBillOfMaterials class="py-2"
                    :quantities="state.data.quantities"
                    :bill-of-materials="state.data.billOfMaterials"
                    :quantity-viewable-offset="state.components.paginator.offset"
                    :max-quantity-viewable="3"/>

                <!-- Table Rows for Services -->
                <EstimateDetailServices class="py-2 pb-4"
                    :quantities="state.data.quantities"
                    :services="state.data.services"
                    :quantity-viewable-offset="state.components.paginator.offset"
                    :max-quantity-viewable="3"/>

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
import EstimateDetailBillOfMaterials from './EstimateDetailBillOfMaterials.vue';
import EstimateDetailServices from './EstimateDetailServices.vue';

import {reactive, computed, onBeforeMount} from 'vue';
import {useRoute} from 'vue-router';
import {EstimateApi} from '@/utils/apis.js';

export default {
    components: {
        Page, Button, Section, DeleteRecordDialog, 
        DescriptionList, DescriptionItem, 
        EstimateDetailBillOfMaterials, EstimateDetailServices
    },
    setup() {
        const route = useRoute();
        const state = reactive({
            isProcessing: false,
            meta: {
                maxQuantitiesColumnLength: 3,
                quantitiesColumnLength: computed(()=> 
                    Math.min(state.data.quantities.length, 
                        state.meta.maxQuantitiesColumnLength)),
            },
            data: {
                id: route.params.id,
                estimateCode: 'CE-1234',
                templateCode: '',
                templateName: '',
                templateDescription: '',
                quantities: [],
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
                },
                paginator: {
                    offset: 0,
                    limit: computed(()=>
                        state.data.quantities.length - state.meta.quantitiesColumnLength),
                    paginate: (array)=> {
                        let spliced = [...array];
                        if (array) spliced = spliced.splice(
                            state.components.paginator.offset, 
                            state.meta.quantitiesColumnLength);
                        return spliced;
                    },
                    left: ()=> {
                        let offset = state.components.paginator.offset - 1;
                        state.components.paginator.offset = Math.max(offset, 0);
                    },
                    right: ()=> {
                        let offset = state.components.paginator.offset + 1;
                        let limit = state.components.paginator.limit;
                        state.components.paginator.offset = Math.min(offset, limit);
                    }
                }
            }
        });

        onBeforeMount(()=> {
            retrieveEstimateById(state.data.id);
        });

        const retrieveEstimateById = async (id)=> {
            state.isProcessing = true;
            if (id != null) {
                const response = await EstimateApi.retrieveEstimate(id);

                state.data.templateCode = response.template_code;
                state.data.templateName = response.name;
                state.data.templateDescription = response.description;
                state.data.quantities = response.order_quantities;

                if (response.estimates) {
                    state.data.billOfMaterials = response.estimates.material_estimates.map(me => ({
                        name: me.name, rate: parseFloat(me.rate), uom: me.uom, 
                        spoilageRate: parseFloat(me.spoilage_rate), isExpanded: false,
                        estimates: me.estimates.map(es => ({
                            itemQuantity: es.order_quantity,
                            estimatedMaterialQuantity: es.estimated_stock_quantity,
                            spoilageMaterialQuantity: es.estimated_spoilage_quantity
                        }))
                    }));
                    
                    state.data.services = response.estimates.service_estimates.map(se => ({
                        name: se.name, isExpanded: false,
                        operations: se.operation_estimates.map(oe => ({
                            name: [oe.name, oe.item_name].join(' '), 
                            activities: oe.activity_estimates.map(ae => ({
                                name: (ae.name + " " + ae.notes).trim(),
                                expenses: ae.activity_expense_estimates.map(aee => ({
                                    name: aee.name,  type: aee.type, 
                                    rate: parseFloat(aee.rate),
                                    rateLabel: aee.rate_label,
                                    estimates: aee.estimates.map(e => ({
                                        itemQuantity: parseFloat(e.order_quantity),
                                        estimate: e.quantity? parseFloat(e.quantity) : null
                                    }))
                                }))
                            }))
                        }))
                    }));
                }

            }
            state.isProcessing = false;
        }

        return {
            state
        }
    }
    
}
</script>