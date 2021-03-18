<template>
    <Page :title="(item.detail.isOpen)? item.detail.selectedItem : 'Inventory : Stock'">
        <hr class="my-4"/>
        <Modal :heading="`${(item.modal.isCreate)? 'Create' : 'Edit'} Item`"
            :is-open="item.modal.IsOpen" @toggle="item.modal.toggle"
            :buttons="[{color: 'primary', icon:'save', text:'Save',
                        action:()=>item.modal.save(), disabled: item.modal.isProcessing},]">
            <Section heading="General Information">
                <span v-if="item.modal.error" class="text-sm text-red-600">*{{item.modal.error}}</span>
                <div class="md:grid md:grid-cols-4 md:gap-4">
                    <InputText type="text" name="Name" required
                        @input="(value)=>item.modal.form.name = value"
                        :value="item.modal.form.name"/>
                    <InputSelect name="Type" required
                        :disabled="!item.modal.isCreate"
                        @input="(value)=>item.modal.form.type = value"
                        :options="item.modal.itemTypes.map(it=>({
                            value: it.value, label: it.label,
                            isSelected: item.modal.form.type == it.value
                        }))"/>
                    <InputSelect name="Base Unit" required
                        @input="(value)=>item.modal.form.baseUnit = value"
                        :options="item.modal.baseStockUnits.map(bu=>({
                            value: bu.id, label: bu.name,
                            isSelected: item.modal.form.baseUnit == bu.id
                        }))"/>
                    <InputSelect name="Alternate Unit" 
                        @input="(value)=>item.modal.form.altUnit = value"
                        :options="item.modal.altStockUnits"/>
                </div>    
            </Section>
            <Section heading="Properties" v-if="item.modal.itemProperties">
                <div class="md:grid md:grid-cols-4 md:gap-4">
                    <component v-for="(itemProp, key) in item.modal.itemProperties" :key="key"
                        :is="itemProp.inputComponent" :required="itemProp.required"
                        :name="itemProp.label" :type="itemProp.inputType"
                        @input="(value)=>item.modal.form.properties[itemProp.name] = value"
                        :value="item.modal.form.properties[itemProp.name]"
                        :options="(itemProp.options)?
                            itemProp.options.map(option => ({
                                ...option,
                                isSelected: option.value == item.modal.form.properties[itemProp.name]
                            })) : null"/>
                </div>
            </Section>
        </Modal>
        <Section>
            <div v-if="item.detail.isOpen">
                <div class="flex">
                    <Button color="secondary" icon="arrow_back"
                        :action="item.detail.close">Go Back</Button>
                    <Button icon="mode_edit" class="mx-4" :action="item.detail.edit"/>
                    <Button icon="delete" :action="item.detail.delete"/>
                </div>  
                <StockDetail :item-id="item.detail.id" :key="item.detail.key"
                    @load-data="(data)=> {item.detail.data = data}"/>
            </div>
            <div v-else>
                <Button color="secondary" :action="()=>item.modal.toggle(true)">
                    Create Item</Button>
                <Table :headers="['Item', 'Type', 'Unit of Measure', 
                    'Available Qty', 'On-hand Qty']">
                    <Row v-for="(i, key) in item.list" :key="key"
                        :select="()=>item.detail.open(i.id)">
                        <Cell label="Item">{{i.name}}</Cell>
                        <Cell label="Type" class="capitalize">{{i.type}}</Cell>
                        <Cell label="UoM">{{i.baseUom}}</Cell>
                        <Cell label="Available Qty">{{i.available}}</Cell>
                        <Cell label="Onhand Qty">{{i.onhand}}</Cell>
                    </Row>
                </Table>
            </div>
        </Section>
    </Page>
</template>

<script>
import Page from '@/components/Page.vue';
import Section from '@/components/Section.vue';
import Button from '@/components/Button.vue' ;
import Modal from '@/components/Modal.vue';
import InputText from '@/components/InputText.vue';
import InputSelect from '@/components/InputSelect.vue';
import Table from '@/components/Table.vue';
import Row from '@/components/Row.vue';
import Cell from '@/components/Cell.vue';
import StockDetail from '@/views/pages/inventory/stock/StockDetail.vue';

import {reactive, computed, watch} from 'vue';
import {ItemApi, ItemPropertiesApi, BaseStockUnitApi} from '@/utils/apis.js';

