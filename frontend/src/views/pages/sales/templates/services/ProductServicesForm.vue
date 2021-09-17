<template>
    <Section heading="Services" heading-position="side">
    </Section>
</template>
<script>
import Section from '@/components/Section.vue';

import {reactive, computed, watch} from 'vue';
import {MetaProductApi} from '@/utils/apis.js';

export default {
    props: {
        metaProductId: [Number, String]
    },
    components: {
        Section
    },
    setup(props) {
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
                    console.log(state.meta.services)
                }
            }
            state.isProcessing = false;
        }


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