<template>
    <Modal :heading="`${state.isCreate ? 'Add' : 'Edit'} Product Class`" 
        :is-open="$props.isOpen" @toggle="(value)=> $emit('toggle', value)"
        :buttons="[{color: 'primary', icon:'save', text:'Save', 
            action: state.save, disabled: state.isProcessing},]">
        <div v-if="state.error" 
            class="pt-4 text-sm text-red-600">*{{state.error}}</div>
        <Section heading="General Information" heading-position="side"> 
            <div class="md:grid md:gap-4 md:grid-cols-3">
                <InputText name="Name"  placeholder="Name" class="col-span-2"
                    type="text" :value="state.data.name" required
                    @input="value => state.data.name = value"/>
                <InputText name="Description"  placeholder="Description"  class="col-span-3"
                    type="text" :value="state.data.description" required
                    @input="value => state.data.description = value"/>
            </div>
        </Section>
    </Modal>
</template>

<script>
import Modal from '@/components/Modal.vue';
import Section from '@/components/Section.vue';
import InputText from '@/components/InputText.vue';

import {reactive, computed, watch} from 'vue';
import {MetaProductApi} from '@/utils/apis.js';

export default {
    components: {
        Modal, Section, InputText
    },
    props: {
        isOpen: Boolean,
        metaProductId: String,
        onAfterSave: Function
    },
    emits: ['toggle'],
    setup(props, {emit}) {
        const state = reactive({
            id: props.metaProductId,
            isCreate: computed(()=> props.metaProductId == null),
            isProcessing: false,
            error: '',
            data: {
                name: '', description: ''
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
                const metaProduct = {
                    name: state.data.name, 
                    description: state.data.description}
                saveMetaProduct(metaProduct);
            }
        });

        const retrieveMetaProduct = async (id)=> {
            state.isProcessing = true;
            const response = await MetaProductApi.retrieveMetaProduct(id);
            if (response) {
                state.data = {
                    name: response.name, description: response.description
                }
            }
            state.isProcessing = false;
        }

        const saveMetaProduct = async (metaProduct)=> {
            state.isProcessing = true;
            if (metaProduct) {
                let response = null;
                if (!state.isCreate && state.id) {
                    response = await MetaProductApi.updateMetaProduct(state.id, metaProduct);
                } else {
                    response = await MetaProductApi.createMetaProduct(metaProduct);
                }
                if (response) {
                    if (props.onAfterSave) props.onAfterSave();
                    emit('toggle', false);
                }
            }
            state.isProcessing = false;
        }

        watch(()=> props.isOpen, ()=> { 
            if (props.isOpen && state.id && !state.isCreate) {
                const id = parseInt(state.id);
                retrieveMetaProduct(id);
            }
        })

        return {
            state
        }
    }
}
</script>