<template>
    <Page :title="detail.data.fullname">
        <hr class="my-4"/>
        <ItemInputModal :is-open="detail.modal.isOpen" :is-create="false" 
            :on-after-save="()=>loadItem(detail.id)" :data="detail.data"
            @toggle="(value)=> detail.modal.isOpen = value"/>
        <div class="flex">
            <Button color="secondary" icon="arrow_back"
                :action="()=>$router.go(-1)">Go Back</Button>
            <Button icon="mode_edit" class="mx-4" :action="detail.edit"/>
            <Button icon="delete" :action="()=>detail.delete(detail.id)"/>
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
                    v-for="(entry, key) in Object.entries(detail.data.properties)
                        .filter(entry => entry[0] != 'resourcetype')" 
                    :key="key" :name="detail.propertyLabels[entry[0]]" :value="entry[1]"/>
            </DescriptionList>
        </Section>
        <StockManagement
            :data="{
                itemId: detail.id,
                units: {
                    base: detail.data.baseUom,
                    alternate: detail.data.altUom
                }
            }"/>
    </Page>
</template>

<script>
import Page from '@/components/Page.vue';
import Section from '@/components/Section.vue';
import DescriptionList from '@/components/DescriptionList.vue';
import DescriptionItem from '@/components/DescriptionItem.vue';
import Button from '@/components/Button.vue';
import ItemInputModal from '@/views/pages/inventory/stock/ItemInputModal.vue';
import StockManagement from '@/views/pages/inventory/stock/StockManagement.vue';

import {useRoute} from 'vue-router';
import {watch, reactive, onBeforeMount} from 'vue';
import {ItemApi, ItemPropertiesApi} from '@/utils/apis.js';

export default {
    components: {
        Page, Section, DescriptionList, DescriptionItem, Button, 
        ItemInputModal, StockManagement
    },
    emits: ['toggle'],
    setup(props, {emit}) {
        const route = useRoute()
        const detail = reactive({
            id: route.params.id,
            modal: {
                isOpen: false
            },
            data: {
                id: null,
                name: null, fullname: null,
                type: null, baseUom: {}, 
                altUom: {}, properties: {}
            },
            propertyLabels: {},
            isProcessing: false,
            edit: ()=> {   
                detail.modal.isOpen = true;
            }, 
            delete: async (itemId)=>{
                if (itemId) {
                    await ItemApi.deleteItem(itemId);
                    if (props.onAfterDelete) props.onAfterDelete();
                    emit('toggle', false);
                }
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
                    properties: {},
                };
                if (response.properties) {
                    Object.entries(response.properties)
                        .filter(entry => entry[0] != 'id')
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
            loadItem(detail.id);
        })
        watch(()=> route.params.id, ()=> {
            const id = route.params.id;
            if (id != null && !isNaN(id))
                detail.id = parseInt(id);
        })
        return {
            detail, loadItem
        }
    }
}
</script>