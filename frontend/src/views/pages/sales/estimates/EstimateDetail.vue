<template>
    <Page :title="`Estimate : CE-${state.data.estimateCode}`">
        <hr class="my-4"/>
        <div class="flex gap-4">
            <Button color="secondary" icon="arrow_back"
                @click="()=>$router.go(-1)">Go Back</Button>
            <Button class="my-auto" icon="edit"
                @click="state.components.editModal.open"/>
            <Button icon="delete" 
                @click="state.components.deleteDialog.open"/>
            <EstimateModal 
                :product-estimate-id="state.data.id"
                :is-open="state.components.editModal.isOpen"
                @toggle="state.components.editModal.toggle" 
                @saved="estimateId => retrieveEstimateCostsById(estimateId)"/>
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
            <DescriptionList class="md:grid-cols-2">
                <DescriptionItem  
                    name="Template" :loader="state.isProcessing" 
                    :value="`[${state.data.templateCode}] ${state.data.templateName}`"/>
                <DescriptionItem :loader="state.isProcessing"
                    name="Description" :value="state.data.templateDescription"/>
            </DescriptionList>
        </Section>
        <EstimateDetailSpecification
            :is-processing="state.isProcessing"
            :components="state.data.specifications.components"
            :services="state.data.specifications.services"/>
        <EstimateDetailCosting
            :is-processing="state.isProcessing"
            :quantities="state.data.quantities"
            :bill-of-materials="state.data.costing.billOfMaterials"
            :services="state.data.costing.services"/>
    </Page>
    
</template>
<script>
import Page from '@/components/Page.vue';
import Button from '@/components/Button.vue';
import Section from '@/components/Section.vue';
import DeleteRecordDialog from '@/components/DeleteRecordDialog.vue';
import DescriptionList from '@/components/DescriptionList.vue';
import DescriptionItem from '@/components/DescriptionItem.vue';
import EstimateModal from './EstimateModal.vue';
import EstimateDetailSpecification from './specification/EstimateDetailSpecification.vue';
import EstimateDetailCosting from './costing/EstimateDetailCosting.vue';

import {reactive, inject, onBeforeMount} from 'vue';
import {useRoute} from 'vue-router';
import {EstimateApi} from '@/utils/apis.js';
import {formatMoney as formatCurrency} from '@/utils/format.js'

export default {
    components: {
        Page, Button, Section, DeleteRecordDialog, 
        DescriptionList, DescriptionItem, EstimateModal,
        EstimateDetailSpecification, EstimateDetailCosting
    },
    setup() {
        const currency = inject('currency').abbreviation;
        const route = useRoute();
        const state = reactive({
            isProcessing: false,
            data: {
                id: route.params.id,
                estimateCode: '',
                templateCode: '',
                templateName: '',
                templateDescription: '',
                quantities: [],
                specifications: {
                    components: [],
                    services: []
                },
                costing: {
                    billOfMaterials: [],
                    services: []
                }
            },
            components: {
                editModal: {
                    isOpen: false,
                    toggle: value => state.components.editModal.isOpen = value,
                    open: ()=> state.components.editModal.toggle(true),
                },
                deleteDialog: {
                    isOpen: false,
                    toggle: value => state.components.deleteDialog.isOpen = value,
                    open: ()=> state.components.deleteDialog.toggle(true),
                    delete: async ()=> {await deleteEstimate(state.data.id)}
                },
            }
        });

        onBeforeMount(()=> {
            retrieveEstimateBydId(state.data.id);
            retrieveEstimateCostsById(state.data.id);
        });

        const deleteEstimate = async (id)=> {
            if (id) await EstimateApi.deleteEstimate(id); 
        }

        const retrieveEstimateBydId = async (id)=> {
            if (id != null) {
                const response = await EstimateApi.retrieveEstimate(id);
                if (response) {
                    state.data.specifications.components = 
                        response.product.components.map(x => ({
                            name: x.name,
                            quantity: x.quantity,
                            materials: x.materials.map(x => x.label)
                        }));
                    
                    state.data.specifications.services = 
                        response.product.services.map(x => ({
                            name: x.name, sequence: x.sequence,
                            operations: x.operation_estimates.map(y => ({
                                name: y.name,
                                material: y.material,
                                activities: y.activity_estimates.map(z => ({
                                    name: z.name,
                                    sequence: z.sequence,
                                    speed: z.speed,
                                    notes: z.notes
                                }))
                            }))
                        }));
                }
            }
        }

        const retrieveEstimateCostsById = async (id)=> {
            state.isProcessing = true;
            if (id != null) {
                const response = await EstimateApi.retrieveEstimateCosts(id);
                if (response) {
                    state.data.estimateCode = response.id;
                    state.data.templateCode = response.template_code;
                    state.data.templateName = response.name;
                    state.data.templateDescription = response.description;
                    state.data.quantities = response.order_quantities;
                    
                    if (response.estimates) {
                        state.data.costing.billOfMaterials = response.estimates.material_estimates.map(me => ({
                            name: me.name, rate: parseFloat(me.rate), uom: me.uom, 
                            spoilageRate: parseFloat(me.spoilage_rate), isExpanded: false,
                            layouts: me.layouts_meta,
                            estimates: me.estimates.map(es => ({
                                itemQuantity: es.order_quantity,
                                estimatedMaterialQuantity: es.estimated_stock_quantity,
                                spoilageMaterialQuantity: es.estimated_spoilage_quantity
                            }))
                        }));
                        
                        state.data.costing.services = response.estimates.service_estimates.map(se => ({
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
            }
            state.isProcessing = false;
        }

        const formatMoney = (amount)=> {
            if (amount != null)
                return formatCurrency(amount, currency)
            else return ''
        }

        return {
            state, retrieveEstimateCostsById, formatMoney
        }
    }
    
}
</script>