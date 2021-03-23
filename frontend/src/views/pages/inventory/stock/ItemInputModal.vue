<template>
    <Modal :heading="`${($props.isCreate)? 'Create' : 'Edit'} Item`"
        :is-open="$props.isOpen" @toggle="(value)=> $emit('toggle', value)"
        :buttons="[{color: 'primary', icon:'save', text:'Save',
                    action:()=>modal.save(), disabled: modal.isProcessing},]">
        <Section heading="General Information">
            <span v-if="modal.error" class="text-sm text-red-600">*{{modal.error}}</span>
            <div class="md:grid md:grid-cols-4 md:gap-4">
                <InputText type="text" name="Name" required
                    @input="(value)=>modal.form.name = value"
                    :value="modal.form.name"/>
                <InputSelect name="Type" required
                    :disabled="!$props.isCreate"
                    @input="(value)=>modal.form.type = value"
                    :options="modal.itemTypes.map(it=>({
                        value: it.value, label: it.label,
                        isSelected: modal.form.type == it.value
                    }))"/>
                <InputSelect name="Base Unit" required
                    @input="(value)=>modal.form.baseUnit = value"
                    :options="modal.baseStockUnits.map(bu=>({
                        value: bu.id, label: bu.name,
                        isSelected: modal.form.baseUnit == bu.id
                    }))"/>
                <InputSelect name="Alternate Unit" 
                    @input="(value)=>modal.form.altUnit = value"
                    :options="modal.altStockUnits.map(au=>({
                       value: au.id, label: au.name,
                       isSelected: modal.form.altUnit == au.id 
                    }))"/>
            </div>    
        </Section>
        <Section heading="Properties" v-if="modal.itemProperties">
            <div class="md:grid md:grid-cols-4 md:gap-4">
                <component v-for="(itemProp, key) in modal.itemProperties" :key="key"
                    :is="itemProp.inputComponent" :required="itemProp.required"
                    :name="itemProp.label" :type="itemProp.inputType"
                    @input="(value)=>modal.form.properties[itemProp.name] = value"
                    :value="modal.form.properties[itemProp.name]"
                    :options="(itemProp.options)?
                        itemProp.options.map(option => ({
                            ...option,
                            isSelected: option.value == modal.form.properties[itemProp.name]
                        })) : null"/>
            </div>
        </Section>
    </Modal>
</template>

<script>
import Modal from '@/components/Modal.vue';
import Section from '@/components/Section.vue';
import InputSelect from '@/components/InputSelect.vue';
import InputText from '@/components/InputText.vue';

import {reactive, watch} from 'vue';
import {ItemApi, ItemPropertiesApi, BaseStockUnitApi} from '@/utils/apis.js';

