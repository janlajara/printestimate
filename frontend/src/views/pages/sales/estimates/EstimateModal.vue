<template>
    <Modal :heading="`${state.isCreate ? 'Create' : 'Edit'} Product Estimate`" 
        :is-open="$props.isOpen" @toggle="(value)=> $emit('toggle', value)"
        :buttons="[{color: 'primary', icon:'save', text:'Save', 
            action: state.save, disabled: state.isProcessing},]">
        <div v-if="state.error" 
            class="pt-4 text-sm text-red-600">*{{state.error}}</div>
        <Section heading="General Information" heading-position="side"> 
            <div class="md:grid md:gap-4 md:grid-cols-3">
                <InputText class="col-span-2"
                    name="Quantities"  placeholder="e.g. 100,200,300" 
                    type="text" :value="state.form.quantitiesField.text" required
                    @keyup="state.form.quantitiesField.onkeyup"
                    @input="(value) => state.form.quantitiesField.text = value"/>
                <InputText postfix="%"
                    name="Material Spoilage Rate"  placeholder="0-100" 
                    type="number" :min="0" :max="100" required
                    :value="state.data.materialSpoilageRate" 
                    @input="(value) => state.data.materialSpoilageRate = value"/>
            </div>
        </Section>
        <hr/>
        <Section heading="Cost Add-ons" heading-position="side"> 
            <EstimateModalCostAddons
                @input="value => state.data.estimateAddons = value"/>
        </Section>
    </Modal>
</template>
<script>
import {reactive, computed, watch} from 'vue';

import Modal from '@/components/Modal.vue';
import Section from '@/components/Section.vue';
import InputText from '@/components/InputText.vue';
import EstimateModalCostAddons from './EstimateModalCostAddons.vue';

import {EstimateApi} from '@/utils/apis.js';

export default {
    components: {
        Modal, Section, InputText, EstimateModalCostAddons
    },
    props: {
        isOpen: Boolean,
        productEstimateId: String,
        presetData: Object
    },
    emits: ['toggle', 'saved'],
    setup(props, {emit}) {
        const state = reactive({ 
            id: props.productEstimateId,
            isCreate: computed(()=> props.productEstimateId == null),
            isProcessing: false,
            error: '',
            data: {
                template: null,
                orderQuantities: computed(()=> {
                    const split = state.form.quantitiesField.text.trim().split(',');
                    const filtered = split.filter(x => !isNaN(x) && x!="");
                    let parsed = []
                    if (filtered.length > 0) parsed = filtered.map(x=>parseInt(x));
                    return parsed;
                }),
                materialSpoilageRate: 0,
                estimateAddons: []
            },
            form: {
                quantitiesField: {
                    text: '',
                    onkeyup: (event)=> {
                        const value = event.target.value;
                        if (value != null) {
                            let replaced = value.replace(/[^\d,]/g, '');
                            replaced = replaced.replace(/,{2,}/g, ',')
                            event.target.value = replaced;
                        }
                    }
                }
            },
            validate: ()=> {
                let errors = [];
                if (state.data.template == null && state.isCreate) errors.push('product template');
                if (state.data.orderQuantities.length == 0) errors.push('order quantities')
                if (errors.length > 0)
                    state.error = `The following fields must not be empty: ${errors.join(', ')}.`;
                else state.error = '';
                return errors.length > 0;
            },
            save: ()=> {
                if (state.validate()) return;
                const estimate = {
                    product_template: state.data.template,
                    order_quantities: state.data.orderQuantities,
                    material_spoilage_rate: state.data.materialSpoilageRate,
                    estimate_addon_set: {
                        estimate_addon_items: state.data.estimateAddons 
                    }
                };
                saveEstimate(state.id, estimate);
            },
            clear: ()=> {
                state.data.template = null;
                state.data.materialSpoilageRate = 0;
                state.data.estimateAddons = [];
                state.form.quantitiesField.text = '';
            }
        });

        const retrieveEstimateById = async (id)=> {
            state.isProcessing = true;
            if (id != null) {
                const response = await EstimateApi.retrieveEstimate(id);
                state.form.quantitiesField.text = response.order_quantities.join(',');
                state.data.materialSpoilageRate = parseInt(response.material_spoilage_rate);
            }
            state.isProcessing = false;
        }

        const saveEstimate = async (id, estimate)=> {
            state.isProcessing = true;
            if (estimate) {
                let response = null;
                let estimateId = null;
                if (!state.isCreate && id) {
                    response = await EstimateApi.updateEstimate(
                        id, estimate);
                } else {
                    response = await EstimateApi.createEstimate(
                        estimate);
                }
                if (response) {
                    estimateId = response.id;
                    emit('toggle', false); 
                    emit('saved', estimateId);
                }
            }
            state.isProcessing = false;
        }

        const initializePreset = ()=> {
            if (props.presetData && props.presetData.template != null) {
                state.data.template = props.presetData.template;
            }
        }

        watch(()=> props.isOpen, async ()=> { 
            if (props.isOpen) {
                state.error = ''; 
                initializePreset();
                if (state.id) retrieveEstimateById(state.id);
            } else {
                state.clear();
            }
        });

        return {
            state
        }
    },
}
</script>