export default {
    name: 'Stock',
    components: {
        Page, Section, Button, Modal, InputText, InputSelect, 
        Table, Row, Cell, StockDetail
    },
    setup() {
        const item = reactive({
            modal: {
                isOpen: false, 
                isCreate: computed(()=> !item.detail.isOpen),
                isProcessing: false,
                form: {
                    properties: {},
                },
                itemTypes: [{}],
                itemProperties: null,
                baseStockUnits: [{}],
                altStockUnits: [{}],
                error: '',
                toggle: (value, data)=>{ 
                    item.modal.error = ''; 
                    if (data != null && item.detail.isOpen){
                        item.modal.form = {
                            id: data.id, name: data.name,
                            type: data.type, baseUnit: data.baseUom.value,
                            altUnit: data.altUom.value, 
                            properties: Object.assign({},data.properties)
                        }; 
                    } else {
                        item.modal.form = {
                            name:'', type: null,
                            baseUnit: null, altUnit: null,
                            properties: {},
                        }
                        item.modal.itemProperties = null; 
                    }
                    item.modal.IsOpen = value;
                },
                validate: ()=>{
                    let errors = [];
                    if (item.modal.form.name.length == 0) errors.push('name');
                    if (item.modal.form.type == null) errors.push('item type');
                    if (item.modal.form.baseUnit == null) errors.push('base unit');

                    Object.entries(item.modal.form.properties).forEach(entry => {
                        const key = entry[0]; 
                        const val = entry[1];
                        const ref = item.modal.itemProperties.find(prop => prop.name==key);
                        if (ref && ref.required && 
                            (val == null || (isNaN(val) && val.trim() == ''))) 
                            errors.push(key.replaceAll('_', ' '));
                    });

                    if (errors.length > 0)
                        item.modal.error = `The following fields must not be empty: ${errors.join(', ')}.`;
                    else item.modal.error = '';

                    return errors.length > 0;
                },
                save: async ()=> {
                    if (item.modal.validate()) return;
                    const data = item.modal.form;
                    const request = {
                        name: data.name, type: data.type, 
                        override_price: 0, is_override_price: false,
                        base_uom: data.baseUnit, alternate_uom: data.altUnit,
                        properties: Object.assign({}, data.properties)
                    }
                    item.modal.isProcessing = true;
                    let response;
                    
                    if (item.modal.isCreate) response = await ItemApi.createItem(request);
                    else {
                        response = await ItemApi.updateItem(item.modal.form.id, request); 
                        item.detail.reload();
                    }
                    populateItemList();
                    if (!response.error) { 
                        item.modal.IsOpen = false;
                    } else {
                        item.modal.error = response.error;
                    }
                    item.modal.isProcessing = false;
                },
            },
            detail: {
                id: null,
                key: 0,
                isOpen: false,
                selectedItem: computed(()=>item.detail.data.fullname),
                data: {},
                open: async (id)=> {
                    item.detail.isOpen = true;
                    item.detail.id = id;
                },
                close: ()=> {
                    item.detail.isOpen = false;
                    item.detail.id = null;
                    item.detail.data = {}; 
                },
                reload: ()=> {
                    // Force reload hack
                    item.detail.key = new Date().getTime();
                },
                edit: ()=> {   
                    if (item.detail.id)
                        item.modal.toggle(true, item.detail.data);
                },
                delete: async ()=>{
                    if (item.detail.id) {
                        const itemId = item.detail.id;
                        if (itemId) {
                            await ItemApi.deleteItem(itemId);
                            populateItemList();
                            item.detail.close();
                        }
                    }
                }
            },
            list: [{}]
        });
        

        // Pre-load the data for item types, stock units, items
        const populateItemTypes = async() => {
            const response = await ItemApi.getItemTypes();
            if (response && !response.error) {
                const itemTypes = response.map(type=> ({
                    value: type.value, label: type.display_name
                }));
                item.modal.itemTypes = itemTypes;
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
                item.modal.baseStockUnits = baseStockUnits;
            }
        }
        const populateItemList = async() => {
            const response = await ItemApi.listItems();
            item.list = response.map(i=> ({
                id: i.id, name: i.full_name, type: i.type,
                baseUom: i.base_uom, 
                available: i.available_quantity,
                onhand: i.onhand_quantity 
            }))
        }
        populateItemTypes();
        populateStockUnits();
        populateItemList();

        // Make AlternateStockUnit select options  dependent on selected 
        // BaseStockUnit option.
        watch(()=> item.modal.form.baseUnit,()=>{
            item.modal.form.altUnit = null;
            item.modal.altStockUnits = [{}];
            if (item.modal.baseStockUnits && item.modal.form.baseUnit) {
                const bUnits = Array.from(item.modal.baseStockUnits)
                    .map(b => Object.assign({}, b));
                const aUnits = bUnits.find(bu=>bu.id==item.modal.form.baseUnit)
                        .alternateStockUnits
                        .map(au=>({
                            value: au.id, label: au.name,
                            isSelected: item.modal.form.altUnit == au.id}));
                item.modal.altStockUnits = aUnits;
            } 
        });

        // Fetch the property fields for the selected item type and 
        // load the data into the form
        const loadProperties = async(itemType)=> {
            item.modal.error = '';
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
                item.modal.itemProperties = (itemProps.length > 0)?
                    itemProps : null;

                if (item.modal.isCreate) {
                    item.modal.form.properties = {};
                    responseData.forEach( entry => {
                        const name = entry[0];
                        item.modal.form.properties[name] = null;
                    });
                    item.modal.form.properties['resourcetype'] = itemType;
                }
            }
        };
        watch(()=> item.modal.form.type, ()=> {
            const itemType = item.modal.form.type;
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