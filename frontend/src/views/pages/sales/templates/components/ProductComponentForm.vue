<template>
    <div v-if="state.component != null">
        <p class="font-bold">{{state.component.name}}</p>
        <div v-if="state.error" 
            class="pt-4 text-sm text-red-600">*{{state.error}}</div>
        <div class="md:grid md:gap-4 md:grid-cols-4">
            <InputSelect name="Material" required 
                class="flex-grow" :class="`md:col-span-${state.meta.isPaperType? 4:3}`"
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
import InputText from '@/components/InputText.vue';
import DynamicInputField from '@/components/DynamicInputField.vue';
import ProductComponentSheetLayoutTabs from './sheetlayout/ProductComponentSheetLayoutTabs.vue';

import convert from 'convert';
import {roundNumber} from '@/utils/format.js';
import {reactive, onBeforeMount, onMounted, computed} from 'vue';

export default {
    props: {
        component: Object,
        value: Object
    },
    components: {
        InputSelect, InputText, DynamicInputField, ProductComponentSheetLayoutTabs
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
                converted_item_dimensions: {
                    width: computed(()=> {
                        let min = null;
                        let max = null;
                        if (state.meta.materialUom) {
                            const width_values = state.meta.sheet_layout.item_layouts.map(
                                x=> convert(x.width, x.uom).to(state.meta.materialUom));
                            if (width_values.length > 0) {
                                min = Math.min.apply(Math, width_values);
                                max = Math.max.apply(Math, width_values);
                            }
                        }
                        return {min, max}
                    }),
                    length: computed(()=> {
                        let min = null;
                        let max = null;
                        if (state.meta.materialUom) {
                            const length_values = state.meta.sheet_layout.item_layouts.map(
                                x=> convert(x.length, x.uom).to(state.meta.materialUom));
                            if (length_values.length > 0) {
                                min = Math.min.apply(Math, length_values);
                                max = Math.max.apply(Math, length_values);
                            }
                        }
                        return {min, max}
                    })
                },
                converted_machine_dimensions: {
                    width: computed(()=> {
                        let min = null;
                        let max = null;
                        const machine_obj = state.meta.machine_option_obj;
                        if (machine_obj && state.meta.materialUom) {
                            min = convert(machine_obj.min_sheet_width, 
                                machine_obj.uom).to(state.meta.materialUom);
                            max = convert(machine_obj.max_sheet_width, 
                                machine_obj.uom).to(state.meta.materialUom);
                        }
                        return {min, max};
                    }),
                    length: computed(()=> {
                        let min = null;
                        let max = null;
                        const machine_obj = state.meta.machine_option_obj;
                        if (machine_obj && state.meta.materialUom) {
                            min = convert(machine_obj.min_sheet_length, 
                                machine_obj.uom).to(state.meta.materialUom);
                            max = convert(machine_obj.max_sheet_length, 
                                machine_obj.uom).to(state.meta.materialUom);
                        }
                        return {min, max};
                    })
                }
            },
            emitInput: ()=> {
                emit('input', state.data);
            },
            executeRules: (attribute, value)=> {
                if (state.meta.isPaperType && attribute.name == 'size_uom') {
                    const width_value = state.data['width_value'] || 
                        state.meta.converted_machine_dimensions.width.max;
                    const length_value = state.data['length_value'] ||
                        state.meta.converted_machine_dimensions.length.max;
                    const w = Number(width_value);
                    const l = Number(length_value);
                    const asIsSizeUom = state.data['size_uom'] || value;
                    const toBeSizeUom = value;
                    const convertedWidth = convert(w, asIsSizeUom).to(toBeSizeUom);
                    const convertedLength = convert(l, asIsSizeUom).to(toBeSizeUom);
                    state.data['width_value'] = roundNumber(convertedWidth, 4); 
                    state.data['length_value'] = roundNumber(convertedLength, 4);
                }
            },
            getMinValue: (attribute)=> {
                let min = null;
                if (state.meta.materialUom && state.meta.isPaperType && 
                        ['width_value', 'length_value'].includes(attribute.name)) {
                    min = convert(1, 'inch').to(state.meta.materialUom);
                    min = roundNumber(min, 4);
                }
                return min;
            },
            getMaxValue: (attribute)=> {
                let max = null;
                if (state.meta.isPaperType) {
                    if (attribute.name == 'width_value') {
                        max = state.data.machine_option?
                            state.meta.converted_machine_dimensions.width.max : 
                            state.meta.converted_item_dimensions.width.max;
                    } else if (attribute.name == 'length_value') {
                        max = state.data.machine_option?
                            state.meta.converted_machine_dimensions.length.max : 
                            state.meta.converted_item_dimensions.length.max;
                    }
                    if (max) max = roundNumber(max, 4);
                }
                return max;
            },
            validate: ()=> {
                let errors = []
                if (state.data.material_templates.length == 0) 
                    errors.push('material_templates');
                if (state.data.quantity == 0)
                    errors.push('quantity')

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
                
                const dynamicProps = Object.entries(component)
                    .filter(x => !['meta_component', 'material_templates', 
                        'quantity', 'resourcetype'].includes(x[0]));
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
                itemLayouts = state.data.material_templates.map(x => 
                    getItemLayout(x));                
            }
            return itemLayouts;
        };

        return {
            state
        }
    }
}
</script>