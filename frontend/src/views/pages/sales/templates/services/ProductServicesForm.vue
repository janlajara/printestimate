<template>
    <Section heading="Services" heading-position="side">
        <div v-for="(service, key) in state.meta.services" :key="key">
            <ProductServiceForm
                :service="service"
                :value="state.getTemplateByMetaserviceId(service.id)"
                @input="data => {
                    state.setTemplateByMetaserviceId(service.id, data, key);
                    $emit('input', state.data.serviceTemplates);
                }"
                @load="event => {
                    state.setTemplateByMetaserviceId(service.id, event.data, key);
                    state.validators[key] = event.validator;
                    state.emitLoad();
                }"/> 
            <hr v-if="state.meta.services.length-1 > key" 
                class="my-4"/> 
        </div>
    </Section>
</template>
<script>
import Section from '@/components/Section.vue';
import ProductServiceForm from './ProductServiceForm.vue';

import {reactive, computed, watchEffect} from 'vue';
import {MetaProductApi} from '@/utils/apis.js';

export default {
    props: {
        metaProductId: [Number, String],
        value: {
            type: Array,
            default: ()=> []
        }
    },
    components: {
        Section, ProductServiceForm
    },
    emits: ['input', 'load'],
    setup(props, {emit}) {
        const state = reactive({
            id: computed(()=> props.metaProductId),
            errors: [],
            data: {
                serviceTemplates: []
            },
            validators: [],
            meta: {
                services: []
            },
            clear() {
                state.data.serviceTemplates = []
            },
            emitLoad() {
                emit('load', {
                    data: state.data.serviceTemplates,
                    validators: state.validators
                });
            },
            getTemplateByMetaserviceId(metaServiceId) {
                const template = state.data.serviceTemplates.find(
                    x=>x.meta_service == metaServiceId);
                return template;
            },
            setTemplateByMetaserviceId(metaServiceId, value, key) {
                const index = state.data.serviceTemplates.findIndex(
                    x=>x.meta_service == metaServiceId);
                if (index >= 0) state.data.serviceTemplates[index] = value;
                else state.data.serviceTemplates.splice(key, 0, value);
            }
        });

        const retrieveMetaProductServices = async (id) => {
            state.isProcessing = true;
            if (id) {
                const response = await MetaProductApi.retrieveMetaProductServices(id);
                if (response) {
                    state.meta.services = response.map(obj => ({
                        id: obj.id, sequence: obj.sequence,
                        name: obj.name, type: obj.type,
                        costingMeasure: obj.costing_measure,
                        metaOperations: obj.meta_operations.map( x => ({
                            id: x.id, name: x.name,
                            optionsType: x.options_type,
                            isRequired: x.is_required,
                            metaOperationOptions: x.meta_operation_options
                        })),
                        metaComponent: obj.meta_component,
                        estimateVariableType: obj.estimate_variable_type
                    }));
                }
            }
            state.isProcessing = false;
        }

        watchEffect(()=> { 
            if (props.value && props.value.length > 0) { 
                state.data.serviceTemplates = [...props.value];
                if (state.id) retrieveMetaProductServices(state.id);
            } else {state.clear();}
        });

        return {
            state
        }
    }    
}
</script>