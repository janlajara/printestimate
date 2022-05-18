<template>
    <div v-if="state.component != null">
        <p class="font-bold">{{state.component.name}}</p>
        <div v-if="state.error" 
            class="pt-4 text-sm text-red-600">*{{state.error}}</div>
        <div class="md:grid md:gap-4 md:grid-cols-4">
            <template v-if="state.meta.isPaperType && state.component.allowMultipleMaterials">
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
                    :multiple="state.component.allowMultipleMaterials"
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
        <ProductComponentSheetLayoutTabs
            v-if="state.meta.isPaperType && 
                state.meta.sheet_layout.material_layout.length && 
                state.meta.sheet_layout.item_layouts"
            :machine-id="state.meta.machine_option_obj? state.meta.machine_option_obj.id : null"
            :material-layout="state.meta.sheet_layout.material_layout"
            :item-layouts="state.meta.sheet_layout.item_layouts"/>
    </div>
</template>
<script>
import InputSelect from '@/components/InputSelect.vue';
import InputSelectDraggableList from '@/components/InputSelectDraggableList.vue';
import InputText from '@/components/InputText.vue';
import DynamicInputField from '@/components/DynamicInputField.vue';
import ProductComponentSheetLayoutTabs from './sheetlayout/ProductComponentSheetLayoutTabs.vue';

import {ProductComponentHelper} from './utils/product.utils.js';
import {reactive, onBeforeMount, onMounted, computed, watchEffect} from 'vue';

export default {
    props: {
        component: Object,
        value: Object
    },
    components: {
        InputSelect, InputSelectDraggableList, InputText, 
        DynamicInputField, ProductComponentSheetLayoutTabs
    },
    emits: ['input', 'load'],
    setup(props, {emit}) {
        const state = reactive({
            component: props.component,
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
                materialUom: computed(()=> state.data['size_uom']),
                isPaperType: computed(()=> state.data.resourcetype == 'paper'),
                sheet_layout: {
                    material_layout: computed(()=>getMaterialLayout()),
                    item_layouts: computed(()=>getItemLayouts()),
                },
                machine_option_obj: computed(()=>{
                    const machineOption = state.component.metaMachineOptions.find(x => 
                        x.id == state.data.machine_option);
                    let obj = null;
                    if (machineOption) obj = machineOption.machine_obj;
                    return obj;
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
            if (props.value) {
                const component = props.value; 
                state.data.material_templates = component.material_templates;
                state.data.machine_option = component.machineOption;
                state.data.quantity = component.quantity;
                
                // Initialize data dynamically according to given props 
                const dynamicProps = Object.entries(component)
                    .filter(x => !['meta_component', 'material_templates', 
                        'quantity', 'resourcetype'].includes(x[0]));
                dynamicProps.forEach(x => {
                    const key = x[0];
                    const value = x[1];
                    state.data[key] = value;
                });
                
                // Initialize helper class
                state.helper = ProductComponentHelper.create(
                    component.resourcetype,
                    state.meta.sheet_layout.item_layouts,
                    state.meta.machine_option_obj,
                    state.meta.materialUom)
            }
        });
        onMounted(()=> {
            emit('load', {
                data: state.data,
                validator: state.validate
            });
        });
        watchEffect(()=> {
            // Update helper class
            if (state.helper) {
                state.helper.rawMaterialDimensions = state.meta.sheet_layout.item_layouts;
                state.helper.machine = state.meta.machine_option_obj;
                state.helper.targetUom = state.meta.materialUom;
            }
        })

        const getMaterialLayout = ()=> {
            let materialLayout = null;
            if (state.meta.isPaperType) {
                return {
                    width: state.data['width_value'],
                    length: state.data['length_value'],
                    uom: state.data['size_uom']}
            }
            return materialLayout;
        }

        const getItemLayouts = () => {
            let itemLayouts = [];
            const getItemLayout = (x) => {
                const metaMaterialOption = 
                    state.component.metaMaterialOptions.find(
                        y => y.id == x.meta_material_option);
                const itemLayout = {
                    width: metaMaterialOption.properties.width_value, 
                    length: metaMaterialOption.properties.length_value,
                    uom: metaMaterialOption.properties.size_uom,
                    label: metaMaterialOption.label
                }
                return itemLayout;
            }
            if (state.meta.isPaperType) {
                itemLayouts = state.data.material_templates
                    .filter((item, index) => 
                        state.data.material_templates.findIndex(x=>
                            x.meta_material_option == item.meta_material_option)
                        === index)
                    .map(x => getItemLayout(x));     
            }
            return itemLayouts;
        };

        return {
            state
        }
    }
}
</script>