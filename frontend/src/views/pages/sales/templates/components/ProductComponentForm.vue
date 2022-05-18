<template>
    <div v-if="state.component != null">
        <p class="font-bold">{{state.component.name}}</p>
        <div v-if="state.error" 
            class="pt-4 text-sm text-red-600">*{{state.error}}</div>
        <div class="md:grid md:gap-4 md:grid-cols-4">
            <template v-if="state.component.allowMultipleMaterials">
                <InputSelectDraggableList
                    name="Material" required 
                    class="flex-grow md:col-span-4"
                    @input="(value)=> {
                        state.data.material_templates = value.map(x => ({
                            meta_material_option: x
                        }));
                        state.emitInput();
                    }"
                    :options="state.component.metaMaterialOptions.map(
                        c=>({value: c.id, label: c.label}))"
                    :value="state.data.material_templates
                        .map(x => x.meta_material_option)"/>
            </template>
            <template v-else>
                <InputSelect 
                    name="Material" required class="flex-grow" 
                    :class="`md:col-span-${state.meta.isPaperType? 4:3}`"
                    :multiple="false"
                    v-if="state.component.metaMaterialOptions.length > 0"
                    @input="(value)=> {
                        if (!Array.isArray(value)) value = [value];
                        state.data.material_templates = value.map(x => ({
                            meta_material_option: x
                        }));
                        state.emitInput();
                    }"
                    :options="state.component.metaMaterialOptions.map(c=>{
                        let options = {
                            value: c.id, label: c.label,
                            isSelected: state.data.material_templates
                                .map(x => x.meta_material_option)
                                .includes(c.id)};
                        return options;
                    })"/>
            </template>
            
            <InputSelect name="Machine" class="flex-grow md:col-span-2"
                v-if="state.component.metaMachineOptions.length > 0"
                @input="(value)=> {
                    state.data.machine_option = value;
                    state.emitInput();
                }"
                :options="state.component.metaMachineOptions.map(c=>{
                    let options = {
                        value: c.id, label: c.label,
                        isSelected: state.data.machine_option == c.id};
                    return options;
                })"/>
            <DynamicInputField :key="i" :attribute="attribute"
                v-for="(attribute, i) in state.component.additionalFields"
                :number="['width_value', 'length_value'].includes(attribute.name)"
                :value="state.data[attribute.name]"
                :min="state.getMinValue(attribute)"
                :max="state.getMaxValue(attribute)"
                @load="value => state.data[attribute.name] = value" 
                @input="value => {
                    state.executeRules(attribute, value);
                    state.data[attribute.name] = value;
                    state.emitInput();
                }"/>
            <InputText name="Quantity"  placeholder="Quantity" required
                type="number" :value="state.data.quantity" :min="1"
                @input="value => {
                    state.data.quantity = value;
                    state.emitInput();
                }"/>
        </div>
        <ProductComponentLayoutTabs
            v-if="state.data.resourcetype != 'other'"
            :machine="state.meta.machine"
            :final-material-layout="state.meta.material_layout.final_material_layout"
            :raw-material-layouts="state.meta.material_layout.raw_material_layouts"/>
    </div>
</template> 
<script>
import InputSelect from '@/components/InputSelect.vue';
import InputSelectDraggableList from '@/components/InputSelectDraggableList.vue';
import InputText from '@/components/InputText.vue';
import DynamicInputField from '@/components/DynamicInputField.vue';
import ProductComponentLayoutTabs from './layout/ProductComponentLayoutTabs.vue';

import {ProductComponentHelper} from './utils/product.utils.js';
import {reactive, onBeforeMount, onMounted, computed} from 'vue';

export default {
    props: {
        component: Object,
        value: Object
    },
    components: {
        InputSelect, InputSelectDraggableList, InputText, 
        DynamicInputField, ProductComponentLayoutTabs
    },
    emits: ['input', 'load'],
    setup(props, {emit}) {
        const state = reactive({
            component: computed(()=> props.component),
            error: null,
            data: {
                meta_component: props.component.id,
                material_templates: [],
                machine_option: null,
                quantity: 1,
                resourcetype: props.component.type,
            },
            helper: null,
            meta: {
                machine: computed(()=> {
                    if (state.helper) return state.helper.machine;
                }),
                material_layout: computed(()=>{
                    let finalMaterialLayout = null;
                    let rawMaterialLayouts = null;
                    if (state.helper) {
                        finalMaterialLayout = state.helper.finalMaterialDimensions;
                        rawMaterialLayouts = state.helper.rawMaterialDimensions;
                    }
                    return {
                        final_material_layout: finalMaterialLayout,
                        raw_material_layouts: rawMaterialLayouts
                    }
                }),
                converted_item_dimensions: computed(()=> {
                    return (state.helper)? state.helper.minMaxItemDimensions : null;
                }),
                converted_machine_dimensions: computed(()=> {
                    return (state.helper)? state.helper.minMaxMachineDimensions : null;
                }),
            },
            emitInput: ()=> {
                emit('input', state.data);
            },
            executeRules: (attribute, value)=> {
                if (state.helper) state.helper.applyAttributeRules(
                    attribute.name, value, state.data);
            },
            getMinValue: (attribute)=> {
                if (state.helper) return state.helper.getAttributeMinValue(attribute.name);
            },
            getMaxValue: (attribute)=> {
                if (state.helper) return state.helper.getAttributeMaxValue(attribute.name);
            },
            validate: ()=> {
                let errors = []
                if (state.data.material_templates.length == 0) 
                    errors.push('material_templates');
                if (state.data.quantity == 0)
                    errors.push('quantity')

                // If there are required fields with no values,
                // include said fields in the validation error
                const additionalFields = state.component.additionalFields;
                if (additionalFields) {
                    const fields = Object.entries(state.data)
                        .filter(y => additionalFields.find(z => z.name == y[0]) != null); 
                    fields.forEach(y => {
                        const fieldKey = y[0]; const fieldVal = y[1];
                        const fieldMeta = additionalFields.find(y => fieldKey == y.name);
                        if (fieldMeta.required && fieldVal == null) errors.push(fieldKey);
                    });
                }

                if (errors.length > 0)
                    state.error = `The following fields must not be empty: ${errors.join(', ')}.`;
                else state.error = '';
                return errors;
            }
        });

        onBeforeMount(()=> {
            if (props.component) {
                // Initialize helper class
                const propsComponent = props.component;
                state.helper = ProductComponentHelper.create(
                    propsComponent.type, state.data, propsComponent);
            }

            if (props.value) {
                const propsValue = props.value; 
                state.data.material_templates = propsValue.material_templates;
                state.data.machine_option = propsValue.machineOption;
                state.data.quantity = propsValue.quantity;
                
                // Initialize existing data dynamically according to given props 
                const dynamicProps = Object.entries(propsValue)
                    .filter(x => !['meta_component', 'material_templates', 
                        'quantity', 'resourcetype', 'machine_option_obj']
                    .includes(x[0]));
                dynamicProps.forEach(x => {
                    const key = x[0];
                    const value = x[1];
                    state.data[key] = value;
                });
            }
        });
        onMounted(()=> {
            emit('load', {
                data: state.data,
                validator: state.validate
            });
        });

        return {
            state
        }
    }
}
</script>