<template>
    <div>
        <Section>
            <DescriptionList class="md:grid-cols-4">
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
    </div>
</template>

<script>
import Section from '@/components/Section.vue';
import DescriptionList from '@/components/DescriptionList.vue';
import DescriptionItem from '@/components/DescriptionItem.vue';

import {reactive, onBeforeMount} from 'vue';
import {ItemApi, ItemPropertiesApi} from '@/utils/apis.js';

export default {
    components: {
        Section, DescriptionList, DescriptionItem
    },
    props: {
        itemId: Number,
    },
    emits: ['load-data'],
    setup(props, {emit}) {
        const detail = reactive({
            data: {
                id: null,
                name: null, fullname: null,
                type: null, baseUom: {}, 
                altUom: {}, properties: {}
            },
            propertyLabels: {}
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
                    properties: {}
                };
                if (response.properties) {
                    Object.entries(response.properties)
                        .filter(entry => entry[0] != 'id')
                        .forEach(entry => data.properties[entry[0]] = entry[1]);
                    
                    loadPropLabels(response.properties.resourcetype); 
                }
                detail.data = data; 
                emit('load-data', data);
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
            detail
        }
    }
}
</script>