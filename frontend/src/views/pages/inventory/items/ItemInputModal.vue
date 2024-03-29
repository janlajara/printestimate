<template>
    <Modal :heading="`${($props.isCreate)? 'Create' : 'Edit'} Item`"
        :is-open="$props.isOpen" @toggle="(value)=> $emit('toggle', value)"
        :buttons="[{color: 'primary', icon:'save', text:'Save',
                    action:()=>modal.save(), disabled: modal.isProcessing},]">
        <div v-if="modal.error" 
            class="pt-4 text-sm text-red-600">*{{modal.error}}</div>
        <Section heading="General Information" heading-position="side"> 
            <div class="md:grid md:grid-cols-3 md:gap-4">
                <InputText type="text" name="Name" required class="md:col-span-2"
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
                <InputText :name="`Price per ${modal.form.baseUnit? 
                        modal.baseStockUnits
                            .find(x => x.id == modal.form.baseUnit)
                            .name: 
                        'base unit'}`" 
                    type="money" required
                    :prefix="currency.symbol"
                    @input="(value)=> modal.form.overridePrice = value"
                    :value="modal.form.overridePrice"/>
            </div>    
        </Section>
        <hr/>
        <Section heading="Properties" heading-position="side"
            v-if="modal.itemProperties">
            <div class="md:grid md:grid-cols-3 md:gap-4">
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

import {reactive, watch, inject} from 'vue';
import {useRouter} from 'vue-router';
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
        const currency = inject('currency')
        const router = useRouter();
        const modal = reactive({
            isProcessing: false,
            form: {
                name:'', type: null,
                baseUnit: null, altUnit: null,
                properties: {
                    resourcetype: null
                },
                overridePrice: 0
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
                    const ref = modal.itemProperties ?
                        modal.itemProperties.find(prop => prop.name==key) : null;
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
                    override_price: data.overridePrice, is_override_price: true,
                    base_uom: data.baseUnit, alternate_uom: data.altUnit,
                    properties: Object.assign({}, data.properties)
                }
                modal.isProcessing = true;
                let response;
                
                if (props.isCreate) response = await ItemApi.createItem(request);
                else response = await ItemApi.updateItem(modal.form.id, request);
                
                if (!response.error) { 
                    emit('toggle', false);
                    if (props.isCreate) {
                        router.push({
                            name: 'inventory-item-detail',
                            params: {id: response.data.id}});  
                    }
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
                    type: data.type, baseUnit: data.baseUom.id,
                    altUnit: data.altUom ? data.altUom.id : null, 
                    overridePrice: data.overridePrice,
                    properties: Object.assign({},data.properties)
                }; 
            } else {
                modal.form = {
                    name:'', type: null,
                    baseUnit: null, altUnit: null,
                    overridePrice: 0,
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
                    .filter(entry => entry[0] != 'properties_id');
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
            modal, 
            currency
        }
    }
}
</script>