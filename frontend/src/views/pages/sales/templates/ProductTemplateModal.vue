<template>
    <Modal :heading="`${state.isCreate ? 'Add' : 'Edit'} Product Template`" 
        :is-open="$props.isOpen" @toggle="(value)=> $emit('toggle', value)"
        :buttons="[{color: 'primary', icon:'save', text:'Save', 
            action: state.save, disabled: state.isProcessing},]">
        <div v-if="state.error" 
            class="pt-4 text-sm text-red-600">*{{state.error}}</div>
        <Section heading="General Information" heading-position="side"> 
            <div class="md:grid md:gap-4 md:grid-cols-3">
                <InputText name="Name"  placeholder="Name"
                    type="text" :value="state.data.name" required
                    @input="value => state.data.name = value"/>
                <InputText name="Description"  placeholder="Description"  class="col-span-2"
                    type="text" :value="state.data.description" required
                    @input="value => state.data.description = value"/>
                <InputTextLookup name="Product Class" 
                    :disabled="!state.isCreate"
                    placeholder="Search..." class="flex-grow md:col-span-2"
                    :text="state.form.productClass.text"
                    @select="value => {
                        state.form.productClass.select(value)
                    }"
                    @input="value => {
                        state.form.productClass.search(value);
                    }"
                    :options="state.meta.metaproducts.map( option => ({
                        value: option.id,
                        title: option.name,
                        subtitle: option.description,
                        isSelected: state.data.metaProduct == option.id
                    }))"/>
            </div>
        </Section>
        <hr class=""/>
        <ProductComponentsForm :meta-product-id="state.data.metaProduct"/>
    </Modal>
</template>

<script>
import Modal from '@/components/Modal.vue';
import Section from '@/components/Section.vue';
import InputText from '@/components/InputText.vue';
import InputTextLookup from '@/components/InputTextLookup.vue';
import ProductComponentsForm from './components/ProductComponentsForm.vue';

import {reactive, computed, watch} from 'vue';
import {MetaProductApi, ProductTemplateApi} from '@/utils/apis.js';

export default {
    components: {
        Modal, Section, InputText, InputTextLookup, ProductComponentsForm 
    },
    props: {
        isOpen: Boolean,
        productTemplateId: String,
        onAfterSave: Function
    },
    emits: ['toggle'],
    setup(props, {emit}) {
        const state = reactive({
            id: props.productTemplateId,
            isCreate: computed(()=> props.productTemplateId == null),
            isProcessing: false,
            error: '',
            data: {
                name: '', description: '',
                metaProduct: null,
                componentTemplates: [],
                serviceTemplates: [],
            },
            form: {
                productClass: {
                    text: '',
                    search: (value)=> {
                        state.form.productClass.text = value;
                        populateMetaProductList(value); },
                    select: (value)=> {state.data.metaProduct = value}
                }
            },
            meta: {
                metaproducts: []
            },
            validate: ()=> {
                let errors = [];
                if (state.data.name == '' || state.data.name == null) errors.push('name');
                if (errors.length > 0)
                    state.error = `The following fields must not be empty: ${errors.join(', ')}.`;
                else state.error = '';
                return errors.length > 0;
            },
            save: ()=> {
                if (state.validate()) return;
                const productTemplate = {
                    name: state.data.name, 
                    description: state.data.description}
                saveProductTemplate(productTemplate);
            }
        });

        const retrieveProductTemplate = async (id)=> {
            state.isProcessing = true;
            const response = await ProductTemplateApi.retrieveProductTemplate(id);
            if (response) {
                state.data = {
                    name: response.name, description: response.description
                }
            }
            state.isProcessing = false;
        }

        const saveProductTemplate = async (productTemplate)=> {
            state.isProcessing = true;
            if (productTemplate) {
                let response = null;
                if (!state.isCreate && state.id) {
                    response = await ProductTemplateApi.updateProductTemplate(
                        state.id, productTemplate);
                } else {
                    response = await ProductTemplateApi.updateProductTemplate(
                        productTemplate);
                }
                if (response) {
                    if (props.onAfterSave) props.onAfterSave();
                    emit('toggle', false);
                }
            }
            state.isProcessing = false;
        }

        const populateMetaProductList = async (search=null)=> {
            state.isProcessing = true;
            const response = await MetaProductApi.listMetaProducts(10, 0, search);
            if (response) {console.log(response)
                state.meta.metaproducts = response.results.map( obj => ({
                    id: obj.id,
                    name: obj.name,
                    description: obj.description
                }))
            }
            state.isProcessing = false;
        }

        watch(()=> props.isOpen, ()=> { 
            if (props.isOpen && state.id && !state.isCreate) {
                const id = parseInt(state.id);
                retrieveProductTemplate(id);
            } else {
                populateMetaProductList();
            }
        })

        return {
            state
        }
    }
}
</script>