export default {
    name: 'ItemInputModal',
    components: {
        Modal, Section, InputSelect, InputText
    },
    props: {
        isCreate: {
            type: Boolean,
            default: true
        },
        isOpen: {
            type: Boolean,
            required: true
        },
        data: Object,
        onAfterSave: Function
    },
    emits: ['toggle'],
    setup(props, {emit}){
        const modal = reactive({
            isProcessing: false,
            form: {
                properties: {
                    resourcetype: null
                },
            },
            itemTypes: [{}],
            itemProperties: null,
            baseStockUnits: [{}],
            altStockUnits: [{}],
            error: '',
            validate: ()=>{
                let errors = [];
                if (modal.form.name.length == 0) errors.push('name');
                if (modal.form.type == null) errors.push('item type');
                if (modal.form.baseUnit == null) errors.push('base unit');

                Object.entries(modal.form.properties).forEach(entry => {
                    const key = entry[0]; 
                    const val = entry[1];
                    const ref = modal.itemProperties.find(prop => prop.name==key);
                    if (ref && ref.required && 
                        (val == null || (isNaN(val) && val.trim() == ''))) 
                        errors.push(key.replaceAll('_', ' '));
                });

                if (errors.length > 0)
                    modal.error = `The following fields must not be empty: ${errors.join(', ')}.`;
                else modal.error = '';

                return errors.length > 0;
            },
            save: async ()=> {
                if (modal.validate()) return;
                const data = modal.form;
                const request = {
                    name: data.name, type: data.type, 
                    override_price: 0, is_override_price: false,
                    base_uom: data.baseUnit, alternate_uom: data.altUnit,
                    properties: Object.assign({}, data.properties)
                }
                modal.isProcessing = true;
                let response;
                
                if (props.isCreate) response = await ItemApi.createItem(request);
                else response = await ItemApi.updateItem(modal.form.id, request);
                
                if (!response.error) { 
                    emit('toggle', false);
                } else {
                    modal.error = response.error;
                }
                if (props.onAfterSave) await props.onAfterSave();
                modal.isProcessing = false;
            },
        });

        watch(()=> props.isOpen, ()=> { 
            modal.error = ''; 
            const data = props.data;

            if (data != null && !props.isCreate){ 
                modal.form = {
                    id: data.id, name: data.name,
                    type: data.type, baseUnit: data.baseUom.value,
                    altUnit: data.altUom.value, 
                    properties: Object.assign({},data.properties)
                }; 
            } else {
                modal.form = {
                    name:'', type: null,
                    baseUnit: null, altUnit: null,
                    properties: {},
                }
                modal.itemProperties = null; 
            }

        });

        // Pre-load the data for item types, stock units, items
        const populateItemTypes = async() => {
            const response = await ItemApi.getItemTypes();
            if (response && !response.error) {
                const itemTypes = response.map(type=> ({
                    value: type.value, label: type.display_name
                }));
                modal.itemTypes = itemTypes;
            }
        };
        const populateStockUnits = async() => {
            const response = await BaseStockUnitApi.listBaseStockUnits();
            if (response  && !response.error) {
                const baseStockUnits = response.map(bu=> ({
                    id: bu.id, name: bu.name, 
                    alternateStockUnits: bu.alternate_stock_units.map(au => ({
                        id: au.id, name: au.name
                    }))
                }));
                modal.baseStockUnits = baseStockUnits;
            }
        }
        populateItemTypes();
        populateStockUnits();

        // Make AlternateStockUnit select options  dependent on selected 
        // BaseStockUnit option.
        watch(()=> modal.form.baseUnit,()=>{
            if (modal.baseStockUnits && modal.form.baseUnit) {
                const bUnits = Array.from(modal.baseStockUnits)
                    .map(b => Object.assign({}, b));
                const aUnits = bUnits.find(bu=>bu.id==modal.form.baseUnit)
                        .alternateStockUnits
                modal.altStockUnits = aUnits;
            } 
        });

        // Fetch the property fields for the selected item type and 
        // load the data into the form
        const loadProperties = async(itemType)=> {
            modal.error = '';
            const response = await ItemPropertiesApi.getItemProperties(itemType);
            if (response && !response.error) {
                const responseData = Object.entries(response)
                    .filter(entry => entry[0] != 'id');
                const itemProps = responseData.map(entry => {
                        const name = entry[0];
                        const meta = entry[1];  
                        let inputComponent;
                        let inputType;
                        let options;
                        if (meta.type == 'choice') {
                            inputComponent = 'InputSelect';
                            options = meta.choices.map(choice => ({
                                label: choice.display_name,
                                value: choice.value
                            }))
                        } else {
                            inputComponent = 'InputText';
                            if (meta.type == 'integer') inputType = 'number';
                            else if (meta.type == 'float') inputType = 'decimal';
                            else inputType = 'text';
                        }
                        return {
                            name, label: meta.label, required: meta.required,
                            inputComponent, inputType, options
                        } 
                    });
                modal.itemProperties = (itemProps.length > 0)?
                    itemProps : null;

                if (props.isCreate) {
                    modal.form.properties = {};
                    responseData.forEach( entry => {
                        const name = entry[0];
                        modal.form.properties[name] = null;
                    });
                    modal.form.properties.resourcetype = itemType;
                }
            }
        };
        watch(()=> modal.form.type, ()=> {
            const itemType = modal.form.type;
            if (itemType) {
                loadProperties(itemType);
            }
        });

        return {
            modal
        }
    }
}
</script>