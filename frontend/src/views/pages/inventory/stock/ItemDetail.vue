<template>
    <div v-if="$props.isOpen">
        <ItemInputModal :is-open="detail.modal.isOpen" :is-create="false" 
            :on-after-save="()=>loadItem($props.itemId)" :data="detail.data"
            @toggle="(value)=> detail.modal.isOpen = value"/>
        <div class="flex">
            <Button color="secondary" icon="arrow_back"
                :action="()=>$emit('toggle', false)">Go Back</Button>
            <Button icon="mode_edit" class="mx-4" :action="detail.edit"/>
            <Button icon="delete" :action="()=>detail.delete($props.itemId)"/>
        </div> 
        <Section>
            <DescriptionList class="grid-cols-2 md:grid-cols-4">
                <DescriptionItem name="Item" :value="detail.data.name"/>
                <DescriptionItem name="Type" :value="detail.data.type" class="capitalize"/>
                <DescriptionItem name="Base Stock Unit" :value="detail.data.baseUom.label"/>
                <DescriptionItem name="Alternate Stock Unit" :value="detail.data.altUom.label"/>
                <DescriptionItem 
                    v-for="(entry, key) in Object.entries(detail.data.properties)
                        .filter(entry => entry[0] != 'resourcetype')" 
                    :key="key" :name="detail.propertyLabels[entry[0]]" :value="entry[1]"/>
            </DescriptionList>
        </Section>
        <Section heading="Stock Management" class="mt-12">{{detail.onhandQuantity}}
            <div class="flex">
                <Button icon="upload" color="secondary" class="mr-4">Withdraw</Button>
                <Button icon="download" color="secondary" class="mr-4">Deposit</Button>
            </div>
            <DescriptionList class="grid-cols-2 md:grid-cols-4">
                <DescriptionItem name="Available" :value="detail.data.availableQuantityFormatted"/>
                <DescriptionItem name="On-hand" :value="detail.data.onhandQuantityFormatted"/>
                <DescriptionItem name="Average Price" :value="detail.data.averagePriceFormatted"/>
                <DescriptionItem name="Latest Price" :value="detail.data.latestPriceFormatted"/>
            </DescriptionList>
            <Tabs>
                <Tab title="On-hand">
                </Tab>
                <Tab title="Requests"></Tab>
                <Tab title="Incoming"></Tab>
                <Tab title="History"></Tab>
            </Tabs>
        </Section>
    </div>
</template>

<script>
import Section from '@/components/Section.vue';
import DescriptionList from '@/components/DescriptionList.vue';
import DescriptionItem from '@/components/DescriptionItem.vue';
import Tabs from '@/components/Tabs.vue';
import Tab from '@/components/Tab.vue';
import Button from '@/components/Button.vue';
import ItemInputModal from '@/views/pages/inventory/stock/ItemInputModal.vue';

import {reactive, onBeforeMount} from 'vue';
import {ItemApi, ItemPropertiesApi} from '@/utils/apis.js';

export default {
    components: {
        Section, DescriptionList, DescriptionItem, Tabs, Tab, Button, ItemInputModal
    },
    props: {
        itemId: Number,
        isOpen: {
            type: Boolean,
            required: true
        },
        onAfterDelete: Function
    },
    emits: ['toggle'],
    setup(props, {emit}) {
        const detail = reactive({
            modal: {
                isOpen: false
            },
            data: {
                id: null,
                name: null, fullname: null,
                type: null, baseUom: {}, 
                altUom: {}, properties: {},
                latestPrice: null, latestPriceFormatted: null,
                averagePrice: null, averagePriceFormatted: null,
                onhandQuantityFormatted: null,
                availableQuantityFormatted: null,
            },
            propertyLabels: {},
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
            const response = await ItemApi.retrieveItem(id); 
            if (response) {
                const data = {
                    id: id,
                    name: response.name,
                    fullname: response.full_name,
                    type: response.type,
                    baseUom: {
                        value: response.base_uom.id,
                        label: response.base_uom.name},
                    altUom: {
                        value: (response.alternate_uom)? response.alternate_uom.id: null,
                        label: (response.alternate_uom)? response.alternate_uom.name: null},
                    properties: {},
                    onhandQuantity: response.onhand_quantity,
                    onhandQuantityFormatted: response.onhand_quantity_formatted,
                    availableQuantity: response.available_quantity,
                    availableQuantityFormatted: response.available_quantity_formatted,
                    averagePrice: response.average_price_per_quantity,
                    averagePriceFormatted:
                        (response.average_price_per_quantity)?  
                            `${response.average_price_per_quantity_currency} ${response.average_price_per_quantity}`:
                            null,
                    latestPrice: response.latest_price_per_quantity,
                    latestPriceFormatted: 
                        (response.latest_price_per_quantity)?  
                            `${response.latest_price_per_quantity_currency} ${response.latest_price_per_quantity}`:
                            null,
                };
                if (response.properties) {
                    Object.entries(response.properties)
                        .filter(entry => entry[0] != 'id')
                        .forEach(entry => data.properties[entry[0]] = entry[1]);
                    
                    loadPropLabels(response.properties.resourcetype); 
                }
                detail.data = data; 
            }
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
            if (props.itemId != null) loadItem(props.itemId);
        })
        return {
            detail, loadItem
        }
    }
}
</script>