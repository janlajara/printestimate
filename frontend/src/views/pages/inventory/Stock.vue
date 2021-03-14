<template>
    <Page title="Inventory : Stock">
        <Section>
            <Button color="secondary" :action="()=>item.toggle(true)">
                Create Item</Button>
        </Section>
        <Modal :heading="`${(item.modal.isCreate)? 'Create' : 'Edit'} Item`"
            :is-open="item.modal.IsOpen" @toggle="item.toggle"
            :buttons="[{color: 'primary', icon:'save', text:'Save',
                        action:()=>item.save(), disabled: item.isProcessing},]">
            <Section heading="General Information">
                <span v-if="item.error" class="text-sm text-red-600">*{{item.error}}</span>
                <div class="md:grid md:grid-cols-4 md:gap-4">
                    <InputText type="text" name="Name" required
                        @input="(value)=>item.modal.selected.name = value"
                        :value="item.modal.selected.name"/>
                    <InputSelect name="Type" required
                        @input="(value)=>item.modal.selected.itemType = value"
                        :options="item.modal.itemTypes.map(it=>({
                            value: it.value, label: it.label,
                            isSelected: item.modal.selected.itemType == it.value
                        }))"/>
                    <InputSelect name="Base Unit" required
                        @input="(value)=>item.modal.selected.baseUnit = value"
                        :options="item.modal.baseStockUnits.map(bu=>({
                            value: bu.id, label: bu.name,
                            isSelected: item.modal.selected.baseUnit == bu.id
                        }))"/>
                    <InputSelect name="Alternate Unit" 
                        @input="(value)=>item.modal.selected.altUnit = value"
                        :options="item.modal.altStockUnits"/>
                </div>    
            </Section>
            <Section heading="Properties" v-if="item.modal.itemProperties">
                <div class="md:grid md:grid-cols-4 md:gap-4">
                    <component v-for="(itemProp, key) in item.modal.itemProperties" :key="key"
                        :is="itemProp.inputComponent" :required="itemProp.required"
                        :name="itemProp.label" :type="itemProp.inputType"
                        @input="(value)=>item.modal.selected.properties[itemProp.name] = value"
                        :value="item.modal.selected.properties[itemProp.name]"
                        :options="itemProp.options"/>
                </div>
            </Section>
        </Modal>
    </Page>
</template>

<script>
import Page from '@/components/Page.vue';
import Section from '@/components/Section.vue';
import Button from '@/components/Button.vue' ;
import Modal from '@/components/Modal.vue';
import InputText from '@/components/InputText.vue';
import InputSelect from '@/components/InputSelect.vue';

import {reactive, computed, watch} from 'vue';
import {ItemApi, ItemPropertiesApi, BaseStockUnitApi} from '@/utils/apis.js';

export default {
    name: 'Stock',
    components: {
        Page, Section, Button, Modal, InputText, InputSelect
    },
    setup() {
        const item = reactive({
            modal: {
                isOpen: false, 
                isCreate: computed(()=> item.modal.selected.id == null),
                selected: {},
                itemTypes: [{}],
                itemProperties: null,
                baseStockUnits: [{}],
                altStockUnits: [{}]
            },
            list: [{}],
            isProcessing: false,
            error: '',
            toggle: (value, id=null)=>{
                item.error = ''; 
                if (id){
                    console.log(id);
                } else {
                    item.modal.selected = {
                        name:'', itemType: null,
                        baseUnit: null, altUnit: null,
                        properties: {},
                    }
                    item.modal.itemProperties = null; 
                }
                item.modal.IsOpen = value;
            },
            validate: ()=>{
                let errors = [];
                if (item.modal.selected.name.length == 0) errors.push('name');
                if (item.modal.selected.itemType == null) errors.push('item type');
                if (item.modal.selected.baseUnit == null) errors.push('base unit');

                Object.entries(item.modal.selected.properties).forEach(entry => {
                    const key = entry[0]; 
                    const val = entry[1];
                    const ref = item.modal.itemProperties.find(prop => prop.name==key);
                    if (ref && ref.required && (val == null || val.trim() == '')) 
                        errors.push(key.replaceAll('_', ' '));
                });

                if (errors.length > 0)
                    item.error = `The following fields must not be empty: ${errors.join(', ')}.`;
                else item.error = '';

                return errors.length > 0;
            },
            save: async ()=> {
                if (item.validate()) return;
                const data = item.modal.selected;
                const request = {
                    name: data.name, type: data.itemType, 
                    override_price: 0, is_override_price: false,
                    base_uom: data.baseUnit, alternate_uom: data.altUnit,
                    properties: Object.assign({}, data.properties)
                }
                console.log(request);
                const response = await ItemApi.createItem(request);
                console.log(response);
            },
            delete: ()=>{}
        });
        
        const populateItemTypes = async() => {
            const response = await ItemApi.getItemTypes();
            if (response) {
                const itemTypes = response.map(type=> ({
                    value: type.value, label: type.display_name
                }));
                item.modal.itemTypes = itemTypes;
            }
        };
        const populateStockUnits = async() => {
            const response = await BaseStockUnitApi.listBaseStockUnits();
            if (response) {
                const baseStockUnits = response.map(bu=> ({
                    id: bu.id, name: bu.name, 
                    alternateStockUnits: bu.alternate_stock_units.map(au => ({
                        id: au.id, name: au.name
                    }))
                }));
                item.modal.baseStockUnits = baseStockUnits;
            }
        }
        populateItemTypes();
        populateStockUnits();
        watch(()=> item.modal.selected.baseUnit,()=>{
            item.modal.selected.altUnit = null;
            item.modal.altStockUnits = [{}];
            if (item.modal.baseStockUnits && item.modal.selected.baseUnit) {
                const bUnits = Array.from(item.modal.baseStockUnits)
                    .map(b => Object.assign({}, b));
                const aUnits = bUnits.find(bu=>bu.id==item.modal.selected.baseUnit)
                        .alternateStockUnits
                        .map(au=>({
                            value: au.id, label: au.name,
                            isSelected: item.modal.selected.altUnit == au.id}));
                item.modal.altStockUnits = aUnits;
            } 
        });

        const loadProperties = async(itemType)=> {
            item.error = '';
            const response = await ItemPropertiesApi.getItemProperties(itemType);
            if (response) {
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
                item.modal.itemProperties = (itemProps.length > 0)?
                    itemProps : null;

                item.modal.selected.properties = {};
                responseData.forEach( entry => {
                    const name = entry[0];
                    item.modal.selected.properties[name] = null;
                });
                item.modal.selected.properties['resourcetype'] = itemType;
            }
        };
        watch(()=> item.modal.selected.itemType, ()=> {
            const itemType = item.modal.selected.itemType;
            if (itemType) {
                loadProperties(itemType);
            }
        });


        return {
            item
        }
    }
}
</script>