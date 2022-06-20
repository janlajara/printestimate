<template>
    <Modal :heading="`${state.isCreate ? 'Add' : 'Edit'} Product Template`" 
        :is-open="$props.isOpen" @toggle="(value)=> $emit('toggle', value)"
        :buttons="[{color: 'primary', icon:'save', text:'Save', 
            action: state.save, disabled: state.isProcessing},]">
        <div v-if="state.error" 
            class="pt-4 text-sm text-red-600">*{{state.error}}</div>
        <Section heading="General Information" heading-position="side"> 
            <div class="md:grid md:gap-4 md:grid-cols-3">
                <InputText class="col-span-2"
                    name="Name"  placeholder="Name" :max=40
                    type="text" :value="state.data.name" required
                    @input="value => state.data.name = value"/>
                <InputTextarea class="col-span-2"
                    name="Description"  placeholder="Description"  
                    :value="state.data.description" required
                    @input="value => state.data.description = value"/>
                <InputTextLookup name="Product Class" required
                    :disabled="!state.isCreate"
                    placeholder="Search..." class="flex-grow md:col-span-2"
                    :text="state.form.productClass.text"
                    @select="value => state.form.productClass.select(value)"
                    @input="value => state.form.productClass.search(value)"
                    @cleared="{
                        state.data.componentTemplates = [];
                        state.data.serviceTemplates = [];
                    }"
                    :options="state.meta.metaproducts.map( option => ({
                        value: option.id,
                        title: option.name,
                        subtitle: option.description,
                        isSelected: state.data.metaProduct == option.id
                    }))"/>
            </div>
        </Section>
        <div v-show="state.data.metaProduct != null && 
                state.data.metaProduct != ''">
            <hr/> 
            <ProductComponentsForm 
                :meta-product-id="state.data.metaProduct"
                :value="state.data.componentTemplates"
                @input="value => state.data.componentTemplates = value"
                @load="event => {
                    state.data.componentTemplates = event.data;
                    state.validators.componentValidators = event.validators;
                }"/>
            <hr/>
            <ProductServicesForm
                :meta-product-id="state.data.metaProduct"
                :value="state.data.serviceTemplates" 
                @input="value => state.data.serviceTemplates = value"
                @load="event => {
                    state.data.serviceTemplates = event.data;
                    state.validators.serviceValidators = event.validators;
                }"/>
        </div>
    </Modal>
</template>

<script>
import Modal from '@/components/Modal.vue';
import Section from '@/components/Section.vue';
import InputText from '@/components/InputText.vue';
import InputTextarea from '@/components/InputTextarea.vue';
import InputTextLookup from '@/components/InputTextLookup.vue';
import ProductComponentsForm from './components/ProductComponentsForm.vue';
import ProductServicesForm from './services/ProductServicesForm.vue';

import {reactive, computed, watch} from 'vue';
import {MetaProductApi, ProductTemplateApi} from '@/utils/apis.js';

export default {
    components: {
        Modal, Section, InputText, InputTextarea, InputTextLookup, 
        ProductComponentsForm, ProductServicesForm
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
            validators: {
                componentValidators: [],
                serviceValidators: []
            },
            validate: ()=> {
                let errors = [];
                if (state.data.name == '') errors.push('name');
                if (state.data.description == '') errors.push('description');
                if (state.data.metaProduct == null) errors.push('product class');
                if (errors.length > 0)
                    state.error = `The following fields must not be empty: ${errors.join(', ')}.`;
                else state.error = '';
                if (state.validators.componentValidators.length > 0) {
                    state.validators.componentValidators.forEach( validator => {
                        errors = errors.concat(validator())});
                }
                if (state.validators.serviceValidators.length > 0) {
                    state.validators.serviceValidators.forEach( validator => {
                        errors = errors.concat(validator())});
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
                    service_templates: state.data.serviceTemplates
                }
                saveProductTemplate(state.id, productTemplate);
            }
        });

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

        const retrieveProductTemplateDetail = async (id)=> {
            state.isProcessing = true;
            const response = await ProductTemplateApi.retrieveProductTemplate(id);
            if (response) { 
                state.data = {
                    name: response.name,
                    description: response.description,
                    metaProduct: response.meta_product,
                    componentTemplates: response.component_templates,
                    serviceTemplates: response.service_templates
                };
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

        watch(()=> props.isOpen, async ()=> { 
            if (props.isOpen) {
                state.error = ''; 
                if (!state.isCreate && state.id != null) {
                    await retrieveProductTemplateDetail(state.id);} 
                populateMetaProductList();
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