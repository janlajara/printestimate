<template>
    <Page title="Inventory : Stock">
        <Section>
            <Button color="secondary" :action="()=>item.toggle(true)">
                Create Item</Button>
        </Section>
        <Modal heading="Item" :is-open="item.modal.IsOpen" @toggle="item.toggle">
            <Section :heading="`${(item.modal.isCreate)? 'Create' : 'Edit'}`">
                <span v-if="item.error" class="text-sm text-red-600">*{{item.error}}</span>
                <div class="md:grid md:grid-cols-4 md:gap-4">
                    <InputText type="text" name="Name" class="md:col-span-2"
                        :value="item.modal.selected.name"/>
                    <InputText type="number" name="Price" postfix="PHP" 
                        :value="item.modal.selected.price"/>
                    <InputSelect name="Type" :options="item.modal.itemTypes"/>
                    <InputSelect name="Base Unit" 
                        @input="(value)=>{
                            item.modal.selected.baseUnit = value;
                            item.modal.selected.altUnit = null;
                            item.modal.altStockUnits = [{}];
                        }"
                        :options="item.modal.baseStockUnits.map(bu=>({
                            value: bu.id, label: bu.name,
                            isSelected: item.modal.selected.baseUnit == bu.id
                        }))"/>
                    <InputSelect name="Alternate Unit" 
                        @input="(value)=>item.modal.selected.altUnit = value"
                        :options="item.modal.altStockUnits"/>
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
import {ItemApi, BaseStockUnitApi} from '@/utils/apis.js';

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
                        name:'', price: 0.00, baseUnit: null, altUnit: null
                    }
                }
                item.modal.IsOpen = value;
            },
            validate: ()=>{},
            save: ()=>{},
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
            if (item.modal.baseStockUnits && item.modal.selected.baseUnit) {
                const bUnits = Array.from(item.modal.baseStockUnits)
                    .map(b => Object.assign({}, b));
                const aUnits = bUnits.find(bu=>bu.id==item.modal.selected.baseUnit)
                        .alternateStockUnits
                        .map(au=>({
                            value: au.id, label: au.name,
                            isSelected: item.modal.selected.altUnit == au.id}));
                item.modal.altStockUnits = aUnits;
            } else {
                item.modal.altStockUnits = [{}];
            }
        });


        return {
            item
        }
    }
}
</script>