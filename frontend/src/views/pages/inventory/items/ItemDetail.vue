<template>
    <Page :title="'Item : ' + detail.data.fullname">
        <hr class="my-4"/>
        <ItemInputModal 
            :is-open="detail.modal.isOpen" :is-create="false" 
            :on-after-save="()=>loadItem(detail.id)" :data="detail.data"
            @toggle="(value)=> detail.modal.isOpen = value"/>
        <DeleteRecordDialog 
            :heading="`Delete Item`"
            :is-open="detail.deleteDialog.isOpen"
            :execute="detail.delete"
            :on-after-execute="()=>$router.go(-1)"
            @toggle="detail.deleteDialog.toggle">
            <div>
                Are you sure you want to delete 
                <span class="font-bold">{{detail.data.fullname}}</span>?
            </div>
        </DeleteRecordDialog>
        <div class="flex gap-4">
            <Button color="secondary" icon="arrow_back"
                :action="()=>$router.go(-1)">Go Back</Button>
            <Button icon="mode_edit" :action="detail.edit"/>
            <Button icon="delete" :action="detail.deleteDialog.open"/>
        </div> 
        <Section>
            <DescriptionList class="grid-cols-2 md:grid-cols-4">
                <DescriptionItem :loader="detail.isProcessing"
                    name="Item" :value="detail.data.name"/>
                <DescriptionItem :loader="detail.isProcessing"
                    name="Type" :value="detail.data.type" class="capitalize"/>
                <DescriptionItem :loader="detail.isProcessing" 
                    name="Base Stock Unit" 
                    :value="detail.data.baseUom ? detail.data.baseUom.name : null"/>
                <DescriptionItem :loader="detail.isProcessing"
                    name="Alternate Stock Unit" 
                    :value="detail.data.altUom ? detail.data.altUom.name : null"/>
                <DescriptionItem :loader="detail.isProcessing"
                    :name="`Price per ${detail.data.baseUom ? 
                        detail.data.baseUom.name : 'base unit'}`" 
                    :value="detail.data.overridePrice ? 
                        formatMoney(detail.data.overridePrice) : null"/>
            </DescriptionList>
        </Section>
        <Section heading="Properties" 
            v-if="detail.data.properties && detail.data.properties.resourcetype != 'other'">
            <DescriptionList class="grid-cols-2 md:grid-cols-4">
                <DescriptionItem :loader="detail.isProcessing"
                    v-for="(entry, key) in Object.entries(detail.data.properties)
                        .filter(entry => entry[0] != 'resourcetype')" 
                    :key="key" :name="detail.propertyLabels[entry[0]]" :value="entry[1]"/>
            </DescriptionList>
        </Section>
        <!--
            <StockManagement
                :data="{
                    itemId: detail.id,
                    units: {
                        base: detail.data.baseUom,
                        alternate: detail.data.altUom
                    }
                }"/>
        -->
    </Page>
</template>

<script>
import Page from '@/components/Page.vue';
import Section from '@/components/Section.vue';
import DescriptionList from '@/components/DescriptionList.vue';
import DescriptionItem from '@/components/DescriptionItem.vue';
import Button from '@/components/Button.vue';
import DeleteRecordDialog from '@/components/DeleteRecordDialog.vue';
import ItemInputModal from '@/views/pages/inventory/items/ItemInputModal.vue';
//import StockManagement from '@/views/pages/inventory/items/StockManagement.vue';

import {useRoute} from 'vue-router';
import {reactive, onBeforeMount, inject} from 'vue';
import {ItemApi, ItemPropertiesApi} from '@/utils/apis.js';
import {formatMoney as formatCurrency} from '@/utils/format.js'

export default {
    components: {
        Page, Section, DescriptionList, DescriptionItem, Button,
        DeleteRecordDialog, ItemInputModal, //StockManagement
    },
    setup() {
        const currency = inject('currency').abbreviation;
        const route = useRoute()
        const detail = reactive({
            id: route.params.id,
            modal: {
                isOpen: false
            },
            data: {
                id: null,
                name: null, fullname: '',
                type: null, baseUom: {}, 
                altUom: {}, overridePrice: 0, 
                properties: {}
            },
            deleteDialog: {
                isOpen: false,
                toggle: value => detail.deleteDialog.isOpen = value,
                open: ()=> detail.deleteDialog.toggle(true)
            },
            propertyLabels: {},
            isProcessing: false,
            edit: ()=> {   
                detail.modal.isOpen = true;
            }, 
            delete: async ()=>{
                const itemId = detail.id
                if (itemId) await ItemApi.deleteItem(itemId);
            }
        });
        const loadItem = async (id) => { 
            detail.isProcessing = true; 
            const response = await ItemApi.retrieveItem(id); 
            if (response) { 
                const data = {
                    id: id,
                    name: response.name,
                    fullname: response.full_name,
                    type: response.type,
                    baseUom: response.base_uom,
                    altUom: response.alternate_uom,
                    overridePrice: response.override_price,
                    properties: {},
                };
                if (response.properties) {
                    Object.entries(response.properties)
                        .filter(entry => entry[0] != 'properties_id')
                        .forEach(entry => data.properties[entry[0]] = entry[1]);
                    
                    loadPropLabels(response.properties.resourcetype); 
                }
                detail.data = data; 
            }
            detail.isProcessing = false;
        };
        const loadPropLabels = async (resourcetype) => {
            if (resourcetype) {
                const response = await ItemPropertiesApi.getItemProperties(resourcetype);
                if (response == null) return;

                Object.entries(response)
                    .filter(entry => entry[0] != 'id')
                    .forEach(entry => detail.propertyLabels[entry[0]] = entry[1].label);
            }
        }
        onBeforeMount(()=> {
            const id = route.params.id;
            if (id != null && !isNaN(id)) {
                detail.id = parseInt(id);
                loadItem(detail.id);
            }
        });
        const formatMoney = (amount)=> {
            if (amount != null)
                return formatCurrency(amount, currency)
            else return ''
        }
        return {
            detail, loadItem, formatMoney
        }
    }
}
</script>