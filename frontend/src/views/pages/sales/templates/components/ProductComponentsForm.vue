<template>
    <Section heading="Components" heading-position="side">
        <div v-for="(component, key) in state.meta.components" :key="key">
            <ProductComponentForm 
                :component="component"
                :value="state.data.componentTemplates[key]"
                @input="data => {
                    state.data.componentTemplates[key] = data;
                    $emit('input', state.data.componentTemplates);
                }"
                @load="event => {
                    state.data.componentTemplates[key] = event.data;
                    state.validators[key] = event.validator;
                    state.emitLoad();
                }"/>
            <hr v-if="state.meta.components.length-1 > key" 
                class="my-4"/>
        </div>
    </Section>
</template>
<script>
import Section from '@/components/Section.vue';
import ProductComponentForm from './ProductComponentForm.vue';

import {reactive, computed, onBeforeMount, onMounted} from 'vue';
import {MetaProductApi, ComponentTemplateApi} from '@/utils/apis.js';

export default {
    props: {
        metaProductId: [Number, String],
        value: {
            type: Array,
            default: ()=> []
        }
    },
    components: {
        Section, ProductComponentForm
    },
    emits: ['input', 'load'],
    setup(props, {emit}) { 
        const state = reactive({
            id: computed(()=> props.metaProductId),
            errors: [],
            data: {
                componentTemplates: []
            },
            validators: [],
            meta: {
                components: [],
                componentAdditionalFieldsMap: [],
            },
            emitLoad() {
                emit('load', {
                    data: state.data.componentTemplates,
                    validators: state.validators
                });
            },
            clear() {
                state.data = {
                    componentTemplates: []}
                state.meta.components = []
            }
        });

        const retrieveMetaProductComponents = async (id) => {
            state.isProcessing = true;
            if (id) {
                const response = await MetaProductApi.retrieveMetaProductComponents(id);
                if (response) {
                    state.meta.components = response.map(obj=> ({
                        id: obj.id,
                        name: obj.name,
                        type: obj.type,
                        additionalFields: state.meta.componentAdditionalFieldsMap
                            .find(x => x.type == obj.type).fields,
                        allowMultipleMaterials: obj.allow_multiple_materials,
                        metaEstimateVariables: obj.meta_estimate_variables,
                        metaMaterialOptions: obj.meta_material_options,
                        metaMachineOptions: obj.meta_machine_options
                    }));
                }
            }
            state.isProcessing = false;
        }
        
        const getComponentTemplateFields = async () => {
            const response = await ComponentTemplateApi.getComponentMetaData();
            if (response) {
                state.meta.componentAdditionalFieldsMap = response.data
                    .map(obj => ({
                        type: obj.type, 
                        fields: Object.entries(obj.fields)
                                .filter(entry => !entry[1].read_only)
                                .map( entry => {
                            const key = entry[0];
                            const value = entry[1];
                            let inputComponent;
                            let inputType;
                            let options;
                            if (value.type == 'choice') {
                                inputComponent = 'InputSelect';
                                options = value.choices.map(choice => ({
                                    label: choice.display_name,
                                    value: choice.value
                                }))
                            } else {
                                inputComponent = 'InputText';
                                if (value.type == 'integer') inputType = 'number';
                                else if (value.type == 'float') inputType = 'decimal';
                                else inputType = 'text';
                            }
                            return {
                                name: key, label: value.label, required: value.required,
                                inputComponent, inputType, options
                            } 
                        })
                    }));
            }
        }

        onBeforeMount(getComponentTemplateFields);
        onMounted(async ()=> {
            if (props.value) {
                state.data.componentTemplates = props.value;
                if (state.id) await retrieveMetaProductComponents(state.id);
            } else {state.clear()}
        });

        return {
            state
        }
    }
}
</script>