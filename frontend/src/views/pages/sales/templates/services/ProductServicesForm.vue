<template>
    <Section heading="Services" heading-position="side">
        <div v-for="(service, key) in state.meta.services" :key="key">
            <ProductServiceForm
                :service="service"
                @input="data => {
                    state.data.serviceTemplates[key] = data;
                    $emit('input', state.data.serviceTemplates);
                }"
                @load="event => {
                    state.data.serviceTemplates[key] = event.data;
                    state.validators[key] = event.validator;
                }"/>
            <hr v-if="state.meta.services.length-1 > key" 
                class="my-4"/>
        </div>
    </Section>
</template>
<script>
import Section from '@/components/Section.vue';
import ProductServiceForm from './ProductServiceForm.vue';

import {reactive, computed, watch, onMounted} from 'vue';
import {MetaProductApi} from '@/utils/apis.js';

export default {
    props: {
        metaProductId: [Number, String]
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

        onMounted(()=> {
            emit('load', {
                data: state.data.serviceTemplates,
                validators: state.validators
            });
        });
        watch(()=> state.id, async ()=> {
            if (state.id) {
                await retrieveMetaProductServices(state.id);
            } else {
                state.clear()
            }
        });

        return {
            state
        }
    }    
}
</script>