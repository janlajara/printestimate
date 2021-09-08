<template>
    <Section heading="Components" heading-position="side"> 
        <div v-for="(component, key) in state.meta.components" :key="key">
            <span>{{component.name}}</span>
            <span class="capitalize">{{component.type}}</span>
            <div class="md:grid md:gap-4 md:grid-cols-3">
                <InputSelect name="Material" required 
                    class="flex-grow md:col-span-2"
                    :multiple="component.allowMultipleMaterials"
                    v-if="component.metaMaterialOptions.length > 0"
                    @input="()=>{}"
                    :options="component.metaMaterialOptions.map(c=>({
                        value: c.id, label: c.label
                    }))"/>
                <InputSelect name="Machine" required 
                    v-if="component.metaMachineOptions.length > 0"
                    @input="()=>{}"
                    :options="component.metaMachineOptions.map(c=>({
                        value: c.id, label: c.label
                    }))"/>
                <component v-for="(field, key) in component.additionalFields" :key="key"
                    :is="field.inputComponent" :required="field.required"
                    :name="field.label" :type="field.inputType"
                    @input="()=>{}"
                    :value="''"
                    :options="(field.options)?
                        field.options.map(option => ({
                            ...option,
                            isSelected: option.value != ''
                        })) : null"/>
            </div>
        </div>
    </Section>
</template>
<script>
import Section from '@/components/Section.vue';
import InputSelect from '@/components/InputSelect.vue';
import InputText from '@/components/InputText.vue';

import {reactive, watch, computed, onBeforeMount} from 'vue';
import {MetaProductApi, ComponentTemplateApi} from '@/utils/apis.js';

export default {
    props: {
        metaProductId: [Number, String]
    },
    components: {
        Section, InputSelect, InputText
    },
    setup(props) {
        const state = reactive({
            id: computed(()=> props.metaProductId),
            data: {
                componentTemplates: []
            },
            meta: {
                components: [],
                componentAdditionalFieldsMap: [],
            }
        })

        const retrieveMetaProductComponents = async (id) => {
            state.isProcessing = true;
            if (id) {
                const response = await MetaProductApi.retrieveMetaProductComponents(id);
                if (response) {
                    console.log(response);
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
                    console.log(state.meta.components);
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
                        fields: Object.entries(obj.fields).map( entry => {
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
                    }))
            }
        }

        onBeforeMount(getComponentTemplateFields);
        watch(()=> state.id, ()=> {
            if (state.id) {
                retrieveMetaProductComponents(state.id);
            }
        })

        return {
            state
        }
    }
}
</script>