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
                <InputText class="col-span-2"
                    name="Description"  placeholder="Description"  
                    type="text" :value="state.data.description" required
                    @input="value => state.data.description = value"/>
                <InputTextLookup name="Product Class" required
                    :disabled="!state.isCreate"
                    placeholder="Search..." class="flex-grow md:col-span-2"
                    :text="state.form.productClass.text"
                    @select="value => state.form.productClass.select(value)"
                    @input="value => state.form.productClass.search(value)"
                    :options="state.meta.metaproducts.map( option => ({
                        value: option.id,
                        title: option.name,
                        subtitle: option.description,
                        isSelected: state.data.metaProduct == option.id
                    }))"/>
            </div>
        </Section>
        <hr/>
        <ProductComponentsForm 
            :meta-product-id="state.data.metaProduct"
            @input="value => state.data.componentTemplates = value"
            @load="event => {
                state.data.componentTemplates = event.data;
                state.validators = event.validators;
            }"/>
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
            clear: ()=>{
                state.data = {
                    name: '', description: '',
                    metaProduct: null,
                    componentTemplates: [],
                    serviceTemplates: [],
                }
            },
            validators: [],
            validate: ()=> {
                let errors = [];
                if (state.data.name == '') errors.push('name');
                if (state.data.description == '') errors.push('description');
                if (state.data.metaProduct == null) errors.push('product class');
                if (errors.length > 0)
                    state.error = `The following fields must not be empty: ${errors.join(', ')}.`;
                else state.error = '';
                if (state.validators.length > 0) {
                    state.validators.forEach( validator => validator());
                }
                return errors.length > 0;
            },
            save: ()=> {
                if (state.validate()) return;
                const productTemplate = {
                    meta_product: state.data.metaProduct,
                    name: state.data.name, 
                    description: state.data.description,
                    component_templates: state.data.componentTemplates,
                    service_templates: []
                }
                
                console.log(state.data);
                console.log(productTemplate);
                //if (state.id == 'asd')
                saveProductTemplate(state.id, productTemplate);
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

        const saveProductTemplate = async (id, productTemplate)=> {
            state.isProcessing = true;
            if (productTemplate) {
                let response = null;
                if (!state.isCreate && id) {
                    response = await ProductTemplateApi.updateProductTemplate(
                        id, productTemplate);
                } else {
                    response = await ProductTemplateApi.createProductTemplate(
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
            if (response) {
                state.meta.metaproducts = response.results.map( obj => ({
                    id: obj.id,
                    name: obj.name,
                    description: obj.description
                }))
            }
            state.isProcessing = false;
        }

        watch(()=> props.isOpen, ()=> { 
            if (props.isOpen) {
                state.error = '';
                if (state.id && !state.isCreate) {
                    const id = parseInt(state.id);
                    retrieveProductTemplate(id);
                } else {
                    populateMetaProductList();
                }
            } else {
                state.clear()
            }
        })

        return {
            state
        }
    }
}
</script>