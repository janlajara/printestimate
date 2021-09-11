<template>
    <Section heading="Components" heading-position="side">
        <div v-for="(component, key) in state.meta.components" :key="key">
            <span>{{component.name}}</span>
            <span class="capitalize">{{component.type}}</span>
            <div v-if="state.errors[key]" 
                class="pt-4 text-sm text-red-600">*{{state.errors[key]}}</div>
            <div class="md:grid md:gap-4 md:grid-cols-3">
                <InputSelect name="Material" required 
                    class="flex-grow md:col-span-2"
                    :multiple="component.allowMultipleMaterials"
                    v-if="component.metaMaterialOptions.length > 0"
                    @input="(value)=> {
                        const template = state.data.componentTemplates[key];
                        if (template) template['material_templates'] = value
                    }"
                    :options="component.metaMaterialOptions.map(c=>{
                        const template = state.data.componentTemplates[key];
                        let options = {value: c.id, label: c.label};
                        if (template && template['material_templates']) 
                            options['isSelected'] = template['material_templates'].includes(c.id);
                        return options;
                    })"/>
                <InputSelect name="Machine" 
                    v-if="component.metaMachineOptions.length > 0"
                    @input="(value)=> {
                        const template = state.data.componentTemplates[key];
                        if (template) template['machine_option'] = value;
                    }"
                    :options="component.metaMachineOptions.map(c=>{
                        const template = state.data.componentTemplates[key];
                        let options = {value: c.id, label: c.label};
                        if (template) options['isSelected'] = template['machine_option'] == c.id;
                        return options;
                    })"/>
                <component v-for="(field, i) in component.additionalFields" :key="i"
                    :is="field.inputComponent" :required="field.required"
                    :name="field.label" :type="field.inputType"
                    @input="(value)=>{
                        const template = state.data.componentTemplates[key];
                        if (template) template[field.name] = value;
                    }"
                    :value="state.data.componentTemplates[key] ? 
                        state.data.componentTemplates[key][field.name] : ''"
                    :options="(field.options)?
                        field.options.map(option => {
                            const template = state.data.componentTemplates[key];
                            if (template) option['isSelected'] = option.value == template[field.name];
                            return {...option}
                        }) : null"/>
                <InputText name="Quantity"  placeholder="Quantity" required
                    type="number" :value="state.data.componentTemplates[key]?
                        state.data.componentTemplates[key]['quantity'] : ''" 
                    @input="value => {
                        const template = state.data.componentTemplates[key];
                        if (template) template['quantity'] = value
                    }"/>
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
    emits: ['input'],
    setup(props, {emit}) {
        const state = reactive({
            id: computed(()=> props.metaProductId),
            errors: [],
            data: {
                componentTemplates: []
            },
            meta: {
                components: [],
                componentAdditionalFieldsMap: [],
            },
            validate: ()=> {
                let errorCount = 0;
                state.data.componentTemplates.forEach( (x, i) => {
                    let errors = [];
                    const additionalFields = state.meta.components[i].additionalFields;
                    const fields = Object.entries(x)
                        .filter(y => additionalFields.find(z => z.name == y[0]) != null); 
                    fields.forEach(y => {
                        const fieldKey = y[0]; const fieldVal = y[1];
                        const fieldMeta = additionalFields.find(y => fieldKey == y.name);
                        if (fieldMeta.required && fieldVal == null) errors.push(fieldKey);
                    });
                    if (errors.length > 0)
                        state.errors[i] = `The following fields must not be empty: ${errors.join(', ')}.`;
                    else state.errors[i] = '';
                    errorCount += errors.length;
                });
                return errorCount > 0;
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

        const initializeComponentForms = () => {
            const componentTemplates = state.meta.components.map(component => {
                let componentProps = {
                    'material_templates': [],
                    'machine_option': null,
                    'quantity': 1};
                component.additionalFields
                    .forEach(field => {
                        componentProps[field.name] = null;
                    });
                return componentProps;
            });
            state.data.componentTemplates = componentTemplates;
            console.log(state.data.componentTemplates);
        }

        onBeforeMount(getComponentTemplateFields);
        watch(()=> state.id, async ()=> {
            if (state.id) {
                await retrieveMetaProductComponents(state.id);
                initializeComponentForms();
            }
        });
        watch(()=> {
            const toWatch = state.data.componentTemplates.map(x => 
                Object.assign({}, x));
            return toWatch
        }, ()=> {
            emit('input', {
                'data': state.data.componentTemplates,
                'validator': state.validate
            });
        });

        return {
            state
        }
    }
}
</script>