<template>
    <Modal :heading="`${state.isCreate ? 'Create' : 'Edit'} Product Estimate`" 
        :is-open="$props.isOpen" @toggle="(value)=> $emit('toggle', value)"
        :buttons="[{color: 'primary', icon:'save', text:'Save', 
            action: state.save, disabled: state.isProcessing},]">
        <div v-if="state.error" 
            class="pt-4 text-sm text-red-600">*{{state.error}}</div>
        <Section heading="General Information" heading-position="side"> 
            <div class="md:grid md:gap-4 md:grid-cols-3">
                <InputTextLookup name="Product Template" required
                    :disabled="!state.isCreate"
                    placeholder="Search..." class="flex-grow md:col-span-2"
                    :text="state.form.templateLookup.text"
                    @select="value => state.form.templateLookup.select(value)"
                    @input="value => state.form.templateLookup.search(value)"
                    :options="state.meta.templates.map( option => ({
                        value: option.id,
                        title: option.name,
                        subtitle: option.description,
                        isSelected: state.data.template == option.id
                    }))"/>
                <InputText class="col-span-2"
                    name="Quantities"  placeholder="e.g. 100,200,300" 
                    type="text" :value="state.form.quantitiesField.text" required
                    @keyup="state.form.quantitiesField.onkeyup"
                    @input="(value) => state.form.quantitiesField.text = value"/>
            </div>
        </Section>
    </Modal>
</template>
<script>
import {reactive, computed, watch} from 'vue';

import Modal from '@/components/Modal.vue';
import Section from '@/components/Section.vue';
import InputText from '@/components/InputText.vue';
import InputTextLookup from '@/components/InputTextLookup.vue';

import {ProductTemplateApi, EstimateApi} from '@/utils/apis.js';

export default {
    components: {
        Modal, Section, InputText, InputTextLookup
    },
    props: {
        isOpen: Boolean,
        productEstimateId: String,
        onAfterSave: Function
    },
    setup(props, {emit}) {
        const state = reactive({ 
            id: props.productEstimateId,
            isCreate: computed(()=> props.productEstimateId == null),
            isProcessing: false,
            error: '',
            meta: {
                templates: []
            },
            data: {
                template: null,
                orderQuantities: computed(()=> {
                    const split = state.form.quantitiesField.text.trim().split(',');
                    const filtered = split.filter(x => !isNaN(x) && x!="");
                    let parsed = []
                    if (filtered.length > 0) parsed = filtered.map(x=>parseInt(x));
                    return parsed;
                })
            },
            form: {
                templateLookup: {
                    text: '',
                    select: (value)=> {
                        state.data.template = value},
                    search: (value)=> {
                        state.form.templateLookup.text = value;
                        populateProductTemplateList(value);}
                },
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
                if (state.data.template == null) errors.push('product template');
                if (state.data.orderQuantities.length == 0) errors.push('order quantities')
                if (errors.length > 0)
                    state.error = `The following fields must not be empty: ${errors.join(', ')}.`;
                else state.error = '';
                return errors.length > 0;
            },
            save: ()=> {
                if (state.validate()) return;
                const estimate = {
                    product_template_id: state.data.template,
                    order_quantities: state.data.orderQuantities
                };
                saveEstimate(state.id, estimate);
            },
            clear: ()=> {
                state.data.template = null;
                state.form.templateLookup.text = '';
                state.form.quantitiesField.text = '';
            }
        });

        const populateProductTemplateList = async (search=null)=> {
            const response = await ProductTemplateApi.listProductTemplates(10, 0, search);
            if (response && response.results) {
                state.meta.templates = response.results.map( obj => ({
                    id: obj.id,
                    code: obj.code,
                    name: obj.name,
                    description: obj.description
                }))
            }
        }

        const saveEstimate = async (id, estimate)=> {
            state.isProcessing = true;
            if (estimate) {
                let response = null;
                if (!state.isCreate && id) {
                    response = await EstimateApi.updateEstimate(
                        id, estimate);
                } else {
                    response = await EstimateApi.createEstimate(
                        estimate);
                }
                if (response) {
                    if (props.onAfterSave) props.onAfterSave();
                    emit('toggle', false);
                }
            }
            state.isProcessing = false;
        }

        watch(()=> props.isOpen, async ()=> { 
            if (props.isOpen) {
                state.error = ''; 
                populateProductTemplateList();
            } else {
                state.clear();
            }
        })

        return {
            state
        }
    },
}
</script>
